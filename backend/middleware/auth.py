"""
JWT authentication middleware for FastAPI.
Verifies tokens and ensures user_id from token matches path parameter.
"""
from fastapi import Depends, Header
from uuid import UUID
from jose import JWTError
from utils.auth import decode_access_token
from utils.exceptions import AuthenticationError, AuthorizationError


async def get_current_user(authorization: str = Header(None)) -> UUID:
    """
    Extract and verify JWT token from Authorization header.

    Args:
        authorization: Authorization header value (format: "Bearer <token>")

    Returns:
        User ID from verified token

    Raises:
        AuthenticationError: If token is missing, invalid, or expired
    """
    if not authorization:
        raise AuthenticationError("Missing authorization header")

    # Parse "Bearer <token>" format
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthenticationError("Invalid authorization header format")

    token = parts[1]

    try:
        user_id = decode_access_token(token)
        return user_id
    except JWTError as e:
        raise AuthenticationError(f"Invalid or expired token: {str(e)}")


def verify_user_access(path_user_id: UUID, current_user_id: UUID = Depends(get_current_user)) -> UUID:
    """
    Verify that the authenticated user matches the user_id in the path.
    This ensures users can only access their own resources.

    Args:
        path_user_id: User ID from path parameter
        current_user_id: User ID from JWT token

    Returns:
        Verified user ID

    Raises:
        AuthorizationError: If user IDs don't match
    """
    if path_user_id != current_user_id:
        raise AuthorizationError("Cannot access another user's resources")

    return current_user_id
