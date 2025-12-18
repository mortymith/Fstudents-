from typing import Optional, List, Tuple, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from sqlalchemy.orm import selectinload
from app.models import StockAdjustment
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class StockAdjustmentRepository:
    """Repository for StockAdjustment model operations."""

    __slots__ = ()

    async def create(self, session: AsyncSession, **kwargs) -> StockAdjustment:
        """
        Create a new stock adjustment.

        Args:
            session: Async database session
            **kwargs: StockAdjustment attributes

        Returns:
            StockAdjustment: Created stock adjustment instance

        Raises:
            ValueError: If required fields are missing
        """
        try:
            adjustment = StockAdjustment(**kwargs)
            session.add(adjustment)
            await session.commit()
            await session.refresh(adjustment)
            return adjustment
        except Exception as e:
            await session.rollback()
            logger.error(f"Error creating stock adjustment: {e}")
            raise

    async def get(self, session: AsyncSession, id: Any) -> Optional[StockAdjustment]:
        """
        Get a stock adjustment by ID.

        Args:
            session: Async database session
            id: StockAdjustment ID

        Returns:
            Optional[StockAdjustment]: Stock adjustment if found, None otherwise
        """
        try:
            stmt = select(StockAdjustment).where(StockAdjustment.id == id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting stock adjustment by ID {id}: {e}")
            return None

    async def get_all(
        self, session: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[StockAdjustment]:
        """
        Get all stock adjustments with pagination.

        Args:
            session: Async database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[StockAdjustment]: List of stock adjustments
        """
        try:
            stmt = select(StockAdjustment).offset(skip).limit(limit)
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting all stock adjustments: {e}")
            return []

    async def update(
        self, session: AsyncSession, id: Any, **kwargs
    ) -> Optional[StockAdjustment]:
        """
        Update a stock adjustment by ID.

        Args:
            session: Async database session
            id: StockAdjustment ID
            **kwargs: Attributes to update

        Returns:
            Optional[StockAdjustment]: Updated stock adjustment if found, None otherwise
        """
        try:
            adjustment = await self.get(session, id)
            if not adjustment:
                return None

            for key, value in kwargs.items():
                if hasattr(adjustment, key):
                    setattr(adjustment, key, value)

            await session.commit()
            await session.refresh(adjustment)
            return adjustment
        except Exception as e:
            await session.rollback()
            logger.error(f"Error updating stock adjustment {id}: {e}")
            return None

    async def delete(self, session: AsyncSession, id: Any) -> bool:
        """
        Delete a stock adjustment by ID.

        Args:
            session: Async database session
            id: StockAdjustment ID

        Returns:
            bool: True if deleted, False otherwise
        """
        try:
            adjustment = await self.get(session, id)
            if not adjustment:
                return False

            await session.delete(adjustment)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            logger.error(f"Error deleting stock adjustment {id}: {e}")
            return False

    async def get_by_product_id(
        self, session: AsyncSession, product_id: int
    ) -> Optional[StockAdjustment]:
        """
        Get first stock adjustment by product ID.

        Args:
            session: Async database session
            product_id: Product ID

        Returns:
            Optional[StockAdjustment]: Stock adjustment if found, None otherwise
        """
        try:
            stmt = select(StockAdjustment).where(
                StockAdjustment.product_id == product_id
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(
                f"Error getting stock adjustment by product ID {product_id}: {e}"
            )
            return None

    async def filter_by_product(
        self, session: AsyncSession, product_id: int, *, skip: int = 0, limit: int = 100
    ) -> List[StockAdjustment]:
        """
        Filter stock adjustments by product.

        Args:
            session: Async database session
            product_id: Product ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[StockAdjustment]: List of stock adjustments for specified product
        """
        try:
            stmt = (
                select(StockAdjustment)
                .where(StockAdjustment.product_id == product_id)
                .order_by(desc(StockAdjustment.adjustment_date))
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(
                f"Error filtering stock adjustments by product {product_id}: {e}"
            )
            return []

    async def filter_by_adjustment_type(
        self,
        session: AsyncSession,
        adjustment_type: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[StockAdjustment]:
        """
        Filter stock adjustments by adjustment type.

        Args:
            session: Async database session
            adjustment_type: Adjustment type
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[StockAdjustment]: List of stock adjustments with specified type
        """
        try:
            stmt = (
                select(StockAdjustment)
                .where(StockAdjustment.adjustment_type == adjustment_type)
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(
                f"Error filtering stock adjustments by type {adjustment_type}: {e}"
            )
            return []

    async def filter_by_creator(
        self, session: AsyncSession, created_by: int, *, skip: int = 0, limit: int = 100
    ) -> List[StockAdjustment]:
        """
        Filter stock adjustments by creator.

        Args:
            session: Async database session
            created_by: User ID who created the adjustment
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[StockAdjustment]: List of stock adjustments created by specified user
        """
        try:
            stmt = (
                select(StockAdjustment)
                .where(StockAdjustment.created_by == created_by)
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(
                f"Error filtering stock adjustments by creator {created_by}: {e}"
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
    ) -> List[StockAdjustment]:
        """
        Filter stock adjustments by date range.

        Args:
            session: Async database session
            start_date: Start date
            end_date: End date
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[StockAdjustment]: List of stock adjustments within date range
        """
        try:
            stmt = (
                select(StockAdjustment)
                .where(
                    and_(
                        StockAdjustment.adjustment_date >= start_date,
                        StockAdjustment.adjustment_date <= end_date,
                    )
                )
                .order_by(desc(StockAdjustment.adjustment_date))
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error filtering stock adjustments by date range: {e}")
            return []

    async def filter_by_quantity_adjusted(
        self,
        session: AsyncSession,
        min_quantity: int,
        max_quantity: Optional[int] = None,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[StockAdjustment]:
        """
        Filter stock adjustments by adjusted quantity range.

        Args:
            session: Async database session
            min_quantity: Minimum adjusted quantity (absolute value)
            max_quantity: Maximum adjusted quantity (absolute value, optional)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[StockAdjustment]: List of stock adjustments in adjusted quantity range
        """
        try:
            conditions = [func.abs(StockAdjustment.quantity_adjusted) >= min_quantity]
            if max_quantity is not None:
                conditions.append(
                    func.abs(StockAdjustment.quantity_adjusted) <= max_quantity
                )

            stmt = (
                select(StockAdjustment)
                .where(and_(*conditions))
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error filtering stock adjustments by adjusted quantity: {e}")
            return []

    async def get_or_create(
        self, session: AsyncSession, defaults: Optional[dict] = None, **kwargs
    ) -> Tuple[StockAdjustment, bool]:
        """
        Get a stock adjustment or create if it doesn't exist.

        Args:
            session: Async database session
            defaults: Default values for creation
            **kwargs: Criteria for lookup

        Returns:
            Tuple[StockAdjustment, bool]: (Stock adjustment instance, created flag)
        """
        try:
            # For stock adjustments, we typically don't want to get_or_create
            # as each adjustment should be unique. So we'll just create.
            create_data = {**kwargs, **(defaults or {})}
            adjustment = await self.create(session, **create_data)
            return adjustment, True
        except Exception as e:
            logger.error(f"Error in get_or_create for stock adjustment: {e}")
            raise

    async def update_or_create(
        self, session: AsyncSession, criteria: dict, updates: dict
    ) -> Tuple[StockAdjustment, bool]:
        """
        Update a stock adjustment or create if it doesn't exist.

        Args:
            session: Async database session
            criteria: Criteria for lookup
            updates: Values to update/create

        Returns:
            Tuple[StockAdjustment, bool]: (Stock adjustment instance, created flag)
        """
        try:
            # Try to find by any criteria
            conditions = [
                getattr(StockAdjustment, key) == value
                for key, value in criteria.items()
            ]
            stmt = select(StockAdjustment).where(and_(*conditions))
            result = await session.execute(stmt)
            adjustment = result.scalar_one_or_none()

            if adjustment:
                # Update existing
                for key, value in updates.items():
                    if hasattr(adjustment, key):
                        setattr(adjustment, key, value)
                await session.commit()
                await session.refresh(adjustment)
                return adjustment, False
            else:
                # Create new
                adjustment_data = {**criteria, **updates}
                adjustment = await self.create(session, **adjustment_data)
                return adjustment, True
        except Exception as e:
            await session.rollback()
            logger.error(f"Error in update_or_create for stock adjustment: {e}")
            raise

    async def get_with_product(
        self, session: AsyncSession, id: Any
    ) -> Optional[StockAdjustment]:
        """
        Get a stock adjustment with its product loaded.

        Args:
            session: Async database session
            id: StockAdjustment ID

        Returns:
            Optional[StockAdjustment]: Stock adjustment with product if found
        """
        try:
            stmt = (
                select(StockAdjustment)
                .options(selectinload(StockAdjustment.product))
                .where(StockAdjustment.id == id)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting stock adjustment with product {id}: {e}")
            return None

    async def get_with_creator(
        self, session: AsyncSession, id: Any
    ) -> Optional[StockAdjustment]:
        """
        Get a stock adjustment with its creator loaded.

        Args:
            session: Async database session
            id: StockAdjustment ID

        Returns:
            Optional[StockAdjustment]: Stock adjustment with creator if found
        """
        try:
            stmt = (
                select(StockAdjustment)
                .options(selectinload(StockAdjustment.creator))
                .where(StockAdjustment.id == id)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting stock adjustment with creator {id}: {e}")
            return None

    async def get_recent_adjustments(
        self, session: AsyncSession, days: int = 7, *, skip: int = 0, limit: int = 100
    ) -> List[StockAdjustment]:
        """
        Get recent stock adjustments within specified days.

        Args:
            session: Async database session
            days: Number of days
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[StockAdjustment]: List of recent stock adjustments
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            stmt = (
                select(StockAdjustment)
                .where(StockAdjustment.adjustment_date >= cutoff_date)
                .order_by(desc(StockAdjustment.adjustment_date))
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting recent adjustments: {e}")
            return []

    async def get_product_adjustment_history(
        self, session: AsyncSession, product_id: int, days: int = 30
    ) -> List[StockAdjustment]:
        """
        Get adjustment history for a specific product.

        Args:
            session: Async database session
            product_id: Product ID
            days: Number of days of history

        Returns:
            List[StockAdjustment]: List of adjustment history
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            stmt = (
                select(StockAdjustment)
                .where(
                    and_(
                        StockAdjustment.product_id == product_id,
                        StockAdjustment.adjustment_date >= cutoff_date,
                    )
                )
                .order_by(desc(StockAdjustment.adjustment_date))
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(
                f"Error getting product adjustment history for product {product_id}: {e}"
            )
            return []

    async def create_damaged_adjustment(
        self,
        session: AsyncSession,
        product_id: int,
        quantity_adjusted: int,
        reason: str,
        created_by: int,
    ) -> Optional[StockAdjustment]:
        """
        Create a stock adjustment for damaged goods.

        Args:
            session: Async database session
            product_id: Product ID
            quantity_adjusted: Quantity adjusted (negative)
            reason: Reason for adjustment
            created_by: User ID

        Returns:
            Optional[StockAdjustment]: Created stock adjustment
        """
        try:
            return await self._create_adjustment_with_inventory_update(
                session, product_id, quantity_adjusted, "damaged", reason, created_by
            )
        except Exception as e:
            logger.error(
                f"Error creating damaged adjustment for product {product_id}: {e}"
            )
            return None

    async def create_expired_adjustment(
        self,
        session: AsyncSession,
        product_id: int,
        quantity_adjusted: int,
        reason: str,
        created_by: int,
    ) -> Optional[StockAdjustment]:
        """
        Create a stock adjustment for expired goods.

        Args:
            session: Async database session
            product_id: Product ID
            quantity_adjusted: Quantity adjusted (negative)
            reason: Reason for adjustment
            created_by: User ID

        Returns:
            Optional[StockAdjustment]: Created stock adjustment
        """
        try:
            return await self._create_adjustment_with_inventory_update(
                session, product_id, quantity_adjusted, "expired", reason, created_by
            )
        except Exception as e:
            logger.error(
                f"Error creating expired adjustment for product {product_id}: {e}"
            )
            return None

    async def create_returned_adjustment(
        self,
        session: AsyncSession,
        product_id: int,
        quantity_adjusted: int,
        reason: str,
        created_by: int,
    ) -> Optional[StockAdjustment]:
        """
        Create a stock adjustment for returned goods.

        Args:
            session: Async database session
            product_id: Product ID
            quantity_adjusted: Quantity adjusted (positive for returns to inventory)
            reason: Reason for adjustment
            created_by: User ID

        Returns:
            Optional[StockAdjustment]: Created stock adjustment
        """
        try:
            return await self._create_adjustment_with_inventory_update(
                session, product_id, quantity_adjusted, "returned", reason, created_by
            )
        except Exception as e:
            logger.error(
                f"Error creating returned adjustment for product {product_id}: {e}"
            )
            return None

    async def create_found_adjustment(
        self,
        session: AsyncSession,
        product_id: int,
        quantity_adjusted: int,
        reason: str,
        created_by: int,
    ) -> Optional[StockAdjustment]:
        """
        Create a stock adjustment for found goods.

        Args:
            session: Async database session
            product_id: Product ID
            quantity_adjusted: Quantity adjusted (positive)
            reason: Reason for adjustment
            created_by: User ID

        Returns:
            Optional[StockAdjustment]: Created stock adjustment
        """
        try:
            return await self._create_adjustment_with_inventory_update(
                session, product_id, quantity_adjusted, "found", reason, created_by
            )
        except Exception as e:
            logger.error(
                f"Error creating found adjustment for product {product_id}: {e}"
            )
            return None

    async def _create_adjustment_with_inventory_update(
        self,
        session: AsyncSession,
        product_id: int,
        quantity_adjusted: int,
        adjustment_type: str,
        reason: str,
        created_by: int,
    ) -> Optional[StockAdjustment]:
        """
        Internal method to create adjustment with inventory update.

        Args:
            session: Async database session
            product_id: Product ID
            quantity_adjusted: Quantity adjusted
            adjustment_type: Adjustment type
            reason: Reason for adjustment
            created_by: User ID

        Returns:
            Optional[StockAdjustment]: Created stock adjustment
        """
        try:
            from app.repositories.product_inventory_repository import (
                ProductInventoryRepository,
            )
            from app.repositories.stock_movement_repository import (
                StockMovementRepository,
            )

            # Get current inventory
            inventory_repo = ProductInventoryRepository()
            inventory = await inventory_repo.get_by_product_id(session, product_id)
            if not inventory:
                raise ValueError(f"No inventory found for product {product_id}")

            # Check if we have enough stock for negative adjustments
            if (
                quantity_adjusted < 0
                and inventory.quantity_on_hand + quantity_adjusted < 0
            ):
                raise ValueError(
                    f"Insufficient stock for adjustment. Available: {inventory.quantity_on_hand}, Adjustment: {quantity_adjusted}"
                )

            # Create the adjustment
            adjustment = await self.create(
                session,
                product_id=product_id,
                adjustment_type=adjustment_type,
                quantity_adjusted=quantity_adjusted,
                reason=reason,
                adjustment_date=datetime.utcnow(),
                created_by=created_by,
            )

            # Update inventory
            await inventory_repo.update_quantity(
                session, product_id, quantity_adjusted, commit=False
            )

            # Create corresponding stock movement
            movement_repo = StockMovementRepository()
            await movement_repo.create(
                session,
                product_id=product_id,
                movement_type="adjustment",
                quantity_change=quantity_adjusted,
                quantity_before=inventory.quantity_on_hand,
                quantity_after=inventory.quantity_on_hand + quantity_adjusted,
                reference_type="adjustment",
                reference_id=adjustment.id,
                movement_date=datetime.utcnow(),
                created_by=created_by,
            )

            await session.commit()
            return adjustment
        except Exception as e:
            await session.rollback()
            raise

    async def get_adjustment_summary_by_type(
        self, session: AsyncSession, start_date: datetime, end_date: datetime
    ) -> dict:
        """
        Get adjustment summary by type.

        Args:
            session: Async database session
            start_date: Start date
            end_date: End date

        Returns:
            dict: Adjustment summary by type
        """
        try:
            stmt = (
                select(
                    StockAdjustment.adjustment_type,
                    func.count(StockAdjustment.id).label("count"),
                    func.sum(StockAdjustment.quantity_adjusted).label("total_quantity"),
                )
                .where(
                    and_(
                        StockAdjustment.adjustment_date >= start_date,
                        StockAdjustment.adjustment_date <= end_date,
                    )
                )
                .group_by(StockAdjustment.adjustment_type)
            )

            result = await session.execute(stmt)

            summary = {}
            for row in result:
                summary[row.adjustment_type] = {
                    "count": row.count,
                    "total_quantity": row.total_quantity or 0,
                }

            return summary
        except Exception as e:
            logger.error(f"Error getting adjustment summary by type: {e}")
            return {}

    async def get_total_loss_value(
        self, session: AsyncSession, start_date: datetime, end_date: datetime
    ) -> dict:
        """
        Get total loss value from adjustments (damaged, expired, theft).

        Args:
            session: Async database session
            start_date: Start date
            end_date: End date

        Returns:
            dict: Total loss value summary
        """
        try:
            from app.models.product import Product

            # Join with products to get cost price
            stmt = (
                select(
                    StockAdjustment.adjustment_type,
                    func.sum(
                        StockAdjustment.quantity_adjusted * Product.cost_price
                    ).label("total_loss_value"),
                )
                .join(Product, StockAdjustment.product_id == Product.id)
                .where(
                    and_(
                        StockAdjustment.adjustment_date >= start_date,
                        StockAdjustment.adjustment_date <= end_date,
                        StockAdjustment.adjustment_type.in_(
                            ["damaged", "expired", "theft"]
                        ),
                        StockAdjustment.quantity_adjusted < 0,
                    )
                )
                .group_by(StockAdjustment.adjustment_type)
            )

            result = await session.execute(stmt)

            summary = {}
            total_loss = 0
            for row in result:
                loss_value = abs(row.total_loss_value or 0)
                summary[row.adjustment_type] = loss_value
                total_loss += loss_value

            return {"by_type": summary, "total_loss": total_loss}
        except Exception as e:
            logger.error(f"Error getting total loss value: {e}")
            return {"by_type": {}, "total_loss": 0}
