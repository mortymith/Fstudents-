# app/routes/auth_routes.py
"""
Authentication API routes.
"""
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth_deps import get_current_user, require_auth
from app.dependencies.database import get_db_session
from app.dependencies.cache import get_redis_client
from app.repositories import UserRepository
from app.repositories import UserSessionRepository
from app.repositories import PasswordResetTokenRepository
from app.schemas import (
    LoginRequest,
    LoginResponse,
    UserResponse,
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordChange,
    ErrorResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


# Dependency factory for auth service
async def get_auth_service(
    db: AsyncSession = Depends(get_db_session),
    redis_client=Depends(get_redis_client),
) -> AuthService:
    """Get authentication service instance."""
    user_repo = UserRepository()
    session_repo = UserSessionRepository(redis_client)
    reset_repo = PasswordResetTokenRepository(redis_client)

    return AuthService(user_repo, session_repo, reset_repo)


@router.post(
    "/login",
    response_model=LoginResponse,
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Invalid credentials",
            "content": {
                "application/json": {
                    "example": {
                        "error": "INVALID_CREDENTIALS",
                        "message": "Invalid email or password",
                        "trace_id": "req_123456789",
                    }
                }
            },
        },
        400: {"model": ErrorResponse, "description": "Validation error"},
    },
    summary="Authenticate user and obtain access token",
    description="Authenticate user credentials and return JWT token for API access (UC-01)",
)
async def login(
    request: Request,
    login_data: LoginRequest,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Authenticate user and create session.

    Returns:
        - Access token (JWT) for API calls
        - Session token (HTTP-only cookie) for web interface
        - User information
    """
    # Get client information
    ip_address = request.client.host if request.client else "0.0.0.0"
    user_agent = request.headers.get("user-agent", "")

    # Authenticate user
    result, error = await auth_service.authenticate_user(
        db, login_data, ip_address, user_agent
    )

    if error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=error)

    # Set session cookie (HTTP-only, secure in production)
    response.set_cookie(
        key="session_token",
        value=result["session_token"],
        httponly=True,
        secure=True,  # Set to False for local development without HTTPS
        samesite="lax",
        max_age=24 * 3600,  # 24 hours
    )

    return LoginResponse(
        user=result["user"],
        access_token=result["access_token"],
        expires_in=result["expires_in"],
        token_type=result["token_type"],
    )


@router.post(
    "/logout",
    responses={
        200: {
            "description": "Successfully logged out",
            "content": {
                "application/json": {"example": {"message": "Successfully logged out"}}
            },
        },
        401: {"model": ErrorResponse, "description": "Authentication required"},
    },
    summary="Logout user and invalidate session",
    description="Invalidate the current user session and access token",
)
async def logout(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
    user_id: int = Depends(require_auth),
):
    """
    Logout user by invalidating current session.

    Clears:
        - Session cookie
        - All user sessions (optional)
    """
    # Get session token from cookie
    session_token = request.cookies.get("session_token")
    
    # Invalidate session
    success = await auth_service.logout_user(
        session_token=session_token, user_id=user_id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to logout"
        )

    # Clear session cookie
    response.delete_cookie(key="session_token")

    return {"message": "Successfully logged out"}


@router.post(
    "/password-reset",
    responses={
        200: {
            "description": "Password reset instructions sent",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Password reset instructions sent to your email"
                    }
                }
            },
        },
        400: {"model": ErrorResponse, "description": "Validation error"},
    },
    summary="Request password reset",
    description="Send password reset instructions to user's email",
)
async def request_password_reset(
    reset_data: PasswordResetRequest,
    auth_service: AuthService = Depends(get_auth_service),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Request password reset for a user.

    Security notes:
        - Always returns success even if email doesn't exist
        - Prevents email enumeration attacks
        - Rate limiting should be implemented at the gateway level
    """
    success, error = await auth_service.request_password_reset(db, reset_data)

    if error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error
        )

    return {"message": "Password reset instructions sent to your email"}


