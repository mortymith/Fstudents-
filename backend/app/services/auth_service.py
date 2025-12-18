# app/services/auth_service.py
"""
Authentication service for user management and session handling.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
from jose import jwt

from app.core.config import settings
from app.repositories.user_repository import UserRepository
from app.repositories.user_session_repository import UserSessionRepository
from app.repositories.reset_password_repository import PasswordResetTokenRepository
from app.schemas import (
    LoginRequest, 
    UserCreate, 
    UserResponse,
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordChange
)


class AuthService:
    """Service for authentication and user management operations."""
    
    def __init__(
        self,
        user_repo: UserRepository,
        session_repo: UserSessionRepository,
        reset_repo: PasswordResetTokenRepository,
    ):
        self.user_repo = user_repo
        self.session_repo = session_repo
        self.reset_repo = reset_repo
        self.ph = PasswordHasher()
    
    # =============== AUTHENTICATION METHODS ===============
    
    async def authenticate_user(
        self, 
        db: AsyncSession, 
        login_data: LoginRequest,
        ip_address: str,
        user_agent: str,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Authenticate user with email and password.
        Returns (user_data, session_token) or (None, error_message)
        """
        # Get user by email
        user = await self.user_repo.get_by_email(db, login_data.email)
        if not user:
            return None, "Invalid email or password"
        
        if not user.is_active:
            return None, "Account is deactivated"
        
        # Verify password
        if not self._verify_password(plain_password=login_data.password, hashed_password=user.password_hash):
            return None, "Invalid email or password"
        
        # Update last login
        user.last_login_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(user)
        
        # Create session
        session_data = await self.session_repo.create(
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            ttl_hours=settings.SESSION_TTL_HOURS
        )
        
        if not session_data:
            return None, "Failed to create session"
        
        # Generate JWT token
        access_token = self._create_access_token(user.id, user.role)
        
        user_response = UserResponse.from_orm(user)
        return {
            "user": user_response.dict(),
            "access_token": access_token,
            "session_token": session_data["session_token"],
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "token_type": "Bearer"
        }, None
    
    async def logout_user(
        self, 
        session_token: Optional[str] = None,
        access_token: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> bool:
        """
        Logout user by invalidating session and/or all sessions.
        """
        success = True
        
        # Invalidate specific session
        if session_token:
            if not await self.session_repo.delete(session_token):
                success = False
        
        # Invalidate all user sessions
        elif user_id:
            revoked = await self.session_repo.revoke_user_sessions(user_id)
            if revoked == 0:
                success = False
        
        return success
    
    # =============== USER MANAGEMENT METHODS ===============
    
    async def create_user(
        self, 
        db: AsyncSession, 
        user_data: UserCreate,
        created_by: Optional[int] = None,
    ) -> Tuple[Optional[UserResponse], Optional[str]]:
        """
        Create a new user account.
        """
        # Check if email already exists
        existing = await self.user_repo.get_by_email(db, user_data.email)
        if existing:
            return None, "Email already registered"
        
        # Hash password
        password_hash = self._hash_password(user_data.password)
        
        # Create user
        try:
            user = await self.user_repo.create(
                db,
                email=user_data.email,
                password_hash=password_hash,
                full_name=user_data.full_name,
                role=user_data.role,
                is_active=True,
                created_by=created_by
            )
            
            return UserResponse.from_orm(user), None
            
        except Exception as e:
            return None, f"Failed to create user: {str(e)}"
    
    async def update_user(
        self,
        db: AsyncSession,
        user_id: int,
        update_data: Dict[str, Any],
        updated_by: Optional[int] = None,
    ) -> Tuple[Optional[UserResponse], Optional[str]]:
        """
        Update user information.
        """
        user = await self.user_repo.get(db, user_id)
        if not user:
            return None, "User not found"
        
        # Prevent role escalation (only admins can change roles)
        if "role" in update_data and updated_by:
            updater = await self.user_repo.get(db, updated_by)
            if not updater or updater.role != "admin":
                return None, "Only admins can change user roles"
        
        # Update user
        updated_user = await self.user_repo.update(db, user_id, **update_data)
        if not updated_user:
            return None, "Failed to update user"
        
        return UserResponse.from_orm(updated_user), None
    
    # =============== PASSWORD MANAGEMENT METHODS ===============
    
    async def change_password(
        self,
        db: AsyncSession,
        user_id: int,
        password_data: PasswordChange,
    ) -> Tuple[bool, Optional[str]]:
        """
        Change user password with current password verification.
        """
        user = await self.user_repo.get(db, user_id)
        if not user:
            return False, "User not found"
        
        # Verify current password
        if not self._verify_password(password_data.current_password, user.password_hash):
            return False, "Current password is incorrect"
        
        # Update password
        new_password_hash = self._hash_password(password_data.new_password)
        updated = await self.user_repo.update(
            db, user_id, password_hash=new_password_hash
        )
        
        if not updated:
            return False, "Failed to update password"
        
        # Invalidate all existing sessions for security
        await self.session_repo.revoke_user_sessions(user_id)
        
        return True, None
    
    async def request_password_reset(
        self,
        db: AsyncSession,
        reset_data: PasswordResetRequest,
    ) -> Tuple[bool, Optional[str]]:
        """
        Request password reset for a user.
        """
        user = await self.user_repo.get_by_email(db, reset_data.email)
        if not user:
            # Return success even if user doesn't exist (security best practice)
            return True, None
        
        # Create reset token
        token_data = await self.reset_repo.create(
            user_id=user.id,
            expiry_minutes=settings.PASSWORD_RESET_EXPIRY_MINUTES
        )
        
        if not token_data:
            return False, "Failed to create reset token"
        
        # TODO: Send email with reset link
        # For now, log the token (remove in production)
        print(f"Password reset token for {user.email}: {token_data['reset_token']}")
        
        return True, None
    
    async def confirm_password_reset(
        self,
        db: AsyncSession,
        confirm_data: PasswordResetConfirm,
    ) -> Tuple[bool, Optional[str]]:
        """
        Confirm password reset with valid token.
        """
        # Validate token
        is_valid, error = await self.reset_repo.validate_token(confirm_data.token)
        if not is_valid:
            return False, error
        
        # Get token data
        token_data = await self.reset_repo.get(confirm_data.token)
        if not token_data:
            return False, "Invalid token"
        
        # Update user password
        new_password_hash = self._hash_password(confirm_data.new_password)
        updated = await self.user_repo.update(
            db, token_data["user_id"], password_hash=new_password_hash
        )
        
        if not updated:
            return False, "Failed to update password"
        
        # Mark token as used
        await self.reset_repo.use_token(confirm_data.token)
        
        # Invalidate all existing sessions for security
        await self.session_repo.revoke_user_sessions(token_data["user_id"])
        
        return True, None
    
    # =============== HELPER METHODS ===============
    
    def _hash_password(self, password: str) -> str:
        """Hash password using Argon2id."""
        # .hash() returns a string containing the salt, parameters, and the hash
        return self.ph.hash(password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against Argon2 hash."""
        try:
            # .verify() returns True if it matches, or raises VerifyMismatchError
            return self.ph.verify(hashed_password, plain_password)
        except (VerifyMismatchError, ValueError, TypeError):
            # VerifyMismatchError: wrong password
            # ValueError/TypeError: malformed hash string
            return False
    
    def _create_access_token(self, user_id: int, role: str) -> str:
        """Create JWT access token."""
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        now = datetime.now(timezone.utc)
        expire = now + expires_delta
        
        payload = {
            "sub": str(user_id),
            "role": role,
            "exp": expire,
            "iat":  now,
            "type": "access"
        }
        
        return jwt.encode(
            payload, 
            settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
    

    def _create_refresh_token(self, user_id: int) -> str:
        """Create JWT refresh token using python-jose."""
        expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        # Best practice: Use timezone-aware UTC objects
        now = datetime.now(timezone.utc)
        expire = now + expires_delta
        
        payload = {
            "sub": str(user_id),
            "exp": expire,
            "iat": now,
            "type": "refresh"
        }
        
        # jose.jwt.encode handles datetime objects by converting them to Unix timestamps
        return jwt.encode(
            payload, 
            settings.REFRESH_SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
    

