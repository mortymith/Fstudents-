from core.database import db_manager as db
from models import User,Category
from sqlalchemy import select,insert
import asyncio

db.init('postgresql+asyncpg://app_user:pass12345@127.0.0.1:5432/app_db')

async def get_user(user_id: int):
    async for session in db.get_session():
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
async def insert_user(user:User):
    async for session in db.get_session():
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

user = User(
        email="jane.doe@example.com",
        password_hash="hashed_password_here",
        full_name="Jane Doe",
        role="viewer",
        is_active=True
    )

# print(asyncio.run(insert_user(user)))
