# app/dependencies/database.py
"""
Database dependencies for FastAPI.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.database import AsyncDatabase
import asyncio
from app.repositories import StockMovementRepository



async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session.
    
    Usage:
        async def some_route(db: AsyncSession = Depends(get_db_session)):
            # Use db session
            pass
    """
    async with AsyncDatabase(database_url=settings.postgresql_url) as db:
        async with db.session() as session:
            yield session









