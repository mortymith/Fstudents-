from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.async_session = None
    
    def init(self, database_url: str):
        self.engine = create_async_engine(
            database_url,
            echo=False,
            future=True,
            pool_pre_ping=True,
            pool_size=20,
            max_overflow=30
        )
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False
        )
    
    async def get_session(self) -> AsyncSession:
        async with self.async_session() as session:
            try:
                yield session
            finally:
                await session.close()

    
    async def close(self):
        if self.engine:
            await self.engine.dispose()

db_manager = DatabaseManager()