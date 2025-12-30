"""
Authentication utilities for password hashing and JWT token management.
"""
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from uuid import UUID
from config import get_settings

settings = get_settings()

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plain text password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: UUID) -> str:
    """
    Create a JWT access token for the given user.

    Args:
        user_id: UUID of the authenticated user

    Returns:
        JWT token string
    """
    expire = datetime.utcnow() + timedelta(days=settings.access_token_expire_days)
    to_encode = {
        "sub": str(user_id),  # Subject (user ID)
        "exp": expire,  # Expiration time
        "iat": datetime.utcnow(),  # Issued at
    }
    encoded_jwt = jwt.encode(
        to_encode, settings.better_auth_secret, algorithm=settings.algorithm
    )
    return encoded_jwt


def decode_access_token(token: str) -> UUID:
    """
    Decode and verify a JWT access token.

    Args:
        token: JWT token string

    Returns:
        User ID extracted from token

    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token, settings.better_auth_secret, algorithms=[settings.algorithm]
        )
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise JWTError("Token missing subject")
        return UUID(user_id_str)
    except JWTError as e:
        raise JWTError(f"Invalid token: {str(e)}")
