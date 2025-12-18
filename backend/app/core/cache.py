"""
Example Of Usage:
    cache = CacheManager(settings.redis_url)
    await cache.connect()

    password_reset = PasswordResetToken(cache.get_client())
    user_session =  UserSessionRepository(cache.get_client())
    await user_session.create(user_id=12,ip_address='172.0.0.1',user_agent='mozilla',ttl_hours=1)
    print(user_session)
"""


from typing import Optional, Any
from redis.asyncio import Redis, ConnectionPool
from redis.asyncio.client import Pipeline
from redis.exceptions import RedisError, ConnectionError, TimeoutError
import logging
from contextlib import asynccontextmanager
import time
import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

@dataclass
class HealthStatus:
    """Data class for health check results."""

    healthy: bool
    connected: bool
    latency_ms: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    error: Optional[str] = None
    timestamp: Optional[datetime] = None


class CacheManager:
    """Async Redis connection manager with enhanced features."""

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        max_connections: int = 20,
        retry_attempts: int = 3,
        retry_delay: float = 1.0,
        socket_timeout: float = 10.0,
        socket_connect_timeout: float = 5.0,
    ):
        """
        Initialize AsyncCacheManager with configuration.

        Args:
            redis_url: Redis connection URL
            max_connections: Maximum number of connections in pool
            retry_attempts: Number of retry attempts for operations
            retry_delay: Delay between retries in seconds
            socket_timeout: Socket timeout for operations
            socket_connect_timeout: Socket connection timeout
        """
        self._validate_config(
            redis_url,
            max_connections,
            retry_attempts,
            retry_delay,
            socket_timeout,
            socket_connect_timeout,
        )

        self.redis_url = redis_url
        self.max_connections = max_connections
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.socket_timeout = socket_timeout
        self.socket_connect_timeout = socket_connect_timeout

        self.pool: Optional[ConnectionPool] = None
        self.client: Optional[Redis] = None
        self._is_connected = False
        self._disconnecting = False
        self._connection_lock = asyncio.Lock()

        self._setup_logging()

    def _validate_config(
        self,
        redis_url: str,
        max_connections: int,
        retry_attempts: int,
        retry_delay: float,
        socket_timeout: float,
        socket_connect_timeout: float,
    ):
        """Validate configuration parameters."""
        if not redis_url or not isinstance(redis_url, str):
            raise ValueError("redis_url must be a non-empty string")

        if not redis_url.startswith(("redis://", "rediss://", "unix://")):
            raise ValueError(
                "redis_url must start with redis://, rediss://, or unix://"
            )

        if max_connections < 1:
            raise ValueError("max_connections must be at least 1")

        if retry_attempts < 0:
            raise ValueError("retry_attempts must be non-negative")

        if retry_delay < 0:
            raise ValueError("retry_delay must be non-negative")

        if socket_timeout <= 0:
            raise ValueError("socket_timeout must be positive")

        if socket_connect_timeout <= 0:
            raise ValueError("socket_connect_timeout must be positive")

    def _setup_logging(self):
        """Ensure logging is properly configured."""
        if not logging.getLogger().handlers:
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            )
        self.logger = logging.getLogger(__name__)

    async def connect(self) -> bool:
        """
        Establish async Redis connection with connection pooling and retry logic.

        Returns:
            bool: True if connection successful, False otherwise
        """
        async with self._connection_lock:
            if self._is_connected:
                self.logger.warning("Already connected to Redis")
                return True

            attempt = 0
            last_exception = None

            while attempt <= self.retry_attempts:
                try:
                    if attempt > 0:
                        self.logger.info(
                            f"Connection retry attempt {attempt}/{self.retry_attempts}"
                        )
                        await asyncio.sleep(
                            self.retry_delay * (2 ** (attempt - 1))
                        )  # Exponential backoff

                    # Create async connection pool
                    self.pool = ConnectionPool.from_url(
                        self.redis_url,
                        max_connections=self.max_connections,
                        decode_responses=False,
                        retry_on_timeout=True,
                        health_check_interval=30,
                        socket_timeout=self.socket_timeout,
                        socket_connect_timeout=self.socket_connect_timeout,
                    )

                    # Create async Redis client
                    self.client = Redis(
                        connection_pool=self.pool, decode_responses=False
                    )

                    # Test connection
                    if not await self._test_connection():
                        raise RedisError("Connection test failed")

                    self._is_connected = True
                    self._disconnecting = False

                    self.logger.info("Async Redis connection established successfully")
                    return True

                except (
                    RedisError,
                    ConnectionError,
                    TimeoutError,
                    asyncio.TimeoutError,
                ) as e:
                    last_exception = e
                    self.logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                    attempt += 1

                    # Clean up failed connection attempts
                    await self._cleanup_failed_connection()

            self.logger.error(
                f"Failed to connect to Redis after {self.retry_attempts + 1} attempts: {last_exception}"
            )
            return False

    async def _test_connection(self) -> bool:
        """Test Redis connection with timeout and command verification."""
        try:
            # Simple ping test
            if not await self.client.ping():
                return False

            # Test basic operations
            test_key = f"__connection_test_{int(time.time())}"
            await self.client.set(test_key, b"test", ex=1)  # Auto-expire in 1 second
            result = await self.client.get(test_key)
            return result == b"test"

        except (RedisError, ConnectionError, TimeoutError, asyncio.TimeoutError) as e:
            self.logger.warning(f"Connection test failed: {e}")
            return False

    async def _cleanup_failed_connection(self):
        """Clean up resources after failed connection attempts."""
        self._is_connected = False

        if self.client:
            try:
                await self.client.close()
            except Exception as e:
                self.logger.debug(f"Error closing client during cleanup: {e}")
            finally:
                self.client = None

        if self.pool:
            try:
                await self.pool.disconnect()
            except Exception as e:
                self.logger.debug(f"Error disconnecting pool during cleanup: {e}")
            finally:
                self.pool = None

    async def disconnect(self):
        """Safely close async Redis connection."""
        if self._disconnecting:
            self.logger.warning("Already disconnecting from Redis")
            return

        self._disconnecting = True

        try:
            async with self._connection_lock:
                if self.client:
                    try:
                        await self.client.close()
                        self.logger.debug("Async Redis client closed")
                    except Exception as e:
                        self.logger.warning(f"Error closing async Redis client: {e}")
                    finally:
                        self.client = None

                if self.pool:
                    try:
                        await self.pool.disconnect()
                        self.logger.debug("Async connection pool disconnected")
                    except Exception as e:
                        self.logger.warning(f"Error disconnecting async pool: {e}")
                    finally:
                        self.pool = None

                self._is_connected = False
                self.logger.info("Async Redis connection closed successfully")

        except Exception as e:
            self.logger.error(f"Unexpected error during async disconnect: {e}")
            raise
        finally:
            self._disconnecting = False

    async def health_check(self) -> HealthStatus:
        """
        Comprehensive async health check.

        Returns:
            HealthStatus: Detailed health information
        """
        health = HealthStatus(healthy=False, connected=False, timestamp=datetime.now())

        try:
            if not self.client or not self._is_connected:
                health.error = "Not connected to Redis"
                return health

            # Test connectivity and measure latency
            start_time = time.time()
            if not await self.client.ping():
                health.error = "Ping failed"
                return health

            health.latency_ms = (time.time() - start_time) * 1000

            # Test basic operations
            test_key = f"__health_check_{int(time.time())}"
            test_value = b"health_check_value"

            if not await self.client.set(test_key, test_value, ex=5):
                health.error = "SET operation failed"
                return health

            retrieved = await self.client.get(test_key)
            if retrieved != test_value:
                health.error = "GET operation failed or returned wrong value"
                return health

            # Check Redis memory usage if possible
            try:
                info = await self.client.info("memory")
                health.memory_usage_mb = info.get("used_memory", 0) / (1024 * 1024)
            except BaseException:
                pass  # Memory info is optional

            health.connected = True
            health.healthy = True

        except RedisError as e:
            health.error = f"Redis error: {str(e)}"
        except Exception as e:
            health.error = f"Unexpected error: {str(e)}"

        return health

    def is_connected(self) -> bool:
        """Check if Redis is currently connected."""
        return self._is_connected and self.client is not None

    def get_client(self) -> Optional[Redis]:
        """
        Get async Redis client instance.

        Returns:
            Redis client instance or None if not connected
        """
        if not self._is_connected or not self.client:
            self.logger.warning("Attempted to get client without connection")
            return None

        return self.client

    async def safe_operation(self, operation: callable, *args, **kwargs) -> Any:
        """
        Execute async Redis operation with automatic retry and error handling.

        Args:
            operation: Async Redis operation function to execute
            *args: Arguments for the operation
            **kwargs: Keyword arguments for the operation

        Returns:
            Result of the operation or None if failed
        """
        client = self.get_client()
        if not client:
            self.logger.error("Cannot perform operation: not connected")
            return None

        last_exception = None
        for attempt in range(self.retry_attempts + 1):
            try:
                if attempt > 0:
                    self.logger.info(
                        f"Operation retry attempt {attempt}/{self.retry_attempts}"
                    )
                    await asyncio.sleep(self.retry_delay * (2 ** (attempt - 1)))

                return await operation(client, *args, **kwargs)

            except (
                RedisError,
                ConnectionError,
                TimeoutError,
                asyncio.TimeoutError,
            ) as e:
                last_exception = e
                self.logger.warning(f"Operation failed on attempt {attempt + 1}: {e}")

                # Try to re-establish connection if it's a connection error
                if attempt < self.retry_attempts and isinstance(
                    e, (ConnectionError, TimeoutError)
                ):
                    self.logger.info("Attempting to reconnect...")
                    if not await self.connect():
                        continue

        self.logger.error(
            f"Operation failed after {self.retry_attempts + 1} attempts: {last_exception}"
        )
        return None

    async def get(self, key: str, decode_json: bool = False) -> Any:
        """Async get with optional JSON decoding."""

        async def _get(client, k):
            return await client.get(k)

        result = await self.safe_operation(_get, key)

        if result and decode_json:
            try:
                return json.loads(result.decode())
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                self.logger.error(f"Failed to decode JSON for key {key}: {e}")
                return None

        return result

    async def set(
        self, key: str, value: Any, ex: Optional[int] = None, encode_json: bool = False
    ) -> bool:
        """Async set with optional JSON encoding."""

        async def _set(client, k, v, expiry=None):
            if expiry:
                return await client.set(k, v, ex=expiry)
            else:
                return await client.set(k, v)

        if encode_json and isinstance(value, (dict, list)):
            value = json.dumps(value).encode()
        elif isinstance(value, str):
            value = value.encode()

        result = await self.safe_operation(_set, key, value, ex)
        return bool(result)

    async def delete(self, *keys: str) -> int:
        """Async delete multiple keys."""

        async def _delete(client, *ks):
            return await client.delete(*ks)

        return await self.safe_operation(_delete, *keys) or 0

    async def exists(self, *keys: str) -> int:
        """Async check if keys exist."""

        async def _exists(client, *ks):
            return await client.exists(*ks)

        return await self.safe_operation(_exists, *keys) or 0

    async def expire(self, key: str, time: int) -> bool:
        """Async set expiration time."""

        async def _expire(client, k, t):
            return await client.expire(k, t)

        result = await self.safe_operation(_expire, key, time)
        return bool(result)

    async def incr(self, key: str, amount: int = 1) -> Optional[int]:
        """Async increment counter."""

        async def _incr(client, k, amt):
            if amt == 1:
                return await client.incr(k)
            else:
                return await client.incrby(k, amt)

        return await self.safe_operation(_incr, key, amount)

    async def pipeline(self) -> Optional[Pipeline]:
        """Get async pipeline for batch operations."""
        client = self.get_client()
        if not client:
            return None

        return client.pipeline()

    async def execute_pipeline(self, pipe: Pipeline) -> list:
        """Execute async pipeline with retry logic."""

        async def _execute(p):
            return await p.execute()

        return await self.safe_operation(_execute, pipe) or []

    @asynccontextmanager
    async def connection_context(self):
        """
        Async context manager for Redis connection.

        Usage:
            async with cache_manager.connection_context():
                # Use cache_manager.get_client() here
                pass
        """
        try:
            if not await self.connect():
                raise ConnectionError("Failed to connect to Redis")
            yield self
        finally:
            await self.disconnect()

    async def __aenter__(self):
        """Async context manager entry."""
        if not await self.connect():
            raise ConnectionError("Failed to connect to Redis")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()

    async def monitor_health(self, interval_seconds: int = 60) -> asyncio.Task:
        """
        Start background health monitoring task.

        Args:
            interval_seconds: Health check interval in seconds

        Returns:
            asyncio.Task: The monitoring task
        """

        async def _monitor():
            while self.is_connected():
                health = await self.health_check()
                if not health.healthy:
                    self.logger.warning(f"Cache health check failed: {health.error}")
                await asyncio.sleep(interval_seconds)

        task = asyncio.create_task(_monitor())
        return task

    async def flush_all(self) -> bool:
        """Async flush all database (use with caution!)."""

        async def _flush(client):
            return await client.flushall()

        self.logger.warning("Flushing all Redis data")
        result = await self.safe_operation(_flush)
        return bool(result)
