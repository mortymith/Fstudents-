from typing import Optional, List, Tuple, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from sqlalchemy.orm import selectinload
from app.models import StockMovement
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class StockMovementRepository:
    """Repository for StockMovement model operations."""

    __slots__ = ()

    async def create(self, session: AsyncSession, **kwargs) -> StockMovement:
        """
        Create a new stock movement.

        Args:
            session: Async database session
            **kwargs: StockMovement attributes

        Returns:
            StockMovement: Created stock movement instance

        Raises:
            ValueError: If required fields are missing
        """
        try:
            stock_movement = StockMovement(**kwargs)
            session.add(stock_movement)
            await session.commit()
            await session.refresh(stock_movement)
            return stock_movement
        except Exception as e:
            await session.rollback()
            logger.error(f"Error creating stock movement: {e}")
            raise

    async def get(self, session: AsyncSession, id: Any) -> Optional[StockMovement]:
        """
        Get a stock movement by ID.

        Args:
            session: Async database session
            id: StockMovement ID

        Returns:
            Optional[StockMovement]: Stock movement if found, None otherwise
        """
        try:
            stmt = select(StockMovement).where(StockMovement.id == id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting stock movement by ID {id}: {e}")
            return None

    async def get_all(
        self, session: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[StockMovement]:
        """
        Get all stock movements with pagination.

        Args:
            session: Async database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[StockMovement]: List of stock movements
        """
        try:
            stmt = select(StockMovement).offset(skip).limit(limit)
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting all stock movements: {e}")
            return []

    async def update(
        self, session: AsyncSession, id: Any, **kwargs
    ) -> Optional[StockMovement]:
        """
        Update a stock movement by ID.

        Args:
            session: Async database session
            id: StockMovement ID
            **kwargs: Attributes to update

        Returns:
            Optional[StockMovement]: Updated stock movement if found, None otherwise
        """
        try:
            stock_movement = await self.get(session, id)
            if not stock_movement:
                return None

            for key, value in kwargs.items():
                if hasattr(stock_movement, key):
                    setattr(stock_movement, key, value)

            await session.commit()
            await session.refresh(stock_movement)
            return stock_movement
        except Exception as e:
            await session.rollback()
            logger.error(f"Error updating stock movement {id}: {e}")
            return None

    async def delete(self, session: AsyncSession, id: Any) -> bool:
        """
        Delete a stock movement by ID.

        Args:
            session: Async database session
            id: StockMovement ID

        Returns:
            bool: True if deleted, False otherwise
        """
        try:
            stock_movement = await self.get(session, id)
            if not stock_movement:
                return False

            await session.delete(stock_movement)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            logger.error(f"Error deleting stock movement {id}: {e}")
            return False

    async def get_by_product_id(
        self, session: AsyncSession, product_id: int
    ) -> Optional[StockMovement]:
        """
        Get first stock movement by product ID.

        Args:
            session: Async database session
            product_id: Product ID

        Returns:
            Optional[StockMovement]: Stock movement if found, None otherwise
        """
        try:
            stmt = select(StockMovement).where(StockMovement.product_id == product_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(
                f"Error getting stock movement by product ID {product_id}: {e}"
            )
            return None

    async def filter_by_product(
        self, session: AsyncSession, product_id: int, *, skip: int = 0, limit: int = 100
    ) -> List[StockMovement]:
        """
        Filter stock movements by product.

        Args:
            session: Async database session
            product_id: Product ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[StockMovement]: List of stock movements for specified product
        """
        try:
            stmt = (
                select(StockMovement)
                .where(StockMovement.product_id == product_id)
                .order_by(desc(StockMovement.movement_date))
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(
                f"Error filtering stock movements by product {product_id}: {e}"
            )
            return []

    async def filter_by_movement_type(
        self,
        session: AsyncSession,
        movement_type: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[StockMovement]:
        """
        Filter stock movements by movement type.

        Args:
            session: Async database session
            movement_type: Movement type ('in', 'out', 'adjustment')
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[StockMovement]: List of stock movements with specified type
        """
        try:
            stmt = (
                select(StockMovement)
                .where(StockMovement.movement_type == movement_type)
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(
                f"Error filtering stock movements by type {movement_type}: {e}"
            )
            return []

    async def filter_by_creator(
        self, session: AsyncSession, created_by: int, *, skip: int = 0, limit: int = 100
    ) -> List[StockMovement]:
        """
        Filter stock movements by creator.

        Args:
            session: Async database session
            created_by: User ID who created the movement
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[StockMovement]: List of stock movements created by specified user
        """
        try:
            stmt = (
                select(StockMovement)
                .where(StockMovement.created_by == created_by)
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(
                f"Error filtering stock movements by creator {created_by}: {e}"
            )
            return []

    async def filter_by_reference(
        self,
        session: AsyncSession,
        reference_type: str,
        reference_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[StockMovement]:
        """
        Filter stock movements by reference.

        Args:
            session: Async database session
            reference_type: Reference type
            reference_id: Reference ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[StockMovement]: List of stock movements with specified reference
        """
        try:
            stmt = (
                select(StockMovement)
                .where(
                    and_(
                        StockMovement.reference_type == reference_type,
                        StockMovement.reference_id == reference_id,
                    )
                )
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(
                f"Error filtering stock movements by reference {reference_type}/{reference_id}: {e}"
            )
            return []

    async def filter_by_date_range(
        self,
        session: AsyncSession,
        start_date: datetime,
        end_date: datetime,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[StockMovement]:
        """
        Filter stock movements by date range.

        Args:
            session: Async database session
            start_date: Start date
            end_date: End date
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[StockMovement]: List of stock movements within date range
        """
        try:
            stmt = (
                select(StockMovement)
                .where(
                    and_(
                        StockMovement.movement_date >= start_date,
                        StockMovement.movement_date <= end_date,
                    )
                )
                .order_by(desc(StockMovement.movement_date))
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error filtering stock movements by date range: {e}")
            return []

    async def filter_by_quantity_change(
        self,
        session: AsyncSession,
        min_change: int,
        max_change: Optional[int] = None,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[StockMovement]:
        """
        Filter stock movements by quantity change range.

        Args:
            session: Async database session
            min_change: Minimum quantity change
            max_change: Maximum quantity change (optional)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[StockMovement]: List of stock movements in quantity change range
        """
        try:
            conditions = [StockMovement.quantity_change >= min_change]
            if max_change is not None:
                conditions.append(StockMovement.quantity_change <= max_change)

            stmt = (
                select(StockMovement).where(and_(*conditions)).offset(skip).limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error filtering stock movements by quantity change: {e}")
            return []

    async def get_or_create(
        self, session: AsyncSession, defaults: Optional[dict] = None, **kwargs
    ) -> Tuple[StockMovement, bool]:
        """
        Get a stock movement or create if it doesn't exist.

        Args:
            session: Async database session
            defaults: Default values for creation
            **kwargs: Criteria for lookup

        Returns:
            Tuple[StockMovement, bool]: (Stock movement instance, created flag)
        """
        try:
            # For stock movements, we typically don't want to get_or_create
            # as each movement should be unique. So we'll just create.
            create_data = {**kwargs, **(defaults or {})}
            stock_movement = await self.create(session, **create_data)
            return stock_movement, True
        except Exception as e:
            logger.error(f"Error in get_or_create for stock movement: {e}")
            raise

    async def update_or_create(
        self, session: AsyncSession, criteria: dict, updates: dict
    ) -> Tuple[StockMovement, bool]:
        """
        Update a stock movement or create if it doesn't exist.

        Args:
            session: Async database session
            criteria: Criteria for lookup
            updates: Values to update/create

        Returns:
            Tuple[StockMovement, bool]: (Stock movement instance, created flag)
        """
        try:
            # Try to find by any criteria
            conditions = [
                getattr(StockMovement, key) == value for key, value in criteria.items()
            ]
            stmt = select(StockMovement).where(and_(*conditions))
            result = await session.execute(stmt)
            stock_movement = result.scalar_one_or_none()

            if stock_movement:
                # Update existing
                for key, value in updates.items():
                    if hasattr(stock_movement, key):
                        setattr(stock_movement, key, value)
                await session.commit()
                await session.refresh(stock_movement)
                return stock_movement, False
            else:
                # Create new
                stock_movement_data = {**criteria, **updates}
                stock_movement = await self.create(session, **stock_movement_data)
                return stock_movement, True
        except Exception as e:
            await session.rollback()
            logger.error(f"Error in update_or_create for stock movement: {e}")
            raise

    async def get_with_product(
        self, session: AsyncSession, id: Any
    ) -> Optional[StockMovement]:
        """
        Get a stock movement with its product loaded.

        Args:
            session: Async database session
            id: StockMovement ID

        Returns:
            Optional[StockMovement]: Stock movement with product if found
        """
        try:
            stmt = (
                select(StockMovement)
                .options(selectinload(StockMovement.product))
                .where(StockMovement.id == id)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting stock movement with product {id}: {e}")
            return None

    async def get_with_creator(
        self, session: AsyncSession, id: Any
    ) -> Optional[StockMovement]:
        """
        Get a stock movement with its creator loaded.

        Args:
            session: Async database session
            id: StockMovement ID

        Returns:
            Optional[StockMovement]: Stock movement with creator if found
        """
        try:
            stmt = (
                select(StockMovement)
                .options(selectinload(StockMovement.creator))
                .where(StockMovement.id == id)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting stock movement with creator {id}: {e}")
            return None

    async def get_recent_movements(
        self, session: AsyncSession, days: int = 7, *, skip: int = 0, limit: int = 100
    ) -> List[StockMovement]:
        """
        Get recent stock movements within specified days.

        Args:
            session: Async database session
            days: Number of days
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[StockMovement]: List of recent stock movements
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            stmt = (
                select(StockMovement)
                .where(StockMovement.movement_date >= cutoff_date)
                .order_by(desc(StockMovement.movement_date))
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting recent movements: {e}")
            return []

    async def get_product_movement_history(
        self, session: AsyncSession, product_id: int, days: int = 30
    ) -> List[StockMovement]:
        """
        Get movement history for a specific product.

        Args:
            session: Async database session
            product_id: Product ID
            days: Number of days of history

        Returns:
            List[StockMovement]: List of movement history
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            stmt = (
                select(StockMovement)
                .where(
                    and_(
                        StockMovement.product_id == product_id,
                        StockMovement.movement_date >= cutoff_date,
                    )
                )
                .order_by(desc(StockMovement.movement_date))
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(
                f"Error getting product movement history for product {product_id}: {e}"
            )
            return []

    async def get_daily_movement_summary(
        self, session: AsyncSession, date: datetime
    ) -> dict:
        """
        Get daily stock movement summary.

        Args:
            session: Async database session
            date: Date for summary

        Returns:
            dict: Daily movement summary
        """
        try:
            start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)

            # Get total movements
            stmt_total = select(
                func.count(StockMovement.id).label("total_movements"),
                func.sum(StockMovement.quantity_change).label("net_quantity_change"),
            ).where(
                and_(
                    StockMovement.movement_date >= start_date,
                    StockMovement.movement_date < end_date,
                )
            )

            result_total = await session.execute(stmt_total)
            total_summary = result_total.fetchone()

            # Get movement type breakdown
            stmt_breakdown = (
                select(
                    StockMovement.movement_type,
                    func.count(StockMovement.id).label("count"),
                    func.sum(StockMovement.quantity_change).label("total_quantity"),
                )
                .where(
                    and_(
                        StockMovement.movement_date >= start_date,
                        StockMovement.movement_date < end_date,
                    )
                )
                .group_by(StockMovement.movement_type)
            )

            result_breakdown = await session.execute(stmt_breakdown)
            breakdown = {
                row.movement_type: {
                    "count": row.count,
                    "total_quantity": row.total_quantity,
                }
                for row in result_breakdown
            }

            return {
                "date": date.date(),
                "total_movements": total_summary.total_movements or 0,
                "net_quantity_change": total_summary.net_quantity_change or 0,
                "breakdown": breakdown,
            }
        except Exception as e:
            logger.error(f"Error getting daily movement summary: {e}")
            return {
                "date": date.date(),
                "total_movements": 0,
                "net_quantity_change": 0,
                "breakdown": {},
            }

    async def create_in_movement(
        self,
        session: AsyncSession,
        product_id: int,
        quantity_change: int,
        reference_type: str,
        reference_id: Optional[int],
        created_by: int,
        movement_date: Optional[datetime] = None,
    ) -> Optional[StockMovement]:
        """
        Create a stock movement for incoming stock.

        Args:
            session: Async database session
            product_id: Product ID
            quantity_change: Quantity change (positive)
            reference_type: Reference type
            reference_id: Reference ID
            created_by: User ID
            movement_date: Movement date (defaults to now)

        Returns:
            Optional[StockMovement]: Created stock movement
        """
        try:
            from app.repositories.product_inventory_repository import (
                ProductInventoryRepository,
            )

            if quantity_change <= 0:
                raise ValueError("Quantity change for 'in' movement must be positive")

            # Get current inventory
            inventory_repo = ProductInventoryRepository()
            inventory = await inventory_repo.get_by_product_id(session, product_id)
            if not inventory:
                raise ValueError(f"No inventory found for product {product_id}")

            quantity_before = inventory.quantity_on_hand
            quantity_after = quantity_before + quantity_change

            movement = await self.create(
                session,
                product_id=product_id,
                movement_type="in",
                quantity_change=quantity_change,
                quantity_before=quantity_before,
                quantity_after=quantity_after,
                reference_type=reference_type,
                reference_id=reference_id,
                movement_date=movement_date or datetime.utcnow(),
                created_by=created_by,
            )

            # Update inventory
            await inventory_repo.update_quantity(
                session, product_id, quantity_change, commit=False
            )

            await session.commit()
            return movement
        except Exception as e:
            await session.rollback()
            logger.error(f"Error creating in movement for product {product_id}: {e}")
            return None

    async def create_out_movement(
        self,
        session: AsyncSession,
        product_id: int,
        quantity_change: int,
        reference_type: str,
        reference_id: Optional[int],
        created_by: int,
        movement_date: Optional[datetime] = None,
    ) -> Optional[StockMovement]:
        """
        Create a stock movement for outgoing stock.

        Args:
            session: Async database session
            product_id: Product ID
            quantity_change: Quantity change (negative)
            reference_type: Reference type
            reference_id: Reference ID
            created_by: User ID
            movement_date: Movement date (defaults to now)

        Returns:
            Optional[StockMovement]: Created stock movement
        """
        try:
            from app.repositories.product_inventory_repository import (
                ProductInventoryRepository,
            )

            if quantity_change >= 0:
                raise ValueError("Quantity change for 'out' movement must be negative")

            # Get current inventory
            inventory_repo = ProductInventoryRepository()
            inventory = await inventory_repo.get_by_product_id(session, product_id)
            if not inventory:
                raise ValueError(f"No inventory found for product {product_id}")

            quantity_before = inventory.quantity_on_hand
            quantity_after = (
                quantity_before + quantity_change
            )  # quantity_change is negative

            if quantity_after < 0:
                raise ValueError(
                    f"Insufficient stock for product {product_id}. Available: {quantity_before}, Requested: {-quantity_change}"
                )

            movement = await self.create(
                session,
                product_id=product_id,
                movement_type="out",
                quantity_change=quantity_change,
                quantity_before=quantity_before,
                quantity_after=quantity_after,
                reference_type=reference_type,
                reference_id=reference_id,
                movement_date=movement_date or datetime.utcnow(),
                created_by=created_by,
            )

            # Update inventory
            await inventory_repo.update_quantity(
                session, product_id, quantity_change, commit=False
            )

            await session.commit()
            return movement
        except Exception as e:
            await session.rollback()
            logger.error(f"Error creating out movement for product {product_id}: {e}")
            return None
