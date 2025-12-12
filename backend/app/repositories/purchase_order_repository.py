from typing import Optional, List, Tuple, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm import selectinload, joinedload
from models import PurchaseOrder, PurchaseOrderItem
from datetime import datetime, timedelta
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class PurchaseOrderRepository:
    """Repository for PurchaseOrder model operations."""

    def __init__(self, db_manager: Any):
        """
        Initialize repository with database manager.

        Args:
            db_manager: DatabaseManager instance for session management
        """
        self.db_manager = db_manager

    async def create(self, **kwargs) -> PurchaseOrder:
        """
        Create a new purchase order.

        Args:
            **kwargs: PurchaseOrder attributes

        Returns:
            PurchaseOrder: Created purchase order instance

        Raises:
            ValueError: If required fields are missing
        """
        async for session in self.db_manager.get_session():
            try:
                purchase_order = PurchaseOrder(**kwargs)
                session.add(purchase_order)
                await session.commit()
                await session.refresh(purchase_order)
                return purchase_order
            except Exception as e:
                await session.rollback()
                logger.error(f"Error creating purchase order: {e}")
                raise

    async def get(self, id: Any) -> Optional[PurchaseOrder]:
        """
        Get a purchase order by ID.

        Args:
            id: PurchaseOrder ID

        Returns:
            Optional[PurchaseOrder]: Purchase order if found, None otherwise
        """
        async for session in self.db_manager.get_session():
            try:
                stmt = select(PurchaseOrder).where(PurchaseOrder.id == id)
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
            except Exception as e:
                logger.error(f"Error getting purchase order by ID {id}: {e}")
                return None

    async def get_all(self, *, skip: int = 0, limit: int = 100) -> List[PurchaseOrder]:
        """
        Get all purchase orders with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[PurchaseOrder]: List of purchase orders
        """
        async for session in self.db_manager.get_session():
            try:
                stmt = select(PurchaseOrder).offset(skip).limit(limit)
                result = await session.execute(stmt)
                return list(result.scalars().all())
            except Exception as e:
                logger.error(f"Error getting all purchase orders: {e}")
                return []

    async def update(self, id: Any, **kwargs) -> Optional[PurchaseOrder]:
        """
        Update a purchase order by ID.

        Args:
            id: PurchaseOrder ID
            **kwargs: Attributes to update

        Returns:
            Optional[PurchaseOrder]: Updated purchase order if found, None otherwise
        """
        async for session in self.db_manager.get_session():
            try:
                purchase_order = await self.get(id)
                if not purchase_order:
                    return None

                for key, value in kwargs.items():
                    if hasattr(purchase_order, key):
                        setattr(purchase_order, key, value)

                await session.commit()
                await session.refresh(purchase_order)
                return purchase_order
            except Exception as e:
                await session.rollback()
                logger.error(f"Error updating purchase order {id}: {e}")
                return None

    async def delete(self, id: Any) -> bool:
        """
        Delete a purchase order by ID.

        Args:
            id: PurchaseOrder ID

        Returns:
            bool: True if deleted, False otherwise
        """
        async for session in self.db_manager.get_session():
            try:
                purchase_order = await self.get(id)
                if not purchase_order:
                    return False

                await session.delete(purchase_order)
                await session.commit()
                return True
            except Exception as e:
                await session.rollback()
                logger.error(f"Error deleting purchase order {id}: {e}")
                return False

    async def get_by_po_number(self, po_number: str) -> Optional[PurchaseOrder]:
        """
        Get a purchase order by PO number.

        Args:
            po_number: Purchase order number

        Returns:
            Optional[PurchaseOrder]: Purchase order if found, None otherwise
        """
        async for session in self.db_manager.get_session():
            try:
                stmt = select(PurchaseOrder).where(PurchaseOrder.po_number == po_number)
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
            except Exception as e:
                logger.error(
                    f"Error getting purchase order by PO number {po_number}: {e}"
                )
                return None

    async def filter_by_supplier(
        self, supplier_id: int, *, skip: int = 0, limit: int = 100
    ) -> List[PurchaseOrder]:
        """
        Filter purchase orders by supplier.

        Args:
            supplier_id: Supplier ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[PurchaseOrder]: List of purchase orders for specified supplier
        """
        async for session in self.db_manager.get_session():
            try:
                stmt = (
                    select(PurchaseOrder)
                    .where(PurchaseOrder.supplier_id == supplier_id)
                    .offset(skip)
                    .limit(limit)
                )
                result = await session.execute(stmt)
                return list(result.scalars().all())
            except Exception as e:
                logger.error(
                    f"Error filtering purchase orders by supplier {supplier_id}: {e}"
                )
                return []

    async def filter_by_status(
        self, status: str, *, skip: int = 0, limit: int = 100
    ) -> List[PurchaseOrder]:
        """
        Filter purchase orders by status.

        Args:
            status: Order status
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[PurchaseOrder]: List of purchase orders with specified status
        """
        async for session in self.db_manager.get_session():
            try:
                stmt = (
                    select(PurchaseOrder)
                    .where(PurchaseOrder.status == status)
                    .offset(skip)
                    .limit(limit)
                )
                result = await session.execute(stmt)
                return list(result.scalars().all())
            except Exception as e:
                logger.error(f"Error filtering purchase orders by status {status}: {e}")
                return []

    async def filter_by_created_by(
        self, user_id: int, *, skip: int = 0, limit: int = 100
    ) -> List[PurchaseOrder]:
        """
        Filter purchase orders by creator.

        Args:
            user_id: User ID who created the order
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[PurchaseOrder]: List of purchase orders created by specified user
        """
        async for session in self.db_manager.get_session():
            try:
                stmt = (
                    select(PurchaseOrder)
                    .where(PurchaseOrder.created_by == user_id)
                    .offset(skip)
                    .limit(limit)
                )
                result = await session.execute(stmt)
                return list(result.scalars().all())
            except Exception as e:
                logger.error(
                    f"Error filtering purchase orders by creator {user_id}: {e}"
                )
                return []

    async def filter_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[PurchaseOrder]:
        """
        Filter purchase orders by ordered date range.

        Args:
            start_date: Start date
            end_date: End date
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[PurchaseOrder]: List of purchase orders within date range
        """
        async for session in self.db_manager.get_session():
            try:
                stmt = (
                    select(PurchaseOrder)
                    .where(
                        and_(
                            PurchaseOrder.ordered_date >= start_date,
                            PurchaseOrder.ordered_date <= end_date,
                        )
                    )
                    .offset(skip)
                    .limit(limit)
                )
                result = await session.execute(stmt)
                return list(result.scalars().all())
            except Exception as e:
                logger.error(f"Error filtering purchase orders by date range: {e}")
                return []

    async def filter_by_amount_range(
        self,
        min_amount: Decimal,
        max_amount: Decimal,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[PurchaseOrder]:
        """
        Filter purchase orders by total amount range.

        Args:
            min_amount: Minimum total amount
            max_amount: Maximum total amount
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[PurchaseOrder]: List of purchase orders in amount range
        """
        async for session in self.db_manager.get_session():
            try:
                stmt = (
                    select(PurchaseOrder)
                    .where(
                        and_(
                            PurchaseOrder.total_amount >= min_amount,
                            PurchaseOrder.total_amount <= max_amount,
                        )
                    )
                    .offset(skip)
                    .limit(limit)
                )
                result = await session.execute(stmt)
                return list(result.scalars().all())
            except Exception as e:
                logger.error(f"Error filtering purchase orders by amount range: {e}")
                return []

    async def get_or_create(
        self, defaults: Optional[dict] = None, **kwargs
    ) -> Tuple[PurchaseOrder, bool]:
        """
        Get a purchase order or create if it doesn't exist.

        Args:
            defaults: Default values for creation
            **kwargs: Criteria for lookup

        Returns:
            Tuple[PurchaseOrder, bool]: (Purchase order instance, created flag)
        """
        async for session in self.db_manager.get_session():
            try:
                if "po_number" in kwargs:
                    purchase_order = await self.get_by_po_number(kwargs["po_number"])
                    if purchase_order:
                        return purchase_order, False

                create_data = {**kwargs, **(defaults or {})}
                purchase_order = await self.create(**create_data)
                return purchase_order, True
            except Exception as e:
                logger.error(f"Error in get_or_create for purchase order: {e}")
                raise

    async def update_or_create(
        self, criteria: dict, updates: dict
    ) -> Tuple[PurchaseOrder, bool]:
        """
        Update a purchase order or create if it doesn't exist.

        Args:
            criteria: Criteria for lookup
            updates: Values to update/create

        Returns:
            Tuple[PurchaseOrder, bool]: (Purchase order instance, created flag)
        """
        async for session in self.db_manager.get_session():
            try:
                if "po_number" in criteria:
                    purchase_order = await self.get_by_po_number(criteria["po_number"])
                else:
                    # Try to find by any criteria
                    conditions = [
                        getattr(PurchaseOrder, key) == value
                        for key, value in criteria.items()
                    ]
                    stmt = select(PurchaseOrder).where(and_(*conditions))
                    result = await session.execute(stmt)
                    purchase_order = result.scalar_one_or_none()

                if purchase_order:
                    # Update existing
                    for key, value in updates.items():
                        if hasattr(purchase_order, key):
                            setattr(purchase_order, key, value)
                    await session.commit()
                    await session.refresh(purchase_order)
                    return purchase_order, False
                else:
                    # Create new
                    purchase_order_data = {**criteria, **updates}
                    purchase_order = await self.create(**purchase_order_data)
                    return purchase_order, True
            except Exception as e:
                await session.rollback()
                logger.error(f"Error in update_or_create for purchase order: {e}")
                raise

    async def get_with_supplier(self, id: Any) -> Optional[PurchaseOrder]:
        """
        Get a purchase order with its supplier loaded.

        Args:
            id: PurchaseOrder ID

        Returns:
            Optional[PurchaseOrder]: Purchase order with supplier if found
        """
        async for session in self.db_manager.get_session():
            try:
                stmt = (
                    select(PurchaseOrder)
                    .options(selectinload(PurchaseOrder.supplier))
                    .where(PurchaseOrder.id == id)
                )
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
            except Exception as e:
                logger.error(f"Error getting purchase order with supplier {id}: {e}")
                return None

    async def get_with_creator(self, id: Any) -> Optional[PurchaseOrder]:
        """
        Get a purchase order with its creator loaded.

        Args:
            id: PurchaseOrder ID

        Returns:
            Optional[PurchaseOrder]: Purchase order with creator if found
        """
        async for session in self.db_manager.get_session():
            try:
                stmt = (
                    select(PurchaseOrder)
                    .options(selectinload(PurchaseOrder.creator))
                    .where(PurchaseOrder.id == id)
                )
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
            except Exception as e:
                logger.error(f"Error getting purchase order with creator {id}: {e}")
                return None

    async def get_with_items(self, id: Any) -> Optional[PurchaseOrder]:
        """
        Get a purchase order with its items loaded.

        Args:
            id: PurchaseOrder ID

        Returns:
            Optional[PurchaseOrder]: Purchase order with items if found
        """
        async for session in self.db_manager.get_session():
            try:
                stmt = (
                    select(PurchaseOrder)
                    .options(selectinload(PurchaseOrder.items))
                    .where(PurchaseOrder.id == id)
                )
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
            except Exception as e:
                logger.error(f"Error getting purchase order with items {id}: {e}")
                return None

    async def get_with_full_details(self, id: Any) -> Optional[PurchaseOrder]:
        """
        Get a purchase order with all related data loaded.

        Args:
            id: PurchaseOrder ID

        Returns:
            Optional[PurchaseOrder]: Purchase order with full details if found
        """
        async for session in self.db_manager.get_session():
            try:
                stmt = (
                    select(PurchaseOrder)
                    .options(
                        selectinload(PurchaseOrder.supplier),
                        selectinload(PurchaseOrder.creator),
                        selectinload(PurchaseOrder.items).selectinload(
                            PurchaseOrderItem.product
                        ),
                    )
                    .where(PurchaseOrder.id == id)
                )
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
            except Exception as e:
                logger.error(
                    f"Error getting purchase order with full details {id}: {e}"
                )
                return None

    async def get_pending_deliveries(
        self, *, skip: int = 0, limit: int = 100
    ) -> List[PurchaseOrder]:
        """
        Get purchase orders with pending deliveries.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[PurchaseOrder]: List of pending delivery purchase orders
        """
        async for session in self.db_manager.get_session():
            try:
                stmt = (
                    select(PurchaseOrder)
                    .where(PurchaseOrder.status.in_(["draft", "ordered"]))
                    .order_by(PurchaseOrder.expected_delivery_date.asc())
                    .offset(skip)
                    .limit(limit)
                )
                result = await session.execute(stmt)
                return list(result.scalars().all())
            except Exception as e:
                logger.error(f"Error getting pending deliveries: {e}")
                return []

    async def get_overdue_deliveries(
        self, *, skip: int = 0, limit: int = 100
    ) -> List[PurchaseOrder]:
        """
        Get purchase orders with overdue deliveries.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[PurchaseOrder]: List of overdue delivery purchase orders
        """
        async for session in self.db_manager.get_session():
            try:
                today = datetime.utcnow()
                stmt = (
                    select(PurchaseOrder)
                    .where(
                        and_(
                            PurchaseOrder.status == "ordered",
                            PurchaseOrder.expected_delivery_date < today,
                        )
                    )
                    .order_by(PurchaseOrder.expected_delivery_date.asc())
                    .offset(skip)
                    .limit(limit)
                )
                result = await session.execute(stmt)
                return list(result.scalars().all())
            except Exception as e:
                logger.error(f"Error getting overdue deliveries: {e}")
                return []

    async def update_status(self, id: int, status: str) -> Optional[PurchaseOrder]:
        """
        Update purchase order status.

        Args:
            id: PurchaseOrder ID
            status: New status

        Returns:
            Optional[PurchaseOrder]: Updated purchase order if found
        """
        async for session in self.db_manager.get_session():
            try:
                purchase_order = await self.get(id)
                if not purchase_order:
                    return None

                purchase_order.status = status

                if status == "received" and not purchase_order.received_date:
                    purchase_order.received_date = datetime.utcnow()

                await session.commit()
                await session.refresh(purchase_order)
                return purchase_order
            except Exception as e:
                await session.rollback()
                logger.error(f"Error updating purchase order status {id}: {e}")
                return None

    async def calculate_total_amount(self, id: int) -> Optional[Decimal]:
        """
        Calculate and update total amount for a purchase order.

        Args:
            id: PurchaseOrder ID

        Returns:
            Optional[Decimal]: Updated total amount if found
        """
        async for session in self.db_manager.get_session():
            try:
                # Calculate sum of line totals
                stmt = select(func.sum(PurchaseOrderItem.line_total)).where(
                    PurchaseOrderItem.purchase_order_id == id
                )
                result = await session.execute(stmt)
                total_amount = result.scalar() or Decimal("0")

                # Update the purchase order
                purchase_order = await self.get(id)
                if purchase_order:
                    purchase_order.total_amount = total_amount
                    await session.commit()
                    await session.refresh(purchase_order)

                return total_amount
            except Exception as e:
                await session.rollback()
                logger.error(
                    f"Error calculating total amount for purchase order {id}: {e}"
                )
                return None

    async def get_monthly_summary(self, year: int, month: int) -> dict:
        """
        Get monthly purchase order summary.

        Args:
            year: Year
            month: Month

        Returns:
            dict: Monthly summary statistics
        """
        async for session in self.db_manager.get_session():
            try:
                start_date = datetime(year, month, 1)
                if month == 12:
                    end_date = datetime(year + 1, 1, 1)
                else:
                    end_date = datetime(year, month + 1, 1)

                stmt = select(
                    func.count(PurchaseOrder.id).label("total_orders"),
                    func.sum(PurchaseOrder.total_amount).label("total_amount"),
                    func.count(func.distinct(PurchaseOrder.supplier_id)).label(
                        "unique_suppliers"
                    ),
                ).where(
                    and_(
                        PurchaseOrder.ordered_date >= start_date,
                        PurchaseOrder.ordered_date < end_date,
                    )
                )

                result = await session.execute(stmt)
                summary = result.fetchone()

                return {
                    "year": year,
                    "month": month,
                    "total_orders": summary.total_orders or 0,
                    "total_amount": summary.total_amount or Decimal("0"),
                    "unique_suppliers": summary.unique_suppliers or 0,
                }
            except Exception as e:
                logger.error(f"Error getting monthly summary: {e}")
                return {
                    "year": year,
                    "month": month,
                    "total_orders": 0,
                    "total_amount": Decimal("0"),
                    "unique_suppliers": 0,
                }
