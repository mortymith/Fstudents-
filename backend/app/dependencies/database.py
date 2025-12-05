from app.core.database import db_manager
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db() -> AsyncSession:
    async with db_manager.async_session() as session:
        try:
            yield session
        finally:
            await session.close()