@router.post(
    "/password-reset/confirm",
    responses={
        200: {
            "description": "Password successfully reset",
            "content": {
                "application/json": {
                    "example": {"message": "Password successfully reset"}
                }
            },
        },
        400: {"model": ErrorResponse, "description": "Validation error"},
        410: {
            "description": "Reset token expired or invalid",
            "content": {
                "application/json": {
                    "example": {
                        "error": "INVALID_RESET_TOKEN",
                        "message": "Reset token is invalid or has expired",
                        "trace_id": "req_123456789",
                    }
                }
            },
        },
    },
    summary="Confirm password reset",
    description="Reset user password using valid reset token",
)
async def confirm_password_reset(
    confirm_data: PasswordResetConfirm,
    auth_service: AuthService = Depends(get_auth_service),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Confirm password reset with valid token.

    Requirements:
        - Token must be valid and not expired
        - Token must not have been used before
        - New password must meet security requirements
    """
    success, error = await auth_service.confirm_password_reset(db, confirm_data)

    if not success:
        if error in ["Invalid token", "Token expired", "Token already used"]:
            raise HTTPException(status_code=status.HTTP_410_GONE, detail=error)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return {"message": "Password successfully reset"}


@router.get(
    "/me",
    response_model=UserResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        404: {"model": ErrorResponse, "description": "User not found"},
    },
    summary="Get current user profile",
    description="Get profile information for the authenticated user",
)
async def get_current_user_profile(
    user: UserResponse = Depends(get_current_user),
):
    """
    Get current authenticated user's profile.

    Returns full user information including:
        - Basic details (email, name, role)
        - Account status
        - Timestamps
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


# =============== SESSION MANAGEMENT ENDPOINTS ===============


@router.get(
    "/sessions",
    responses={
        200: {
            "description": "User sessions retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "data": [
                            {
                                "id": 1,
                                "user_id": 1,
                                "login_at": "2023-01-15T09:45:00Z",
                                "logout_at": "2023-01-15T17:30:00Z",
                                "ip_address": "192.168.1.100",
                                "user_agent": "Mozilla/5.0",
                                "is_active": True,
                            }
                        ],
                        "pagination": {
                            "total": 1,
                            "limit": 20,
                            "offset": 0,
                            "has_more": False,
                        },
                    }
                }
            },
        },
        401: {"model": ErrorResponse, "description": "Authentication required"},
    },
    summary="Get current user's active sessions",
    description="Retrieve active sessions for the authenticated user",
)
async def get_my_sessions(
    request: Request,
    redis_client=Depends(get_redis_client),
    user_id: int = Depends(require_auth),
):
    """
    Get all active sessions for the current user.

    Includes:
        - Current session information
        - IP addresses and user agents
        - Login timestamps
        - Activity status
    """
    session_repo = UserSessionRepository(redis_client)
    sessions = await session_repo.find_by_user(user_id, active_only=True)

    # Format response according to UserSession schema
    formatted_sessions = []
    for session in sessions:
        formatted_sessions.append(
            {
                "id": session["id"],
                "user_id": session["user_id"],
                "login_at": session["created_at"],
                "logout_at": None,  # Redis doesn't track logout
                "ip_address": session["ip_address"],
                "user_agent": session["user_agent"],
                "is_active": datetime.fromisoformat(session["expires_at"])
                > datetime.utcnow(),
            }
        )

    return {
        "data": formatted_sessions,
        "pagination": {
            "total": len(formatted_sessions),
            "limit": len(formatted_sessions),
            "offset": 0,
            "has_more": False,
        },
    }


@router.delete(
    "/sessions/{session_id}",
    responses={
        204: {"description": "Session successfully revoked"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        404: {"model": ErrorResponse, "description": "Session not found"},
        403: {
            "model": ErrorResponse,
            "description": "Cannot revoke other users' sessions",
        },
    },
    summary="Revoke a specific session",
    description="Revoke/delete a specific session by ID",
)
async def revoke_session(
    session_id: int,
    request: Request,
    redis_client=Depends(get_redis_client),
    user_id: int = Depends(require_auth),
):
    """
    Revoke a specific session.

    Security:
        - Users can only revoke their own sessions
        - Admins can revoke any session
        - Current session cannot be revoked (use logout instead)
    """
    session_repo = UserSessionRepository(redis_client)

    # Get session data
    session_data = await session_repo.get_by_id(session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    # Check permission
    current_session_token = request.cookies.get("session_token")
    if session_data["user_id"] != user_id and request.state.user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot revoke other users' sessions",
        )

    # Prevent revoking current session (use logout instead)
    if current_session_token and session_data["session_token"] == current_session_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot revoke current session. Use /logout instead.",
        )

    # Delete session
    success = await session_repo.delete(session_data["session_token"])
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke session",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/sessions/revoke-all",
    responses={
        200: {
            "description": "All other sessions revoked",
            "content": {
                "application/json": {
                    "example": {
                        "message": "3 other sessions revoked",
                        "revoked_count": 3,
                    }
                }
            },
        },
        401: {"model": ErrorResponse, "description": "Authentication required"},
    },
    summary="Revoke all other sessions",
    description="Revoke all other sessions except the current one",
)
async def revoke_all_other_sessions(
    request: Request,
    redis_client=Depends(get_redis_client),
    user_id: int = Depends(require_auth),
):
    """
    Revoke all other sessions except the current one.

    Useful for:
        - Security breach response
        - Device management
        - Password change enforcement
    """
    session_repo = UserSessionRepository(redis_client)
    current_session_token = request.cookies.get("session_token")

    # Revoke all sessions except current
    revoked_count = await session_repo.revoke_user_sessions(
        user_id, keep_current=current_session_token
    )

    return {
        "message": f"{revoked_count} other sessions revoked",
        "revoked_count": revoked_count,
    }
