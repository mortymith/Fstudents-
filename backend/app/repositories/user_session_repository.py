"""
Redis Repository for  User Sessions Implements secure session.
"""

from typing import Any, Optional, List, Dict, Tuple
from datetime import datetime, timedelta
import asyncio
import secrets
from redis.asyncio import Redis
from redis.exceptions import RedisError
import logging


class UserSessionRepository:
    """Async Redis repository for user_sessions table."""

    def __init__(self, redis_client: Redis, key_prefix: str = "session:"):
        self.redis = redis_client
        self.key_prefix = key_prefix
        self.logger = logging.getLogger(f"{__name__}.UserSessionsRepo")

        # Key templates
        self.SESSION_KEY = f"{key_prefix}{{token}}"  # Hash for session object
        self.USER_SESSIONS_KEY = (
            f"{key_prefix}user:{{user_id}}"  # Sorted set: user_id -> sessions
        )
        self.SESSION_EXPIRY_KEY = (
            f"{key_prefix}expiry"  # Sorted set: expiry -> sessions
        )
        self.ACTIVITY_KEY = (
            f"{key_prefix}activity"  # Sorted set: last_activity -> sessions
        )
        self.IP_SESSIONS_KEY = f"{key_prefix}ip:{{ip}}"  # Set: IP -> sessions
        self.SESSION_BY_ID_KEY = (
            f"{key_prefix}id:{{id}}"  # Map internal ID to session token
        )

        # Security configuration
        self.DEFAULT_SESSION_TTL = timedelta(hours=24)  # NF-SEC-003: Session expiration
        self.INACTIVITY_TIMEOUT = timedelta(minutes=30)  # Inactive session cleanup
        self.MAX_SESSIONS_PER_USER = 15  # Limit concurrent sessions

    # =============== CRUD OPERATIONS ===============

    async def create(
        self, user_id: int, ip_address: str, user_agent: str, ttl_hours: int = 24
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new user session.
        Enforces security limits and tracking requirements.
        """
        # Generate secure session token
        session_token = secrets.token_urlsafe(48)
        session_id = await self.redis.incr(f"{self.key_prefix}id_seq")
        expires_at = datetime.now() + timedelta(hours=ttl_hours)

        session_data = {
            "id": session_id,
            "user_id": user_id,
            "session_token": session_token,
            "expires_at": expires_at.isoformat(),
            "ip_address": ip_address,
            "user_agent": user_agent,
            "last_activity_at": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat(),
        }

        # Check session limits before creating
        if not await self._check_session_limits(user_id):
            self.logger.warning(f"User {user_id} has too many active sessions")
            return None

        async with self.redis.pipeline(transaction=True) as pipe:
            # Store session as Hash
            session_key = self.SESSION_KEY.format(token=session_token)
            await pipe.hset(
                session_key,
                mapping={
                    "id": str(session_id),
                    "user_id": str(user_id),
                    "session_token": session_token,
                    "expires_at": expires_at.isoformat(),
                    "ip_address": ip_address,
                    "user_agent": user_agent,
                    "last_activity_at": datetime.now().isoformat(),
                    "created_at": datetime.now().isoformat(),
                },
            )

            # Set TTL for automatic cleanup
            await pipe.expireat(session_key, int(expires_at.timestamp()))

            # Add to user's sessions (score = expiry timestamp)
            user_sessions_key = self.USER_SESSIONS_KEY.format(user_id=user_id)
            await pipe.zadd(user_sessions_key, {session_token: expires_at.timestamp()})

            # Add to expiry index
            await pipe.zadd(
                self.SESSION_EXPIRY_KEY, {session_token: expires_at.timestamp()}
            )

            # Add to activity index (score = last activity timestamp)
            await pipe.zadd(
                self.ACTIVITY_KEY, {session_token: datetime.now().timestamp()}
            )

            # Add to IP tracking
            ip_sessions_key = self.IP_SESSIONS_KEY.format(ip=ip_address)
            await pipe.sadd(ip_sessions_key, session_token)
            await pipe.expire(ip_sessions_key, 86400)  # IP index expires in 24h

            # Map internal ID to session token
            await pipe.set(self.SESSION_BY_ID_KEY.format(id=session_id), session_token)

            # Enforce session limits by removing oldest if needed
            session_count = await self.redis.zcard(user_sessions_key)
            if session_count > self.MAX_SESSIONS_PER_USER:
                # Remove oldest session (lowest score = earliest expiry)
                oldest = await self.redis.zrange(user_sessions_key, 0, 0)
                if oldest:
                    await self.delete(oldest[0].decode())

            try:
                await pipe.execute()
                self.logger.info(
                    f"Created session for user {user_id} from IP {ip_address}"
                )
                return session_data
            except RedisError as e:
                self.logger.error(f"Failed to create session: {e}")
                return None

    async def get(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Get session data by token."""
        session_key = self.SESSION_KEY.format(token=session_token)
        data = await self.redis.hgetall(session_key)

        if not data:
            return None

        return self._parse_session_data(data)

    async def get_by_id(self, id: int) -> Optional[Dict[str, Any]]:
        """Get session by internal ID."""
        token = await self.redis.get(self.SESSION_BY_ID_KEY.format(id=id))
        if not token:
            return None
        return await self.get(token.decode())

    async def update_activity(self, session_token: str) -> bool:
        """Update last activity timestamp for a session."""
        session_key = self.SESSION_KEY.format(token=session_token)
        now = datetime.now()

        async with self.redis.pipeline(transaction=True) as pipe:
            # Update hash field
            await pipe.hset(session_key, "last_activity_at", now.isoformat())

            # Update activity sorted set
            await pipe.zadd(self.ACTIVITY_KEY, {session_token: now.timestamp()})

            try:
                await pipe.execute()
                return True
            except RedisError as e:
                self.logger.error(
                    f"Failed to update activity for session {session_token}: {e}"
                )
                return False

    async def extend(self, session_token: str, additional_hours: int = 1) -> bool:
        """Extend session expiration."""
        session_data = await self.get(session_token)
        if not session_data:
            return False

        new_expiry = datetime.now() + timedelta(hours=additional_hours)

        async with self.redis.pipeline(transaction=True) as pipe:
            session_key = self.SESSION_KEY.format(token=session_token)

            # Update expiration in hash
            await pipe.hset(session_key, "expires_at", new_expiry.isoformat())

            # Update TTL
            await pipe.expireat(session_key, int(new_expiry.timestamp()))

            # Update expiry index
            await pipe.zadd(
                self.SESSION_EXPIRY_KEY, {session_token: new_expiry.timestamp()}
            )

            # Update user sessions index
            user_sessions_key = self.USER_SESSIONS_KEY.format(
                user_id=session_data["user_id"]
            )
            await pipe.zadd(user_sessions_key, {session_token: new_expiry.timestamp()})

            try:
                await pipe.execute()
                return True
            except RedisError as e:
                self.logger.error(f"Failed to extend session {session_token}: {e}")
                return False

    async def delete(self, session_token: str) -> bool:
        """Delete session and clean up indexes."""
        session_data = await self.get(session_token)
        if not session_data:
            return False

        async with self.redis.pipeline(transaction=True) as pipe:
            session_key = self.SESSION_KEY.format(token=session_token)

            # Delete main session object
            await pipe.delete(session_key)

            # Remove from user's sessions
            user_sessions_key = self.USER_SESSIONS_KEY.format(
                user_id=session_data["user_id"]
            )
            await pipe.zrem(user_sessions_key, session_token)

            # Remove from expiry index
            await pipe.zrem(self.SESSION_EXPIRY_KEY, session_token)

            # Remove from activity index
            await pipe.zrem(self.ACTIVITY_KEY, session_token)

            # Remove from IP tracking
            ip_sessions_key = self.IP_SESSIONS_KEY.format(ip=session_data["ip_address"])
            await pipe.srem(ip_sessions_key, session_token)

            # Delete ID mapping
            if session_data.get("id"):
                await pipe.delete(self.SESSION_BY_ID_KEY.format(id=session_data["id"]))

            try:
                await pipe.execute()
                self.logger.info(
                    f"Deleted session {session_token} for user {session_data['user_id']}"
                )
                return True
            except RedisError as e:
                self.logger.error(f"Failed to delete session {session_token}: {e}")
                return False

    # =============== QUERY METHODS ===============

    async def find_by_user(
        self, user_id: int, active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """Find all sessions for a specific user."""
        user_sessions_key = self.USER_SESSIONS_KEY.format(user_id=user_id)

        if active_only:
            # Get only active sessions (not expired)
            now = datetime.now().timestamp()
            tokens = await self.redis.zrangebyscore(
                user_sessions_key, min=now, max="+inf"  # Only future expiries
            )
        else:
            tokens = await self.redis.zrange(user_sessions_key, 0, -1)

        if not tokens:
            return []

        # Fetch all sessions in parallel
        tasks = [self.get(token.decode()) for token in tokens]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        valid_sessions = []
        for result in results:
            if isinstance(result, Exception):
                continue
            if result:
                valid_sessions.append(result)

        # Sort by last activity (most recent first)
        valid_sessions.sort(key=lambda x: x["last_activity_at"], reverse=True)
        return valid_sessions

    async def find_by_ip(self, ip_address: str) -> List[Dict[str, Any]]:
        """Find all sessions from a specific IP address."""
        ip_sessions_key = self.IP_SESSIONS_KEY.format(ip=ip_address)
        tokens = await self.redis.smembers(ip_sessions_key)

        if not tokens:
            return []

        tasks = [self.get(token.decode()) for token in tokens]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        return [r for r in results if not isinstance(r, Exception) and r]

    async def find_inactive(self, inactive_minutes: int = 30) -> List[Dict[str, Any]]:
        """Find sessions inactive for specified minutes."""
        cutoff = datetime.now().timestamp() - (inactive_minutes * 60)
        inactive_tokens = await self.redis.zrangebyscore(
            self.ACTIVITY_KEY, min="-inf", max=cutoff
        )

        tasks = [self.get(token.decode()) for token in inactive_tokens]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        return [r for r in results if not isinstance(r, Exception) and r]

    async def find_expiring_soon(self, hours: int = 1) -> List[Dict[str, Any]]:
        """Find sessions expiring within specified hours."""
        now = datetime.now().timestamp()
        max_time = now + (hours * 3600)

        expiring_tokens = await self.redis.zrangebyscore(
            self.SESSION_EXPIRY_KEY, min=now, max=max_time
        )

        tasks = [self.get(token.decode()) for token in expiring_tokens]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        return [r for r in results if not isinstance(r, Exception) and r]

    async def validate_session(self, session_token: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a session token.
        Returns (is_valid, error_message)
        """
        session_data = await self.get(session_token)
        if not session_data:
            return False, "Invalid session"

        expiry = datetime.fromisoformat(session_data["expires_at"].isoformat())
        if expiry < datetime.now():
            return False, "Session expired"

        # Check inactivity timeout (optional)
        last_activity = datetime.fromisoformat(
            session_data["last_activity_at"].isoformat()
        )
        if datetime.now() - last_activity > self.INACTIVITY_TIMEOUT:
            return False, "Session inactive"

        return True, None

    # =============== SECURITY & MAINTENANCE METHODS ===============

    async def revoke_user_sessions(
        self, user_id: int, keep_current: Optional[str] = None
    ) -> int:
        """Revoke all sessions for a user, optionally keeping one."""
        sessions = await self.find_by_user(user_id, active_only=False)

        revoked_count = 0
        for session in sessions:
            if keep_current and session["session_token"] == keep_current:
                continue

            if await self.delete(session["session_token"]):
                revoked_count += 1

        self.logger.info(f"Revoked {revoked_count} sessions for user {user_id}")
        return revoked_count

    async def revoke_sessions_by_ip(self, ip_address: str) -> int:
        """Revoke all sessions from a specific IP address."""
        sessions = await self.find_by_ip(ip_address)

        revoked_count = 0
        for session in sessions:
            if await self.delete(session["session_token"]):
                revoked_count += 1

        self.logger.warning(
            f"Revoked {revoked_count} sessions from suspicious IP {ip_address}"
        )
        return revoked_count

    async def cleanup_expired(self, batch_size: int = 100) -> int:
        """Clean up expired sessions."""
        now = datetime.now().timestamp()
        expired_tokens = await self.redis.zrangebyscore(
            self.SESSION_EXPIRY_KEY, min="-inf", max=now
        )

        deleted_count = 0
        for i in range(0, len(expired_tokens), batch_size):
            batch = expired_tokens[i : i + batch_size]

            tasks = [self.delete(token.decode()) for token in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, Exception):
                    continue
                if result:
                    deleted_count += 1

            if i + batch_size < len(expired_tokens):
                await asyncio.sleep(0.01)

        self.logger.info(f"Cleaned up {deleted_count} expired sessions")
        return deleted_count

    async def cleanup_inactive(
        self, inactive_minutes: int = 30, batch_size: int = 50
    ) -> int:
        """Clean up inactive sessions."""
        inactive_sessions = await self.find_inactive(inactive_minutes)

        deleted_count = 0
        for i in range(0, len(inactive_sessions), batch_size):
            batch = inactive_sessions[i : i + batch_size]

            tasks = [self.delete(session["session_token"]) for session in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, Exception):
                    continue
                if result:
                    deleted_count += 1

            if i + batch_size < len(inactive_sessions):
                await asyncio.sleep(0.01)

        self.logger.info(f"Cleaned up {deleted_count} inactive sessions")
        return deleted_count

    async def get_stats(self) -> Dict[str, Any]:
        """Get session repository statistics."""
        total_sessions = await self.redis.zcard(self.SESSION_EXPIRY_KEY)
        active_sessions = await self.redis.zcount(
            self.SESSION_EXPIRY_KEY, min=datetime.now().timestamp(), max="+inf"
        )

        # Get unique user count (approximate)
        user_pattern = f"{self.key_prefix}user:*"
        user_keys = []
        cursor = 0
        while True:
            cursor, keys = await self.redis.scan(
                cursor=cursor, match=user_pattern, count=100
            )
            user_keys.extend(keys)
            if cursor == 0:
                break

        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "expired_sessions": total_sessions - active_sessions,
            "unique_users": len(user_keys),
            "inactive_sessions": await self.redis.zcount(
                self.ACTIVITY_KEY,
                min="-inf",
                max=(datetime.now() - self.INACTIVITY_TIMEOUT).timestamp(),
            ),
        }

    async def get_user_session_stats(self, user_id: int) -> Dict[str, Any]:
        """Get session statistics for a specific user."""
        sessions = await self.find_by_user(user_id, active_only=False)
        active_sessions = [
            s
            for s in sessions
            if datetime.fromisoformat(s["expires_at"].isoformat()) > datetime.now()
        ]

        return {
            "total_sessions": len(sessions),
            "active_sessions": len(active_sessions),
            "latest_activity": (
                max([s["last_activity_at"] for s in sessions]) if sessions else None
            ),
            "ip_addresses": list(set([s["ip_address"] for s in sessions])),
            "user_agents": list(set([s["user_agent"] for s in sessions])),
        }

    # =============== HELPER METHODS ===============

    def _parse_session_data(self, redis_data: Dict[bytes, bytes]) -> Dict[str, Any]:
        """Parse Redis hash data into Python dict with proper types."""
        result = {}
        for key_bytes, value_bytes in redis_data.items():
            key = key_bytes.decode()
            value = value_bytes.decode()

            if key in ["id", "user_id"]:
                result[key] = int(value) if value else None
            elif key in ["expires_at", "last_activity_at", "created_at"]:
                result[key] = datetime.fromisoformat(value) if value else None
            else:
                result[key] = value

        return result

    async def _check_session_limits(self, user_id: int) -> bool:
        """Check if user has reached session limits."""
        user_sessions_key = self.USER_SESSIONS_KEY.format(user_id=user_id)
        session_count = await self.redis.zcard(user_sessions_key)

        if session_count >= self.MAX_SESSIONS_PER_USER:
            # Try to clean up expired sessions first
            now = datetime.now().timestamp()
            expired_count = await self.redis.zcount(
                user_sessions_key, min="-inf", max=now
            )

            if session_count - expired_count >= self.MAX_SESSIONS_PER_USER:
                return False

        return True

    async def _update_indexes(self, session_token: str, session_data: Dict[str, Any]):
        """Update all indexes for a session."""
        async with self.redis.pipeline(transaction=True) as pipe:
            expiry = (
                session_data["expires_at"].timestamp()
                if isinstance(session_data["expires_at"], datetime)
                else datetime.fromisoformat(session_data["expires_at"]).timestamp()
            )
            activity = (
                session_data["last_activity_at"].timestamp()
                if isinstance(session_data["last_activity_at"], datetime)
                else datetime.fromisoformat(
                    session_data["last_activity_at"]
                ).timestamp()
            )

            # Update user sessions index
            user_sessions_key = self.USER_SESSIONS_KEY.format(
                user_id=session_data["user_id"]
            )
            await pipe.zadd(user_sessions_key, {session_token: expiry})

            # Update expiry index
            await pipe.zadd(self.SESSION_EXPIRY_KEY, {session_token: expiry})

            # Update activity index
            await pipe.zadd(self.ACTIVITY_KEY, {session_token: activity})

            # Update IP index
            ip_sessions_key = self.IP_SESSIONS_KEY.format(ip=session_data["ip_address"])
            await pipe.sadd(ip_sessions_key, session_token)
            await pipe.expire(ip_sessions_key, 86400)

            try:
                await pipe.execute()
            except RedisError as e:
                self.logger.error(
                    f"Failed to update indexes for session {session_token}: {e}"
                )
