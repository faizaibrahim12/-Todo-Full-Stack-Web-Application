"""
Authentication routes: signup, login, logout.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from models.user import User
from schemas.user import UserCreate, UserLogin, UserResponse, AuthResponse
from utils.auth import hash_password, verify_password, create_access_token
from database import get_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate, session: Session = Depends(get_session)):
    """
    Register a new user.

    - Validates email format and password length
    - Checks for duplicate email
    - Hashes password
    - Creates user in database
    - Returns JWT token
    """
    logger.info(f"Signup attempt for email: {user_data.email}")

    # Check if email already exists
    statement = select(User).where(User.email == user_data.email)
    existing_user = session.exec(statement).first()
    logger.info(f"Existing user check: {existing_user}")

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )

    # Validate password length
    if len(user_data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters",
        )

    # Hash password and create user
    try:
        logger.info("Hashing password...")
        hashed_password = hash_password(user_data.password)
        logger.info("Creating new user...")
        new_user = User(email=user_data.email, password_hash=hashed_password)

        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        logger.info(f"User created with ID: {new_user.id}")

        # Generate JWT token
        logger.info("Generating JWT token...")
        token = create_access_token(new_user.id)
        logger.info("JWT token generated successfully")

        # Create UserResponse from SQLModel instance
        user_response = UserResponse(
            id=new_user.id,
            email=new_user.email,
            created_at=new_user.created_at
        )
        logger.info("UserResponse created successfully")
        
        response = AuthResponse(user=user_response, token=token)
        logger.info("AuthResponse created, returning...")
        return response
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        session.rollback()
        raise
    except Exception as e:
        logger.error(f"Error during signup: {type(e).__name__}: {e}", exc_info=True)
        session.rollback()
        # Return more detailed error for debugging
        error_msg = f"Signup failed: {type(e).__name__}: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )


@router.post("/login", response_model=AuthResponse)
async def login(credentials: UserLogin, session: Session = Depends(get_session)):
    """
    Authenticate a user and return JWT token.

    - Verifies email exists
    - Verifies password matches
    - Returns JWT token
    """
    # Find user by email
    statement = select(User).where(User.email == credentials.email)
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Generate JWT token
    token = create_access_token(user.id)

    # Create UserResponse from SQLModel instance
    user_response = UserResponse(
        id=user.id,
        email=user.email,
        created_at=user.created_at
    )
    
    return AuthResponse(user=user_response, token=token)


@router.post("/logout")
async def logout():
    """
    Logout endpoint (client-side token removal).

    Token invalidation is handled on the frontend by removing the token.
    This endpoint exists for API completeness and future server-side logout logic.
    """
    return {"message": "Logged out successfully"}
