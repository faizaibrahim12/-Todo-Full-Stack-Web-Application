"""Test signup logic directly."""
import sys
sys.path.insert(0, '.')

from database import get_session, create_db_and_tables
from models.user import User
from schemas.user import UserCreate
from utils.auth import hash_password, create_access_token
from schemas.user import AuthResponse, UserResponse

# Create tables
create_db_and_tables()

# Test signup
def test_signup():
    user_data = UserCreate(email="test5@example.com", password="test123456")

    session = next(get_session())
    try:
        # Check if email exists
        from sqlmodel import select
        existing = session.exec(select(User).where(User.email == user_data.email)).first()
        print(f"Existing user: {existing}")

        if existing:
            print("Email already exists!")
            return

        # Create user
        hashed = hash_password(user_data.password)
        new_user = User(email=user_data.email, password_hash=hashed)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        print(f"User created: {new_user.id} - {new_user.email}")

        # Generate token
        token = create_access_token(new_user.id)
        print(f"Token generated: {token[:50]}...")

        print("SUCCESS!")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    test_signup()
