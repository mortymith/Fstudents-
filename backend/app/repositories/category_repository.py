from typing import Optional, List, Tuple, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from models import Category
import logging

logger = logging.getLogger(__name__)


class CategoryRepository:
    """Repository for Category model operations."""

    __slots__ = ()

    async def create(self, session: AsyncSession, **kwargs) -> Category:
        """
        Create a new category.

        Args:
            session: Async database session
            **kwargs: Category attributes

        Returns:
            Category: Created category instance

        Raises:
            ValueError: If required fields are missing
        """
        try:
            category = Category(**kwargs)
            session.add(category)
            await session.commit()
            await session.refresh(category)
            return category
        except Exception as e:
            await session.rollback()
            logger.error(f"Error creating category: {e}")
            raise

    async def get(self, session: AsyncSession, id: Any) -> Optional[Category]:
        """
        Get a category by ID.

        Args:
            session: Async database session
            id: Category ID

        Returns:
            Optional[Category]: Category if found, None otherwise
        """
        try:
            stmt = select(Category).where(Category.id == id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting category by ID {id}: {e}")
            return None

    async def get_all(
        self, session: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Category]:
        """
        Get all categories with pagination.

        Args:
            session: Async database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Category]: List of categories
        """
        try:
            stmt = select(Category).offset(skip).limit(limit)
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting all categories: {e}")
            return []

    async def update(
        self, session: AsyncSession, id: Any, **kwargs
    ) -> Optional[Category]:
        """
        Update a category by ID.

        Args:
            session: Async database session
            id: Category ID
            **kwargs: Attributes to update

        Returns:
            Optional[Category]: Updated category if found, None otherwise
        """
        try:
            category = await self.get(session, id)
            if not category:
                return None

            for key, value in kwargs.items():
                if hasattr(category, key):
                    setattr(category, key, value)

            await session.commit()
            await session.refresh(category)
            return category
        except Exception as e:
            await session.rollback()
            logger.error(f"Error updating category {id}: {e}")
            return None

    async def delete(self, session: AsyncSession, id: Any) -> bool:
        """
        Delete a category by ID.

        Args:
            session: Async database session
            id: Category ID

        Returns:
            bool: True if deleted, False otherwise
        """
        try:
            category = await self.get(session, id)
            if not category:
                return False

            await session.delete(category)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            logger.error(f"Error deleting category {id}: {e}")
            return False

    async def get_by_name(self, session: AsyncSession, name: str) -> Optional[Category]:
        """
        Get a category by name.

        Args:
            session: Async database session
            name: Category name

        Returns:
            Optional[Category]: Category if found, None otherwise
        """
        try:
            stmt = select(Category).where(Category.name == name)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting category by name {name}: {e}")
            return None

    async def filter_by_active_status(
        self, session: AsyncSession, is_active: bool, *, skip: int = 0, limit: int = 100
    ) -> List[Category]:
        """
        Filter categories by active status.

        Args:
            session: Async database session
            is_active: Active status
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Category]: List of categories with specified active status
        """
        try:
            stmt = (
                select(Category)
                .where(Category.is_active == is_active)
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(
                f"Error filtering categories by active status {is_active}: {e}"
            )
            return []

    async def filter_by_parent_id(
        self,
        session: AsyncSession,
        parent_id: Optional[int],
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Category]:
        """
        Filter categories by parent ID.

        Args:
            session: Async database session
            parent_id: Parent category ID (None for root categories)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Category]: List of categories with specified parent
        """
        try:
            if parent_id is None:
                stmt = (
                    select(Category)
                    .where(Category.parent_id.is_(None))
                    .offset(skip)
                    .limit(limit)
                )
            else:
                stmt = (
                    select(Category)
                    .where(Category.parent_id == parent_id)
                    .offset(skip)
                    .limit(limit)
                )

            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error filtering categories by parent ID {parent_id}: {e}")
            return []

    async def get_or_create(
        self, session: AsyncSession, defaults: Optional[dict] = None, **kwargs
    ) -> Tuple[Category, bool]:
        """
        Get a category or create if it doesn't exist.

        Args:
            session: Async database session
            defaults: Default values for creation
            **kwargs: Criteria for lookup

        Returns:
            Tuple[Category, bool]: (Category instance, created flag)
        """
        try:
            if "name" in kwargs:
                category = await self.get_by_name(session, kwargs["name"])
                if category:
                    return category, False

            create_data = {**kwargs, **(defaults or {})}
            category = await self.create(session, **create_data)
            return category, True
        except Exception as e:
            logger.error(f"Error in get_or_create for category: {e}")
            raise

    async def update_or_create(
        self, session: AsyncSession, criteria: dict, updates: dict
    ) -> Tuple[Category, bool]:
        """
        Update a category or create if it doesn't exist.

        Args:
            session: Async database session
            criteria: Criteria for lookup
            updates: Values to update/create

        Returns:
            Tuple[Category, bool]: (Category instance, created flag)
        """
        try:
            if "name" in criteria:
                category = await self.get_by_name(session, criteria["name"])
            else:
                # Try to find by any criteria
                conditions = [
                    getattr(Category, key) == value for key, value in criteria.items()
                ]
                stmt = select(Category).where(and_(*conditions))
                result = await session.execute(stmt)
                category = result.scalar_one_or_none()

            if category:
                # Update existing
                for key, value in updates.items():
                    if hasattr(category, key):
                        setattr(category, key, value)
                await session.commit()
                await session.refresh(category)
                return category, False
            else:
                # Create new
                category_data = {**criteria, **updates}
                category = await self.create(session, **category_data)
                return category, True
        except Exception as e:
            await session.rollback()
            logger.error(f"Error in update_or_create for category: {e}")
            raise

    async def get_with_children(
        self, session: AsyncSession, id: Any
    ) -> Optional[Category]:
        """
        Get a category with its children loaded.

        Args:
            session: Async database session
            id: Category ID

        Returns:
            Optional[Category]: Category with children if found
        """
        try:
            stmt = (
                select(Category)
                .options(selectinload(Category.children))
                .where(Category.id == id)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting category with children {id}: {e}")
            return None

    async def get_with_parent(
        self, session: AsyncSession, id: Any
    ) -> Optional[Category]:
        """
        Get a category with its parent loaded.

        Args:
            session: Async database session
            id: Category ID

        Returns:
            Optional[Category]: Category with parent if found
        """
        try:
            stmt = (
                select(Category)
                .options(selectinload(Category.parent))
                .where(Category.id == id)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting category with parent {id}: {e}")
            return None

    async def get_with_products(
        self, session: AsyncSession, id: Any
    ) -> Optional[Category]:
        """
        Get a category with its products loaded.

        Args:
            session: Async database session
            id: Category ID

        Returns:
            Optional[Category]: Category with products if found
        """
        try:
            stmt = (
                select(Category)
                .options(selectinload(Category.products))
                .where(Category.id == id)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting category with products {id}: {e}")
            return None

    async def get_hierarchy(self, session: AsyncSession, id: Any) -> Optional[Category]:
        """
        Get a category with full hierarchy (parent and children).

        Args:
            session: Async database session
            id: Category ID

        Returns:
            Optional[Category]: Category with hierarchy if found
        """
        try:
            stmt = (
                select(Category)
                .options(selectinload(Category.parent), selectinload(Category.children))
                .where(Category.id == id)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting category hierarchy {id}: {e}")
            return None

    async def get_root_categories(
        self, session: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Category]:
        """
        Get all root categories (categories without parent).

        Args:
            session: Async database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Category]: List of root categories
        """
        try:
            stmt = (
                select(Category)
                .where(Category.parent_id.is_(None))
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting root categories: {e}")
            return []

    async def get_active_categories_tree(self, session: AsyncSession) -> List[Category]:
        """
        Get all active categories with their children (tree structure).

        Args:
            session: Async database session

        Returns:
            List[Category]: List of active root categories with children
        """
        try:
            stmt = (
                select(Category)
                .options(selectinload(Category.children))
                .where(and_(Category.parent_id.is_(None), Category.is_active))
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting active categories tree: {e}")
            return []
