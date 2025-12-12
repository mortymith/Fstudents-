"""
Redis Repository for  Password Reset Token Repository.
"""

from typing import Any, Optional, List, Dict, Tuple
from datetime import datetime, timedelta
import asyncio
import secrets
from redis.asyncio import Redis
from redis.exceptions import RedisError
import logging


class PasswordResetTokenRepository:
    """Async Redis repository for password_reset_tokens table."""

    def __init__(self, redis_client: Redis, key_prefix: str = "reset_token:"):
        self.redis = redis_client
        self.key_prefix = key_prefix
        self.logger = logging.getLogger(f"{__name__}.PasswordResetTokensRepo")

        # Key templates
        self.TOKEN_KEY = f"{key_prefix}{{token}}"  # Hash for token object
        self.USER_TOKENS_KEY = (
            f"{key_prefix}user:{{user_id}}"  # Sorted set: user_id -> tokens
        )
        self.EXPIRY_KEY = f"{key_prefix}expiry"  # Sorted set: expiry -> tokens
        self.USED_KEY = f"{key_prefix}used"  # Set of used tokens
        self.PENDING_KEY = f"{key_prefix}pending"  # Set of pending tokens
        self.TOKEN_BY_ID_KEY = f"{key_prefix}id:{{id}}"  # Map internal ID to token

        # Configuration
        self.DEFAULT_EXPIRY = timedelta(hours=1)  # NF-SEC-003: Token expiration

    # =============== CRUD OPERATIONS ===============

    async def create(
        self, user_id: int, expiry_minutes: int = 60
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new password reset token.
        Returns token data if successful.
        """
        # Generate cryptographically secure token
        reset_token = secrets.token_urlsafe(32)
        token_id = await self.redis.incr(f"{self.key_prefix}id_seq")
        token_expires = datetime.now() + timedelta(minutes=expiry_minutes)

        token_data = {
            "id": token_id,
            "user_id": user_id,
            "reset_token": reset_token,
            "token_expires": token_expires.isoformat(),
            "is_used": False,
            "created_at": datetime.now().isoformat(),
            "used_at": None,
        }

        # Atomic transaction to ensure consistency
        async with self.redis.pipeline(transaction=True) as pipe:
            # Store token object as Hash
            token_key = self.TOKEN_KEY.format(token=reset_token)
            await pipe.hset(
                token_key,
                mapping={
                    "id": str(token_id),
                    "user_id": str(user_id),
                    "reset_token": reset_token,
                    "token_expires": token_expires.isoformat(),
                    "is_used": "0",  # Redis stores as string
                    "created_at": datetime.now().isoformat(),
                    "used_at": "",
                },
            )

            # Set expiration on token (auto-cleanup)
            await pipe.expireat(token_key, int(token_expires.timestamp()))

            # Add to user's token sorted set (score = expiry timestamp)
            user_tokens_key = self.USER_TOKENS_KEY.format(user_id=user_id)
            await pipe.zadd(user_tokens_key, {reset_token: token_expires.timestamp()})

            # Add to expiry sorted set
            await pipe.zadd(self.EXPIRY_KEY, {reset_token: token_expires.timestamp()})

            # Add to pending tokens set
            await pipe.sadd(self.PENDING_KEY, reset_token)

            # Map internal ID to token
            await pipe.set(self.TOKEN_BY_ID_KEY.format(id=token_id), reset_token)

            try:
                await pipe.execute()
                self.logger.info(
                    f"Created reset token for user {user_id}, expires {token_expires}"
                )
                return token_data
            except RedisError as e:
                self.logger.error(f"Failed to create reset token: {e}")
                return None

    async def get(self, token: str) -> Optional[Dict[str, Any]]:
        """Get token data by reset token."""
        token_key = self.TOKEN_KEY.format(token=token)
        data = await self.redis.hgetall(token_key)

        if not data:
            return None

        return self._parse_token_data(data)

    async def get_by_id(self, id: int) -> Optional[Dict[str, Any]]:
        """Get token data by internal ID."""
        token = await self.redis.get(self.TOKEN_BY_ID_KEY.format(id=id))
        if not token:
            return None
        return await self.get(token.decode())

    async def update(self, token: str, updates: Dict[str, Any]) -> bool:
        """Update specific fields of a token."""
        token_key = self.TOKEN_KEY.format(token=token)

        # Prepare updates
        redis_updates = {}
        for field, value in updates.items():
            if field == "is_used" and value is True:
                redis_updates["is_used"] = "1"
                redis_updates["used_at"] = datetime.now().isoformat()
            elif field == "is_used" and value is False:
                redis_updates["is_used"] = "0"
                redis_updates["used_at"] = ""
            elif isinstance(value, datetime):
                redis_updates[field] = value.isoformat()
            else:
                redis_updates[field] = str(value)

        if not redis_updates:
            return False

        async with self.redis.pipeline(transaction=True) as pipe:
            # Update hash
            if redis_updates:
                await pipe.hset(token_key, mapping=redis_updates)

            # If marking as used, update indexes
            if "is_used" in redis_updates and redis_updates["is_used"] == "1":
                # Remove from pending, add to used
                await pipe.srem(self.PENDING_KEY, token)
                await pipe.sadd(self.USED_KEY, token)

            try:
                await pipe.execute()
                return True
            except RedisError as e:
                self.logger.error(f"Failed to update token {token}: {e}")
                return False

    async def delete(self, token: str) -> bool:
        """Delete token and clean up indexes."""
        # First get token data to clean up indexes
        token_data = await self.get(token)
        if not token_data:
            return False

        async with self.redis.pipeline(transaction=True) as pipe:
            token_key = self.TOKEN_KEY.format(token=token)
            user_id = token_data["user_id"]

            # Delete main token object
            await pipe.delete(token_key)

            # Remove from user's tokens
            user_tokens_key = self.USER_TOKENS_KEY.format(user_id=user_id)
            await pipe.zrem(user_tokens_key, token)

            # Remove from expiry index
            await pipe.zrem(self.EXPIRY_KEY, token)

            # Remove from pending/used sets
            await pipe.srem(self.PENDING_KEY, token)
            await pipe.srem(self.USED_KEY, token)

            # Delete ID mapping if exists
            if token_data.get("id"):
                await pipe.delete(self.TOKEN_BY_ID_KEY.format(id=token_data["id"]))

            try:
                await pipe.execute()
                return True
            except RedisError as e:
                self.logger.error(f"Failed to delete token {token}: {e}")
                return False

    # =============== QUERY METHODS ===============

    async def find_by_user(
        self, user_id: int, include_used: bool = False
    ) -> List[Dict[str, Any]]:
        """Find all tokens for a specific user."""
        user_tokens_key = self.USER_TOKENS_KEY.format(user_id=user_id)
        tokens = await self.redis.zrange(user_tokens_key, 0, -1)

        if not tokens:
            return []

        # Fetch all tokens in parallel
        tasks = [self.get(token.decode()) for token in tokens]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                continue
            if result and (include_used or not result["is_used"]):
                valid_results.append(result)

        # Sort by creation date (newest first)
        valid_results.sort(key=lambda x: x["created_at"], reverse=True)
        return valid_results

    async def find_valid_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        """Find valid (unexpired, unused) tokens for a user."""
        all_tokens = await self.find_by_user(user_id, include_used=False)
        now = datetime.now()

        return [
            token
            for token in all_tokens
            if datetime.fromisoformat(token["token_expires"]) > now
        ]

    async def find_expired(self, before: Optional[datetime] = None) -> List[str]:
        """Find expired tokens."""
        score_max = before.timestamp() if before else datetime.now().timestamp()
        expired = await self.redis.zrangebyscore(
            self.EXPIRY_KEY, min="-inf", max=score_max
        )
        return [token.decode() for token in expired]

    async def find_pending(self) -> List[str]:
        """Get all pending (unused) tokens."""
        pending = await self.redis.smembers(self.PENDING_KEY)
        return [token.decode() for token in pending]

    async def find_used(self) -> List[str]:
        """Get all used tokens."""
        used = await self.redis.smembers(self.USED_KEY)
        return [token.decode() for token in used]

    async def validate_token(self, token: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a reset token.
        Returns (is_valid, error_message)
        """
        token_data = await self.get(token)
        if not token_data:
            return False, "Invalid token"

        if token_data["is_used"]:
            return False, "Token already used"

        expiry = datetime.fromisoformat(token_data["token_expires"].isoformat())
        if expiry < datetime.now():
            return False, "Token expired"

        return True, None

    async def use_token(self, token: str) -> bool:
        """Mark a token as used."""
        token_data = await self.get(token)
        if not token_data:
            return False

        if token_data["is_used"]:
            self.logger.warning(f"Attempt to reuse token {token}")
            return False

        return await self.update(token, {"is_used": True})

    # =============== MAINTENANCE METHODS ===============

    async def cleanup_expired(self, batch_size: int = 100) -> int:
        """Clean up expired tokens in batches."""
        expired = await self.find_expired()

        deleted_count = 0
        for i in range(0, len(expired), batch_size):
            batch = expired[i : i + batch_size]

            # Delete in parallel
            tasks = [self.delete(token) for token in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Count successful deletions
            for result in results:
                if isinstance(result, Exception):
                    continue
                if result:
                    deleted_count += 1

            # Small delay to prevent Redis overload
            if i + batch_size < len(expired):
                await asyncio.sleep(0.01)

        self.logger.info(f"Cleaned up {deleted_count} expired tokens")
        return deleted_count

    async def revoke_user_tokens(self, user_id: int) -> int:
        """Revoke all tokens for a user."""
        tokens = await self.find_by_user(user_id, include_used=True)

        revoked_count = 0
        for token_data in tokens:
            if await self.delete(token_data["reset_token"]):
                revoked_count += 1

        self.logger.info(f"Revoked {revoked_count} tokens for user {user_id}")
        return revoked_count

    async def get_stats(self) -> Dict[str, Any]:
        """Get repository statistics."""
        pending_count = await self.redis.scard(self.PENDING_KEY)
        used_count = await self.redis.scard(self.USED_KEY)
        expiry_count = await self.redis.zcard(self.EXPIRY_KEY)

        # Estimate total active tokens (not expired)
        now = datetime.now().timestamp()
        active_count = await self.redis.zcount(self.EXPIRY_KEY, min=now, max="+inf")

        return {
            "pending_tokens": pending_count,
            "used_tokens": used_count,
            "total_tracked": expiry_count,
            "active_tokens": active_count,
            "expired_tokens": expiry_count - active_count,
        }

    # =============== HELPER METHODS ===============

    def _parse_token_data(self, redis_data: Dict[bytes, bytes]) -> Dict[str, Any]:
        """Parse Redis hash data into Python dict with proper types."""
        result = {}
        for key_bytes, value_bytes in redis_data.items():
            key = key_bytes.decode()
            value = value_bytes.decode()

            if key in ["id", "user_id"]:
                result[key] = int(value) if value else None
            elif key == "is_used":
                result[key] = value == "1"
            elif key in ["token_expires", "created_at", "used_at"]:
                result[key] = datetime.fromisoformat(value) if value else None
            else:
                result[key] = value

        return result

    async def _ensure_indexes(self, token: str, token_data: Dict[str, Any]):
        """Ensure all indexes are properly maintained."""
        async with self.redis.pipeline(transaction=True) as pipe:
            user_tokens_key = self.USER_TOKENS_KEY.format(user_id=token_data["user_id"])
            expiry = (
                token_data["token_expires"].timestamp()
                if isinstance(token_data["token_expires"], datetime)
                else datetime.fromisoformat(token_data["token_expires"]).timestamp()
            )

            # Update user index
            await pipe.zadd(user_tokens_key, {token: expiry})

            # Update expiry index
            await pipe.zadd(self.EXPIRY_KEY, {token: expiry})

            # Update pending/used sets
            if token_data["is_used"]:
                await pipe.srem(self.PENDING_KEY, token)
                await pipe.sadd(self.USED_KEY, token)
            else:
                await pipe.sadd(self.PENDING_KEY, token)
                await pipe.srem(self.USED_KEY, token)

            try:
                await pipe.execute()
            except RedisError as e:
                self.logger.error(f"Failed to maintain indexes for token {token}: {e}")
