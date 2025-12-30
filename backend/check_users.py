from database import engine
from sqlmodel import text, select
from models.user import User

with engine.connect() as conn:
    result = conn.execute(select(User))
    users = result.all()
    print("Users:", users)
