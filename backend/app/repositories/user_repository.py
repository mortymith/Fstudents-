from typing import Optional, List, Tuple, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from ..models import User
import logging

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository for User model operations."""
    
    __slots__ = ()
    
    async def create(self, session: AsyncSession, **kwargs) -> User:
        """
        Create a new user.
        
        Args:
            session: Async database session
            **kwargs: User attributes
        
        Returns:
            User: Created user instance
        
        Raises:
            ValueError: If required fields are missing
        """
        try:
            user = User(**kwargs)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
        except Exception as e:
            await session.rollback()
            logger.error(f"Error creating user: {e}")
            raise
    
    async def get(self, session: AsyncSession, id: Any) -> Optional[User]:
        """
        Get a user by ID.
        
        Args:
            session: Async database session
            id: User ID
        
        Returns:
            Optional[User]: User if found, None otherwise
        """
        try:
            stmt = select(User).where(User.id == id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user by ID {id}: {e}")
            return None
    
    async def get_all(self, session: AsyncSession, *, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get all users with pagination.
        
        Args:
            session: Async database session
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List[User]: List of users
        """
        try:
            stmt = select(User).offset(skip).limit(limit)
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    async def update(self, session: AsyncSession, id: Any, **kwargs) -> Optional[User]:
        """
        Update a user by ID.
        
        Args:
            session: Async database session
            id: User ID
            **kwargs: Attributes to update
        
        Returns:
            Optional[User]: Updated user if found, None otherwise
        """
        try:
            user = await self.get(session, id)
            if not user:
                return None
            
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            await session.commit()
            await session.refresh(user)
            return user
        except Exception as e:
            await session.rollback()
            logger.error(f"Error updating user {id}: {e}")
            return None
    
    async def delete(self, session: AsyncSession, id: Any) -> bool:
        """
        Delete a user by ID.
        
        Args:
            session: Async database session
            id: User ID
        
        Returns:
            bool: True if deleted, False otherwise
        """
        try:
            user = await self.get(session, id)
            if not user:
                return False
            
            await session.delete(user)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            logger.error(f"Error deleting user {id}: {e}")
            return False
    
    async def get_by_email(self, session: AsyncSession, email: str) -> Optional[User]:
        """
        Get a user by email.
        
        Args:
            session: Async database session
            email: User email
        
        Returns:
            Optional[User]: User if found, None otherwise
        """
        try:
            stmt = select(User).where(User.email == email)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None
    
    async def get_by_role(self, session: AsyncSession, role: str) -> Optional[User]:
        """
        Get first user by role.
        
        Args:
            session: Async database session
            role: User role
        
        Returns:
            Optional[User]: User if found, None otherwise
        """
        try:
            stmt = select(User).where(User.role == role)
            result = await session.execute(stmt)
            return result.first()
        except Exception as e:
            logger.error(f"Error getting user by role {role}: {e}")
            return None
    
    async def filter_by_role(self, session: AsyncSession, role: str, *, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Filter users by role.
        
        Args:
            session: Async database session
            role: User role
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List[User]: List of users with specified role
        """
        try:
            stmt = select(User).where(User.role == role).offset(skip).limit(limit)
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error filtering users by role {role}: {e}")
            return []
    
    async def filter_by_active_status(self, session: AsyncSession, is_active: bool, *, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Filter users by active status.
        
        Args:
            session: Async database session
            is_active: Active status
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List[User]: List of users with specified active status
        """
        try:
            stmt = select(User).where(User.is_active == is_active).offset(skip).limit(limit)
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error filtering users by active status {is_active}: {e}")
            return []
    
    async def get_or_create(self, session: AsyncSession, defaults: Optional[dict] = None, **kwargs) -> Tuple[User, bool]:
        """
        Get a user or create if it doesn't exist.
        
        Args:
            session: Async database session
            defaults: Default values for creation
            **kwargs: Criteria for lookup
        
        Returns:
            Tuple[User, bool]: (User instance, created flag)
        """
        try:
            user = await self.get_by_email(session, kwargs.get('email', ''))
            if user:
                return user, False
            
            create_data = {**kwargs, **(defaults or {})}
            user = await self.create(session, **create_data)
            return user, True
        except Exception as e:
            logger.error(f"Error in get_or_create for user: {e}")
            raise
    
    async def update_or_create(self, session: AsyncSession, criteria: dict, updates: dict) -> Tuple[User, bool]:
        """
        Update a user or create if it doesn't exist.
        
        Args:
            session: Async database session
            criteria: Criteria for lookup
            updates: Values to update/create
        
        Returns:
            Tuple[User, bool]: (User instance, created flag)
        """
        try:
            if 'email' in criteria:
                user = await self.get_by_email(session, criteria['email'])
            else:
                # Try to find by any criteria
                conditions = [getattr(User, key) == value for key, value in criteria.items()]
                stmt = select(User).where(and_(*conditions))
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()
            
            if user:
                # Update existing
                for key, value in updates.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
                await session.commit()
                await session.refresh(user)
                return user, False
            else:
                # Create new
                user_data = {**criteria, **updates}
                user = await self.create(session, **user_data)
                return user, True
        except Exception as e:
            await session.rollback()
            logger.error(f"Error in update_or_create for user: {e}")
            raise
    
    async def get_with_purchase_orders(self, session: AsyncSession, id: Any) -> Optional[User]:
        """
        Get a user with their purchase orders loaded.
        
        Args:
            session: Async database session
            id: User ID
        
        Returns:
            Optional[User]: User with purchase orders if found
        """
        try:
            stmt = select(User).options(selectinload(User.created_purchase_orders)).where(User.id == id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user with purchase orders {id}: {e}")
            return None
    
    async def get_with_stock_movements(self, session: AsyncSession, id: Any) -> Optional[User]:
        """
        Get a user with their stock movements loaded.
        
        Args:
            session: Async database session
            id: User ID
        
        Returns:
            Optional[User]: User with stock movements if found
        """
        try:
            stmt = select(User).options(selectinload(User.stock_movements)).where(User.id == id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user with stock movements {id}: {e}")
            return None
    
    async def get_with_stock_adjustments(self, session: AsyncSession, id: Any) -> Optional[User]:
        """
        Get a user with their stock adjustments loaded.
        
        Args:
            session: Async database session
            id: User ID
        
        Returns:
            Optional[User]: User with stock adjustments if found
        """
        try:
            stmt = select(User).options(selectinload(User.stock_adjustments)).where(User.id == id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user with stock adjustments {id}: {e}")
            return None
    
    async def get_active_users_by_role(self, session: AsyncSession, role: str, *, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get active users by role.
        
        Args:
            session: Async database session
            role: User role
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List[User]: List of active users with specified role
        """
        try:
            stmt = (
                select(User)
                .where(and_(User.role == role, User.is_active))
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting active users by role {role}: {e}")
            return []
    
    async def get_users_with_recent_login(self, session: AsyncSession, days: int = 7, *, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get users with recent login within specified days.
        
        Args:
            session: Async database session
            days: Number of days
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List[User]: List of users with recent login
        """
        try:
            from datetime import datetime, timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            stmt = (
                select(User)
                .where(and_(User.last_login_at >= cutoff_date, User.is_active))
                .order_by(User.last_login_at.desc())
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting users with recent login: {e}")
            return []