from typing import Optional, List, Tuple, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from app.models import PurchaseOrderItem
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class PurchaseOrderItemRepository:
    """Repository for PurchaseOrderItem model operations."""

    __slots__ = ()

    async def create(self, session: AsyncSession, **kwargs) -> PurchaseOrderItem:
        """
        Create a new purchase order item.

        Args:
            session: Async database session
            **kwargs: PurchaseOrderItem attributes

        Returns:
            PurchaseOrderItem: Created purchase order item instance

        Raises:
            ValueError: If required fields are missing
        """
        try:
            item = PurchaseOrderItem(**kwargs)
            session.add(item)
            await session.commit()
            await session.refresh(item)
            return item
        except Exception as e:
            await session.rollback()
            logger.error(f"Error creating purchase order item: {e}")
            raise

    async def get(self, session: AsyncSession, id: Any) -> Optional[PurchaseOrderItem]:
        """
        Get a purchase order item by ID.

        Args:
            session: Async database session
            id: PurchaseOrderItem ID

        Returns:
            Optional[PurchaseOrderItem]: Purchase order item if found, None otherwise
        """
        try:
            stmt = select(PurchaseOrderItem).where(PurchaseOrderItem.id == id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting purchase order item by ID {id}: {e}")
            return None

    async def get_all(
        self, session: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[PurchaseOrderItem]:
        """
        Get all purchase order items with pagination.

        Args:
            session: Async database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[PurchaseOrderItem]: List of purchase order items
        """
        try:
            stmt = select(PurchaseOrderItem).offset(skip).limit(limit)
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting all purchase order items: {e}")
            return []

    async def update(
        self, session: AsyncSession, id: Any, **kwargs
    ) -> Optional[PurchaseOrderItem]:
        """
        Update a purchase order item by ID.

        Args:
            session: Async database session
            id: PurchaseOrderItem ID
            **kwargs: Attributes to update

        Returns:
            Optional[PurchaseOrderItem]: Updated purchase order item if found, None otherwise
        """
        try:
            item = await self.get(session, id)
            if not item:
                return None

            for key, value in kwargs.items():
                if hasattr(item, key):
                    setattr(item, key, value)

            # Recalculate line total if quantity or unit cost changed
            if "quantity_ordered" in kwargs or "unit_cost" in kwargs:
                item.line_total = item.quantity_ordered * item.unit_cost

            await session.commit()
            await session.refresh(item)
            return item
        except Exception as e:
            await session.rollback()
            logger.error(f"Error updating purchase order item {id}: {e}")
            return None

    async def delete(self, session: AsyncSession, id: Any) -> bool:
        """
        Delete a purchase order item by ID.

        Args:
            session: Async database session
            id: PurchaseOrderItem ID

        Returns:
            bool: True if deleted, False otherwise
        """
        try:
            item = await self.get(session, id)
            if not item:
                return False

            await session.delete(item)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            logger.error(f"Error deleting purchase order item {id}: {e}")
            return False

    async def get_by_purchase_order_and_product(
        self, session: AsyncSession, purchase_order_id: int, product_id: int
    ) -> Optional[PurchaseOrderItem]:
        """
        Get a purchase order item by purchase order and product.

        Args:
            session: Async database session
            purchase_order_id: Purchase order ID
            product_id: Product ID

        Returns:
            Optional[PurchaseOrderItem]: Purchase order item if found, None otherwise
        """
        try:
            stmt = select(PurchaseOrderItem).where(
                and_(
                    PurchaseOrderItem.purchase_order_id == purchase_order_id,
                    PurchaseOrderItem.product_id == product_id,
                )
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(
                f"Error getting purchase order item by PO {purchase_order_id} and product {product_id}: {e}"
            )
            return None

    async def filter_by_purchase_order(
        self,
        session: AsyncSession,
        purchase_order_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[PurchaseOrderItem]:
        """
        Filter purchase order items by purchase order.

        Args:
            session: Async database session
            purchase_order_id: Purchase order ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[PurchaseOrderItem]: List of items for specified purchase order
        """
        try:
            stmt = (
                select(PurchaseOrderItem)
                .where(PurchaseOrderItem.purchase_order_id == purchase_order_id)
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(
                f"Error filtering purchase order items by purchase order {purchase_order_id}: {e}"
            )
            return []

    async def filter_by_product(
        self, session: AsyncSession, product_id: int, *, skip: int = 0, limit: int = 100
    ) -> List[PurchaseOrderItem]:
        """
        Filter purchase order items by product.

        Args:
            session: Async database session
            product_id: Product ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[PurchaseOrderItem]: List of items for specified product
        """
        try:
            stmt = (
                select(PurchaseOrderItem)
                .where(PurchaseOrderItem.product_id == product_id)
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(
                f"Error filtering purchase order items by product {product_id}: {e}"
            )
            return []

    async def filter_by_quantity_ordered(
        self,
        session: AsyncSession,
        min_quantity: int = 0,
        max_quantity: Optional[int] = None,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[PurchaseOrderItem]:
        """
        Filter purchase order items by ordered quantity range.

        Args:
            session: Async database session
            min_quantity: Minimum ordered quantity
            max_quantity: Maximum ordered quantity (optional)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[PurchaseOrderItem]: List of items in ordered quantity range
        """
        try:
            conditions = [PurchaseOrderItem.quantity_ordered >= min_quantity]
            if max_quantity is not None:
                conditions.append(PurchaseOrderItem.quantity_ordered <= max_quantity)

            stmt = (
                select(PurchaseOrderItem)
                .where(and_(*conditions))
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(
                f"Error filtering purchase order items by ordered quantity: {e}"
            )
            return []

    async def filter_by_unit_cost(
        self,
        session: AsyncSession,
        min_cost: Decimal,
        max_cost: Decimal,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[PurchaseOrderItem]:
        """
        Filter purchase order items by unit cost range.

        Args:
            session: Async database session
            min_cost: Minimum unit cost
            max_cost: Maximum unit cost
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[PurchaseOrderItem]: List of items in unit cost range
        """
        try:
            stmt = (
                select(PurchaseOrderItem)
                .where(
                    and_(
                        PurchaseOrderItem.unit_cost >= min_cost,
                        PurchaseOrderItem.unit_cost <= max_cost,
                    )
                )
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error filtering purchase order items by unit cost: {e}")
            return []

    async def get_or_create(
        self, session: AsyncSession, defaults: Optional[dict] = None, **kwargs
    ) -> Tuple[PurchaseOrderItem, bool]:
        """
        Get a purchase order item or create if it doesn't exist.

        Args:
            session: Async database session
            defaults: Default values for creation
            **kwargs: Criteria for lookup

        Returns:
            Tuple[PurchaseOrderItem, bool]: (Purchase order item instance, created flag)
        """
        try:
            if "purchase_order_id" in kwargs and "product_id" in kwargs:
                item = await self.get_by_purchase_order_and_product(
                    session, kwargs["purchase_order_id"], kwargs["product_id"]
                )
                if item:
                    return item, False

            create_data = {**kwargs, **(defaults or {})}
            item = await self.create(session, **create_data)
            return item, True
        except Exception as e:
            logger.error(f"Error in get_or_create for purchase order item: {e}")
            raise

    async def update_or_create(
        self, session: AsyncSession, criteria: dict, updates: dict
    ) -> Tuple[PurchaseOrderItem, bool]:
        """
        Update a purchase order item or create if it doesn't exist.

        Args:
            session: Async database session
            criteria: Criteria for lookup
            updates: Values to update/create

        Returns:
            Tuple[PurchaseOrderItem, bool]: (Purchase order item instance, created flag)
        """
        try:
            if "purchase_order_id" in criteria and "product_id" in criteria:
                item = await self.get_by_purchase_order_and_product(
                    session, criteria["purchase_order_id"], criteria["product_id"]
                )
            else:
                # Try to find by any criteria
                conditions = [
                    getattr(PurchaseOrderItem, key) == value
                    for key, value in criteria.items()
                ]
                stmt = select(PurchaseOrderItem).where(and_(*conditions))
                result = await session.execute(stmt)
                item = result.scalar_one_or_none()

            if item:
                # Update existing
                for key, value in updates.items():
                    if hasattr(item, key):
                        setattr(item, key, value)

                # Recalculate line total if quantity or unit cost changed
                if "quantity_ordered" in updates or "unit_cost" in updates:
                    item.line_total = item.quantity_ordered * item.unit_cost

                await session.commit()
                await session.refresh(item)
                return item, False
            else:
                # Create new
                item_data = {**criteria, **updates}
                # Calculate line total if not provided
                if (
                    "line_total" not in item_data
                    and "quantity_ordered" in item_data
                    and "unit_cost" in item_data
                ):
                    item_data["line_total"] = (
                        item_data["quantity_ordered"] * item_data["unit_cost"]
                    )

                item = await self.create(session, **item_data)
                return item, True
        except Exception as e:
            await session.rollback()
            logger.error(f"Error in update_or_create for purchase order item: {e}")
            raise

    async def get_with_purchase_order(
        self, session: AsyncSession, id: Any
    ) -> Optional[PurchaseOrderItem]:
        """
        Get a purchase order item with its purchase order loaded.

        Args:
            session: Async database session
            id: PurchaseOrderItem ID

        Returns:
            Optional[PurchaseOrderItem]: Purchase order item with purchase order if found
        """
        try:
            stmt = (
                select(PurchaseOrderItem)
                .options(selectinload(PurchaseOrderItem.purchase_order))
                .where(PurchaseOrderItem.id == id)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(
                f"Error getting purchase order item with purchase order {id}: {e}"
            )
            return None

    async def get_with_product(
        self, session: AsyncSession, id: Any
    ) -> Optional[PurchaseOrderItem]:
        """
        Get a purchase order item with its product loaded.

        Args:
            session: Async database session
            id: PurchaseOrderItem ID

        Returns:
            Optional[PurchaseOrderItem]: Purchase order item with product if found
        """
        try:
            stmt = (
                select(PurchaseOrderItem)
                .options(selectinload(PurchaseOrderItem.product))
                .where(PurchaseOrderItem.id == id)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting purchase order item with product {id}: {e}")
            return None

    async def update_received_quantity(
        self, session: AsyncSession, id: int, quantity_received: int
    ) -> Optional[PurchaseOrderItem]:
        """
        Update received quantity for a purchase order item.

        Args:
            session: Async database session
            id: PurchaseOrderItem ID
            quantity_received: Quantity received

        Returns:
            Optional[PurchaseOrderItem]: Updated purchase order item if found
        """
        try:
            item = await self.get(session, id)
            if not item:
                return None

            item.quantity_received = quantity_received
            await session.commit()
            await session.refresh(item)
            return item
        except Exception as e:
            await session.rollback()
            logger.error(
                f"Error updating received quantity for purchase order item {id}: {e}"
            )
            return None

    async def get_partially_received_items(
        self, session: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[PurchaseOrderItem]:
        """
        Get purchase order items that are partially received.

        Args:
            session: Async database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[PurchaseOrderItem]: List of partially received items
        """
        try:
            stmt = (
                select(PurchaseOrderItem)
                .where(
                    and_(
                        PurchaseOrderItem.quantity_received > 0,
                        PurchaseOrderItem.quantity_received
                        < PurchaseOrderItem.quantity_ordered,
                    )
                )
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting partially received items: {e}")
            return []

    async def get_fully_received_items(
        self, session: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[PurchaseOrderItem]:
        """
        Get purchase order items that are fully received.

        Args:
            session: Async database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[PurchaseOrderItem]: List of fully received items
        """
        try:
            stmt = (
                select(PurchaseOrderItem)
                .where(
                    PurchaseOrderItem.quantity_received
                    == PurchaseOrderItem.quantity_ordered
                )
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting fully received items: {e}")
            return []

    async def get_product_purchase_history(
        self, session: AsyncSession, product_id: int, *, skip: int = 0, limit: int = 100
    ) -> List[PurchaseOrderItem]:
        """
        Get purchase history for a specific product.

        Args:
            session: Async database session
            product_id: Product ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[PurchaseOrderItem]: List of purchase history items
        """
        try:
            stmt = (
                select(PurchaseOrderItem)
                .where(PurchaseOrderItem.product_id == product_id)
                .order_by(PurchaseOrderItem.created_at.desc())
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(
                f"Error getting product purchase history for product {product_id}: {e}"
            )
            return []

    async def calculate_product_total_spend(
        self, session: AsyncSession, product_id: int
    ) -> Decimal:
        """
        Calculate total spend on a specific product.

        Args:
            session: Async database session
            product_id: Product ID

        Returns:
            Decimal: Total spend
        """
        try:
            stmt = select(func.sum(PurchaseOrderItem.line_total)).where(
                PurchaseOrderItem.product_id == product_id
            )
            result = await session.execute(stmt)
            total_spend = result.scalar() or Decimal("0")
            return total_spend
        except Exception as e:
            logger.error(f"Error calculating total spend for product {product_id}: {e}")
            return Decimal("0")

    async def get_items_with_product_details(
        self, session: AsyncSession, purchase_order_id: int
    ) -> List[PurchaseOrderItem]:
        """
        Get all items for a purchase order with product details loaded.

        Args:
            session: Async database session
            purchase_order_id: Purchase order ID

        Returns:
            List[PurchaseOrderItem]: List of items with product details
        """
        try:
            stmt = (
                select(PurchaseOrderItem)
                .options(selectinload(PurchaseOrderItem.product))
                .where(PurchaseOrderItem.purchase_order_id == purchase_order_id)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(
                f"Error getting items with product details for PO {purchase_order_id}: {e}"
            )
            return []
