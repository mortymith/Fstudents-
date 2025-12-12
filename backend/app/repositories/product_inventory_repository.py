from typing import Optional, List, Tuple, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from models import ProductInventory
import logging

logger = logging.getLogger(__name__)


class ProductInventoryRepository:
    """Repository for ProductInventory model operations."""

    __slots__ = ()

    async def create(self, session: AsyncSession, **kwargs) -> ProductInventory:
        """
        Create a new product inventory record.

        Args:
            session: Async database session
            **kwargs: ProductInventory attributes

        Returns:
            ProductInventory: Created inventory instance

        Raises:
            ValueError: If required fields are missing
        """
        try:
            inventory = ProductInventory(**kwargs)
            session.add(inventory)
            await session.commit()
            await session.refresh(inventory)
            return inventory
        except Exception as e:
            await session.rollback()
            logger.error(f"Error creating product inventory: {e}")
            raise

    async def get(self, session: AsyncSession, id: Any) -> Optional[ProductInventory]:
        """
        Get a product inventory by ID.

        Args:
            session: Async database session
            id: ProductInventory ID

        Returns:
            Optional[ProductInventory]: Inventory if found, None otherwise
        """
        try:
            stmt = select(ProductInventory).where(ProductInventory.id == id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting product inventory by ID {id}: {e}")
            return None

    async def get_all(
        self, session: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ProductInventory]:
        """
        Get all product inventory records with pagination.

        Args:
            session: Async database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[ProductInventory]: List of inventory records
        """
        try:
            stmt = select(ProductInventory).offset(skip).limit(limit)
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting all product inventory: {e}")
            return []

    async def update(
        self, session: AsyncSession, id: Any, **kwargs
    ) -> Optional[ProductInventory]:
        """
        Update a product inventory by ID.

        Args:
            session: Async database session
            id: ProductInventory ID
            **kwargs: Attributes to update

        Returns:
            Optional[ProductInventory]: Updated inventory if found, None otherwise
        """
        try:
            inventory = await self.get(session, id)
            if not inventory:
                return None

            for key, value in kwargs.items():
                if hasattr(inventory, key):
                    setattr(inventory, key, value)

            await session.commit()
            await session.refresh(inventory)
            return inventory
        except Exception as e:
            await session.rollback()
            logger.error(f"Error updating product inventory {id}: {e}")
            return None

    async def delete(self, session: AsyncSession, id: Any) -> bool:
        """
        Delete a product inventory by ID.

        Args:
            session: Async database session
            id: ProductInventory ID

        Returns:
            bool: True if deleted, False otherwise
        """
        try:
            inventory = await self.get(session, id)
            if not inventory:
                return False

            await session.delete(inventory)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            logger.error(f"Error deleting product inventory {id}: {e}")
            return False

    async def get_by_product_id(
        self, session: AsyncSession, product_id: int
    ) -> Optional[ProductInventory]:
        """
        Get product inventory by product ID.

        Args:
            session: Async database session
            product_id: Product ID

        Returns:
            Optional[ProductInventory]: Inventory if found, None otherwise
        """
        try:
            stmt = select(ProductInventory).where(
                ProductInventory.product_id == product_id
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting inventory by product ID {product_id}: {e}")
            return None

    async def filter_by_available_quantity(
        self,
        session: AsyncSession,
        min_quantity: int = 0,
        max_quantity: Optional[int] = None,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ProductInventory]:
        """
        Filter inventory by available quantity range.

        Args:
            session: Async database session
            min_quantity: Minimum available quantity
            max_quantity: Maximum available quantity (optional)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[ProductInventory]: List of inventory records in quantity range
        """
        try:
            conditions = [ProductInventory.quantity_available >= min_quantity]
            if max_quantity is not None:
                conditions.append(ProductInventory.quantity_available <= max_quantity)

            stmt = (
                select(ProductInventory)
                .where(and_(*conditions))
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error filtering inventory by available quantity: {e}")
            return []

    async def filter_by_on_hand_quantity(
        self,
        session: AsyncSession,
        min_quantity: int = 0,
        max_quantity: Optional[int] = None,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ProductInventory]:
        """
        Filter inventory by on-hand quantity range.

        Args:
            session: Async database session
            min_quantity: Minimum on-hand quantity
            max_quantity: Maximum on-hand quantity (optional)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[ProductInventory]: List of inventory records in on-hand quantity range
        """
        try:
            conditions = [ProductInventory.quantity_on_hand >= min_quantity]
            if max_quantity is not None:
                conditions.append(ProductInventory.quantity_on_hand <= max_quantity)

            stmt = (
                select(ProductInventory)
                .where(and_(*conditions))
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error filtering inventory by on-hand quantity: {e}")
            return []

    async def get_low_stock_inventory(
        self,
        session: AsyncSession,
        threshold: int = 10,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ProductInventory]:
        """
        Get inventory records with low available stock.

        Args:
            session: Async database session
            threshold: Low stock threshold
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[ProductInventory]: List of low stock inventory records
        """
        try:
            stmt = (
                select(ProductInventory)
                .where(ProductInventory.quantity_available < threshold)
                .order_by(ProductInventory.quantity_available.asc())
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting low stock inventory: {e}")
            return []

    async def get_out_of_stock_inventory(
        self, session: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ProductInventory]:
        """
        Get inventory records that are out of stock.

        Args:
            session: Async database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[ProductInventory]: List of out of stock inventory records
        """
        try:
            stmt = (
                select(ProductInventory)
                .where(ProductInventory.quantity_available == 0)
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting out of stock inventory: {e}")
            return []

    async def get_or_create(
        self, session: AsyncSession, defaults: Optional[dict] = None, **kwargs
    ) -> Tuple[ProductInventory, bool]:
        """
        Get a product inventory or create if it doesn't exist.

        Args:
            session: Async database session
            defaults: Default values for creation
            **kwargs: Criteria for lookup

        Returns:
            Tuple[ProductInventory, bool]: (Inventory instance, created flag)
        """
        try:
            if "product_id" in kwargs:
                inventory = await self.get_by_product_id(session, kwargs["product_id"])
                if inventory:
                    return inventory, False

            create_data = {**kwargs, **(defaults or {})}
            inventory = await self.create(session, **create_data)
            return inventory, True
        except Exception as e:
            logger.error(f"Error in get_or_create for product inventory: {e}")
            raise

    async def update_or_create(
        self, session: AsyncSession, criteria: dict, updates: dict
    ) -> Tuple[ProductInventory, bool]:
        """
        Update a product inventory or create if it doesn't exist.

        Args:
            session: Async database session
            criteria: Criteria for lookup
            updates: Values to update/create

        Returns:
            Tuple[ProductInventory, bool]: (Inventory instance, created flag)
        """
        try:
            if "product_id" in criteria:
                inventory = await self.get_by_product_id(
                    session, criteria["product_id"]
                )
            else:
                # Try to find by any criteria
                conditions = [
                    getattr(ProductInventory, key) == value
                    for key, value in criteria.items()
                ]
                stmt = select(ProductInventory).where(and_(*conditions))
                result = await session.execute(stmt)
                inventory = result.scalar_one_or_none()

            if inventory:
                # Update existing
                for key, value in updates.items():
                    if hasattr(inventory, key):
                        setattr(inventory, key, value)
                await session.commit()
                await session.refresh(inventory)
                return inventory, False
            else:
                # Create new
                inventory_data = {**criteria, **updates}
                inventory = await self.create(session, **inventory_data)
                return inventory, True
        except Exception as e:
            await session.rollback()
            logger.error(f"Error in update_or_create for product inventory: {e}")
            raise

    async def get_with_product(
        self, session: AsyncSession, id: Any
    ) -> Optional[ProductInventory]:
        """
        Get a product inventory with its product loaded.

        Args:
            session: Async database session
            id: ProductInventory ID

        Returns:
            Optional[ProductInventory]: Inventory with product if found
        """
        try:
            stmt = (
                select(ProductInventory)
                .options(selectinload(ProductInventory.product))
                .where(ProductInventory.id == id)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting inventory with product {id}: {e}")
            return None

    async def update_quantity(
        self,
        session: AsyncSession,
        product_id: int,
        quantity_change: int,
        commit: bool = True,
    ) -> Optional[ProductInventory]:
        """
        Update product inventory quantity.

        Args:
            session: Async database session
            product_id: Product ID
            quantity_change: Quantity change (positive for increase, negative for decrease)
            commit: Whether to commit the transaction

        Returns:
            Optional[ProductInventory]: Updated inventory if found
        """
        try:
            inventory = await self.get_by_product_id(session, product_id)
            if not inventory:
                return None

            inventory.quantity_on_hand += quantity_change
            inventory.quantity_available = (
                inventory.quantity_on_hand - inventory.quantity_committed
            )

            if commit:
                await session.commit()
                await session.refresh(inventory)

            return inventory
        except Exception as e:
            if commit:
                await session.rollback()
            logger.error(
                f"Error updating inventory quantity for product {product_id}: {e}"
            )
            return None

    async def update_committed_quantity(
        self,
        session: AsyncSession,
        product_id: int,
        quantity_change: int,
        commit: bool = True,
    ) -> Optional[ProductInventory]:
        """
        Update committed quantity.

        Args:
            session: Async database session
            product_id: Product ID
            quantity_change: Committed quantity change
            commit: Whether to commit the transaction

        Returns:
            Optional[ProductInventory]: Updated inventory if found
        """
        try:
            inventory = await self.get_by_product_id(session, product_id)
            if not inventory:
                return None

            inventory.quantity_committed += quantity_change
            inventory.quantity_available = (
                inventory.quantity_on_hand - inventory.quantity_committed
            )

            if commit:
                await session.commit()
                await session.refresh(inventory)

            return inventory
        except Exception as e:
            if commit:
                await session.rollback()
            logger.error(
                f"Error updating committed quantity for product {product_id}: {e}"
            )
            return None

    async def update_restock_date(
        self, session: AsyncSession, product_id: int
    ) -> Optional[ProductInventory]:
        """
        Update last restocked date to current time.

        Args:
            session: Async database session
            product_id: Product ID

        Returns:
            Optional[ProductInventory]: Updated inventory if found
        """
        try:
            from datetime import datetime

            inventory = await self.get_by_product_id(session, product_id)
            if not inventory:
                return None

            inventory.last_restocked_at = datetime.utcnow()
            await session.commit()
            await session.refresh(inventory)
            return inventory
        except Exception as e:
            await session.rollback()
            logger.error(f"Error updating restock date for product {product_id}: {e}")
            return None

    async def update_count_date(
        self, session: AsyncSession, product_id: int
    ) -> Optional[ProductInventory]:
        """
        Update last counted date to current time.

        Args:
            session: Async database session
            product_id: Product ID

        Returns:
            Optional[ProductInventory]: Updated inventory if found
        """
        try:
            from datetime import datetime

            inventory = await self.get_by_product_id(session, product_id)
            if not inventory:
                return None

            inventory.last_counted_at = datetime.utcnow()
            await session.commit()
            await session.refresh(inventory)
            return inventory
        except Exception as e:
            await session.rollback()
            logger.error(f"Error updating count date for product {product_id}: {e}")
            return None

    async def get_inventory_summary(self, session: AsyncSession) -> dict:
        """
        Get inventory summary statistics.

        Args:
            session: Async database session

        Returns:
            dict: Inventory summary statistics
        """
        try:
            from sqlalchemy import func

            # Total inventory value would require joining with products table
            stmt = select(
                func.count(ProductInventory.id).label("total_products"),
                func.sum(ProductInventory.quantity_on_hand).label("total_on_hand"),
                func.sum(ProductInventory.quantity_available).label("total_available"),
                func.sum(ProductInventory.quantity_committed).label("total_committed"),
            )

            result = await session.execute(stmt)
            summary = result.fetchone()

            return {
                "total_products": summary.total_products or 0,
                "total_on_hand": summary.total_on_hand or 0,
                "total_available": summary.total_available or 0,
                "total_committed": summary.total_committed or 0,
            }
        except Exception as e:
            logger.error(f"Error getting inventory summary: {e}")
            return {
                "total_products": 0,
                "total_on_hand": 0,
                "total_available": 0,
                "total_committed": 0,
            }
