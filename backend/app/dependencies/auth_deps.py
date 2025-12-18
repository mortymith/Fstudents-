# app/dependencies/auth_deps.py
"""
Authentication dependencies for FastAPI.
"""
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import  jwt,JWTError
# from jwt.exceptions import InvalidTokenError
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.dependencies.database import get_db_session
from app.dependencies.cache import get_redis_client
from app.models import User
from app.repositories.user_repository import UserRepository
from app.repositories.user_session_repository import UserSessionRepository
from app.schemas import UserRole

# Security schemes
security = HTTPBearer(auto_error=False)


class AuthDependencies:
    """Container for authentication dependencies."""
    
    def __init__(self):
        self.user_repo = UserRepository()
        self.session_repo = None  # Will be initialized with Redis client
        
    async def get_session_repo(self) -> UserSessionRepository:
        """Get or create session repository instance."""
        if self.session_repo is None:
            redis_client = await get_redis_client()
            self.session_repo = UserSessionRepository(redis_client)
        return self.session_repo


auth_deps = AuthDependencies()


async def get_current_user_id(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    session_repo: UserSessionRepository = Depends(lambda: auth_deps.get_session_repo()),
) -> Optional[int]:
    """
    Extract current user ID from JWT token or session.
    Returns None if no valid authentication.
    """
    # Check for JWT token first (API calls)
    if credentials and credentials.scheme.lower() == "bearer":
        try:
            payload = jwt.decode(
                credentials.credentials,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            user_id = int(payload.get("sub"))
            
            # Validate user exists and is active
            async for db in get_db_session():
                user = await auth_deps.user_repo.get(db, user_id)
                if user and user.is_active:
                    request.state.user_id = user_id
                    request.state.user_role = user.role
                    return user_id
                    
        except (JWTError, ValueError, KeyError) as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
    
    # Check for session token (web interface)
    session_token = request.cookies.get("session_token")
    if session_token:
        user = await session_repo.get(session_token)
        is_valid, error = await session_repo.validate_session(session_token)
        if is_valid:
            session_data = await session_repo.get(session_token)
            if session_data:
                # Update last activity
                await session_repo.update_activity(session_token)
                
                user_id = session_data["user_id"]
                async for db in get_db_session():
                    user = await auth_deps.user_repo.get(db, user_id)
                    if user and user.is_active:
                        request.state.user_id = user_id
                        request.state.user_role = user.role
                        return user_id
    
    return None


async def get_current_user(
    user_id: Optional[int] = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
) -> Optional[User]:
    """
    Get current user object.
    Returns None if no authenticated user.
    """
    if user_id is None:
        return None
    
    user = await auth_deps.user_repo.get(db, user_id)
    if not user or not user.is_active:
        return None
    
    return user


async def require_auth(
    user_id: Optional[int] = Depends(get_current_user_id),
) -> int:
    """
    Require authentication - raise 401 if no user.
    Returns the authenticated user ID.
    """
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return user_id


async def require_role(
    required_roles: list[UserRole],
    user: User = Depends(get_current_user),
) -> User:
    """
    Require specific role(s) for authorization.
    """
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    if user.role not in required_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    return user


# Role-specific dependencies
async def require_admin(user: User = Depends(get_current_user)) -> User:
    """Require admin role."""
    return await require_role([UserRole.ADMIN], user)


async def require_inventory_manager(user: User = Depends(get_current_user)) -> User:
    """Require inventory manager or admin role."""
    return await require_role([UserRole.ADMIN, UserRole.INVENTORY_MANAGER], user)


async def require_viewer(user: User = Depends(get_current_user)) -> User:
    """Require viewer, inventory manager, or admin role."""
    return await require_role(
        [UserRole.ADMIN, UserRole.INVENTORY_MANAGER, UserRole.VIEWER], 
        user
    )