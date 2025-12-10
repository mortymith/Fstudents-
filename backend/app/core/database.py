import asyncio
import logging
from contextlib import asynccontextmanager
from contextvars import ContextVar
from typing import AsyncGenerator, Optional, Callable, Awaitable, Any
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncSession, 
    create_async_engine, 
    async_sessionmaker,
    AsyncEngine
)

logger = logging.getLogger(__name__)


class AsyncDatabase:
    """
    Modern, thread-safe async database client with request-scoped sessions.
    Designed for async web applications and microservices.
    """
    
    def __init__(
        self,
        database_url: str,
        *,
        engine_options: Optional[dict] = None,
        session_options: Optional[dict] = None,
        enable_query_logging: bool = False
    ):
        """
        Initialize the async database client.
        
        Args:
            database_url: Database connection URL
            engine_options: Additional SQLAlchemy engine options
            session_options: Additional sessionmaker options
            enable_query_logging: Enable SQL query logging (debug only)
            
        Raises:
            ValueError: If database_url is invalid
        """
        if not database_url or not isinstance(database_url, str):
            raise ValueError("database_url must be a non-empty string")
            
        self._database_url = database_url
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[Callable[..., AsyncSession]] = None
        self._initialized = False
        self._initialization_lock = asyncio.Lock()
        
        # Default engine options
        self._engine_options = {
            "echo": enable_query_logging,
            "future": True,
            "pool_pre_ping": True,
            "pool_size": 20,
            "max_overflow": 30,
            "pool_recycle": 3600,
            "pool_timeout": 30,
            "connect_args": {
                "command_timeout": 60,
                "server_settings": {
                    "application_name": "async_db_client"
                }
            }
        }
        
        if engine_options:
            self._engine_options.update(engine_options)
            
        # Default session options
        self._session_options = {
            "class_": AsyncSession,
            "expire_on_commit": False,
            "autoflush": False,
        }
        
        if session_options:
            self._session_options.update(session_options)
        
        # Context variable for request-scoped sessions
        self._request_session: ContextVar[Optional[AsyncSession]] = ContextVar(
            'request_session', 
            default=None
        )
        
        logger.debug(f"AsyncDatabase instance created for: {self._mask_url(database_url)}")
    
    async def initialize(self) -> "AsyncDatabase":
        """
        Initialize the database engine and session factory.
        
        Returns:
            Self for fluent chaining
            
        Raises:
            RuntimeError: If already initialized
            SQLAlchemyError: If engine creation fails
        """
        async with self._initialization_lock:
            if self._initialized:
                raise RuntimeError("AsyncDatabase already initialized")
                
            try:
                logger.info("Initializing database connection")
                
                # Create async engine
                self._engine = create_async_engine(
                    self._database_url,
                    **self._engine_options
                )
                
                # Create session factory
                self._session_factory = async_sessionmaker(
                    self._engine,
                    **self._session_options
                )
                
                # Test connection
                await self._test_connection()
                
                self._initialized = True
                logger.info("Database initialized successfully")
                
                return self
                
            except SQLAlchemyError as e:
                logger.error(f"Database engine creation failed: {e}")
                await self._cleanup()
                raise
            except Exception as e:
                logger.error(f"Unexpected initialization error: {e}")
                await self._cleanup()
                raise
    
    async def _test_connection(self) -> None:
        """Test database connection with timeout."""
        try:
            async with self._engine.connect() as conn:
                # Simple version query to test connection
                result = await conn.execute(text("SELECT version();"))
                version = result.scalar()
                logger.info(f"Connected to database version: {version}")
        except asyncio.TimeoutError:
            logger.error("Database connection timeout")
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database connection test failed: {e}")
            raise
    
    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get a standalone database session.
        
        Yields:
            AsyncSession: Isolated database session
            
        Raises:
            RuntimeError: If not initialized
        """
        if not self._initialized:
            raise RuntimeError("AsyncDatabase not initialized. Call initialize() first.")
            
        session_instance: Optional[AsyncSession] = None
        try:
            session_instance = self._session_factory()
            logger.debug("Created new database session")
            
            yield session_instance
            
            await session_instance.commit()
            logger.debug("Session committed successfully")
            
        except SQLAlchemyError as e:
            logger.error(f"Database session error: {e}")
            if session_instance and session_instance.is_active:
                await session_instance.rollback()
                logger.debug("Session rolled back due to error")
            raise
            
        except Exception as e:
            logger.error(f"Unexpected error in session: {e}")
            if session_instance and session_instance.is_active:
                await session_instance.rollback()
            raise
            
        finally:
            if session_instance:
                await session_instance.close()
                logger.debug("Session closed")
    
    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get a session with automatic transaction handling.
        Rolls back on exception, commits on success.
        
        Yields:
            AsyncSession: Session with managed transaction
        """
        async with self.session() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
    
    async def get_request_session(self) -> AsyncSession:
        """
        Get or create a request-scoped session.
        Use this in web applications for per-request session management.
        
        Returns:
            AsyncSession: Request-scoped session
            
        Raises:
            RuntimeError: If not initialized
        """
        if not self._initialized:
            raise RuntimeError("AsyncDatabase not initialized")
            
        session_instance = self._request_session.get()
        
        if session_instance is None:
            session_instance = self._session_factory()
            self._request_session.set(session_instance)
            logger.debug("Created new request-scoped session")
            
        return session_instance
    
    async def close_request_session(self) -> None:
        """Close the current request-scoped session."""
        session_instance = self._request_session.get()
        
        if session_instance:
            try:
                await session_instance.close()
                logger.debug("Request-scoped session closed")
            except Exception as e:
                logger.error(f"Error closing request session: {e}")
            finally:
                self._request_session.set(None)
    
    async def execute_in_session(
        self, 
        operation: Callable[[AsyncSession], Awaitable[Any]]
    ) -> Any:
        """
        Execute an async operation within a managed session.
        
        Args:
            operation: Async function that takes a session and returns a result
            
        Returns:
            Result of the operation
            
        Raises:
            RuntimeError: If not initialized
            Exception: Any exception from the operation
        """
        async with self.session() as session:
            try:
                result = await operation(session)
                return result
            except SQLAlchemyError as e:
                logger.error(f"Database operation failed: {e}")
                raise
            except Exception as e:
                logger.error(f"Operation failed: {e}")
                raise
    
    async def shutdown(self) -> None:
        """Shutdown the database client and release all resources."""
        if not self._initialized:
            logger.warning("Attempted to shutdown non-initialized AsyncDatabase")
            return
            
        try:
            logger.info("Shutting down database client")
            
            # Close any active request session
            await self.close_request_session()
            
            # Dispose engine
            if self._engine:
                await self._engine.dispose()
                logger.debug("Database engine disposed")
            
            await self._cleanup()
            logger.info("Database client shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during database shutdown: {e}")
            raise
    
    async def _cleanup(self) -> None:
        """Cleanup internal state."""
        self._engine = None
        self._session_factory = None
        self._initialized = False
        logger.debug("Database client state cleaned up")
    
    @property
    def is_initialized(self) -> bool:
        """Check if database client is initialized."""
        return self._initialized
    
    @property
    def engine(self) -> AsyncEngine:
        """Get the SQLAlchemy async engine."""
        if not self._initialized:
            raise RuntimeError("AsyncDatabase not initialized")
        return self._engine
    
    @property
    def session_factory(self) -> Callable[..., AsyncSession]:
        """Get the session factory."""
        if not self._initialized:
            raise RuntimeError("AsyncDatabase not initialized")
        return self._session_factory
    
    def get_masked_url(self) -> str:
        """Get the database URL with password masked for logging."""
        return self._mask_url(self._database_url)
    
    @staticmethod
    def _mask_url(url: str) -> str:
        """Mask password in database URL."""
        try:
            from urllib.parse import urlparse, urlunparse
            parsed = urlparse(url)
            if parsed.password:
                netloc = parsed.netloc.replace(
                    f":{parsed.password}@", 
                    ":****@"
                )
                return urlunparse((
                    parsed.scheme,
                    netloc,
                    parsed.path,
                    parsed.params,
                    parsed.query,
                    parsed.fragment
                ))
        except Exception:
            pass
        return url
    
    async def __aenter__(self) -> "AsyncDatabase":
        """Context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        await self.shutdown()


class DatabasePool:
    """
    Manages multiple database connections for multi-tenant or sharded applications.
    """
    
    def __init__(self):
        self._databases: dict[str, AsyncDatabase] = {}
        self._lock = asyncio.Lock()
        
    async def add_database(
        self, 
        name: str, 
        database_url: str, 
        **kwargs
    ) -> AsyncDatabase:
        """
        Add a database to the pool.
        
        Args:
            name: Unique name for the database
            database_url: Database connection URL
            **kwargs: Additional arguments for AsyncDatabase
            
        Returns:
            AsyncDatabase: Initialized database client
        """
        async with self._lock:
            if name in self._databases:
                raise ValueError(f"Database '{name}' already exists in pool")
                
            db = AsyncDatabase(database_url, **kwargs)
            await db.initialize()
            self._databases[name] = db
            
            logger.info(f"Added database '{name}' to pool")
            return db
    
    async def get_database(self, name: str) -> AsyncDatabase:
        """
        Get a database from the pool.
        
        Args:
            name: Name of the database
            
        Returns:
            AsyncDatabase: Database client
            
        Raises:
            KeyError: If database not found
        """
        db = self._databases.get(name)
        if not db:
            raise KeyError(f"Database '{name}' not found in pool")
        return db
    
    async def remove_database(self, name: str) -> None:
        """Remove a database from the pool."""
        async with self._lock:
            db = self._databases.pop(name, None)
            if db:
                await db.shutdown()
                logger.info(f"Removed database '{name}' from pool")
    
    async def shutdown_all(self) -> None:
        """Shutdown all databases in the pool."""
        async with self._lock:
            for name, db in list(self._databases.items()):
                try:
                    await db.shutdown()
                except Exception as e:
                    logger.error(f"Error shutting down database '{name}': {e}")
            
            self._databases.clear()
            logger.info("All databases in pool shutdown")
    
    async def __aenter__(self) -> "DatabasePool":
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.shutdown_all()


# Factory functions for dependency injection
async def create_database_client(
    database_url: str,
    **kwargs
) -> AsyncDatabase:
    """
    Create and initialize a database client.
    
    Args:
        database_url: Database connection URL
        **kwargs: Additional arguments for AsyncDatabase
        
    Returns:
        AsyncDatabase: Initialized database client
    """
    db = AsyncDatabase(database_url, **kwargs)
    return await db.initialize()


async def create_database_pool(
    databases: dict[str, str],
    **kwargs
) -> DatabasePool:
    """
    Create and initialize a database pool.
    
    Args:
        databases: Dict of name -> database_url
        **kwargs: Additional arguments for AsyncDatabase
        
    Returns:
        DatabasePool: Initialized database pool
    """
    pool = DatabasePool()
    for name, url in databases.items():
        await pool.add_database(name, url, **kwargs)
    return pool