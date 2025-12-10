from typing import Optional, List, Tuple, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from ..models import Product
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class ProductRepository:
    """Repository for Product model operations."""
    
    __slots__ = ()
    
    async def create(self, session: AsyncSession, **kwargs) -> Product:
        """
        Create a new product.
        
        Args:
            session: Async database session
            **kwargs: Product attributes
        
        Returns:
            Product: Created product instance
        
        Raises:
            ValueError: If required fields are missing
        """
        try:
            product = Product(**kwargs)
            session.add(product)
            await session.commit()
            await session.refresh(product)
            return product
        except Exception as e:
            await session.rollback()
            logger.error(f"Error creating product: {e}")
            raise
    
    async def get(self, session: AsyncSession, id: Any) -> Optional[Product]:
        """
        Get a product by ID.
        
        Args:
            session: Async database session
            id: Product ID
        
        Returns:
            Optional[Product]: Product if found, None otherwise
        """
        try:
            stmt = select(Product).where(Product.id == id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting product by ID {id}: {e}")
            return None
    
    async def get_all(self, session: AsyncSession, *, skip: int = 0, limit: int = 100) -> List[Product]:
        """
        Get all products with pagination.
        
        Args:
            session: Async database session
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List[Product]: List of products
        """
        try:
            stmt = select(Product).offset(skip).limit(limit)
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting all products: {e}")
            return []
    
    async def update(self, session: AsyncSession, id: Any, **kwargs) -> Optional[Product]:
        """
        Update a product by ID.
        
        Args:
            session: Async database session
            id: Product ID
            **kwargs: Attributes to update
        
        Returns:
            Optional[Product]: Updated product if found, None otherwise
        """
        try:
            product = await self.get(session, id)
            if not product:
                return None
            
            for key, value in kwargs.items():
                if hasattr(product, key):
                    setattr(product, key, value)
            
            await session.commit()
            await session.refresh(product)
            return product
        except Exception as e:
            await session.rollback()
            logger.error(f"Error updating product {id}: {e}")
            return None
    
    async def delete(self, session: AsyncSession, id: Any) -> bool:
        """
        Delete a product by ID.
        
        Args:
            session: Async database session
            id: Product ID
        
        Returns:
            bool: True if deleted, False otherwise
        """
        try:
            product = await self.get(session, id)
            if not product:
                return False
            
            await session.delete(product)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            logger.error(f"Error deleting product {id}: {e}")
            return False
    
    async def get_by_sku(self, session: AsyncSession, sku: str) -> Optional[Product]:
        """
        Get a product by SKU.
        
        Args:
            session: Async database session
            sku: Product SKU
        
        Returns:
            Optional[Product]: Product if found, None otherwise
        """
        try:
            stmt = select(Product).where(Product.sku == sku)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting product by SKU {sku}: {e}")
            return None
    
    async def get_by_name(self, session: AsyncSession, name: str) -> Optional[Product]:
        """
        Get a product by name.
        
        Args:
            session: Async database session
            name: Product name
        
        Returns:
            Optional[Product]: Product if found, None otherwise
        """
        try:
            stmt = select(Product).where(Product.name == name)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting product by name {name}: {e}")
            return None
    
    async def filter_by_category(self, session: AsyncSession, category_id: int, *, skip: int = 0, limit: int = 100) -> List[Product]:
        """
        Filter products by category.
        
        Args:
            session: Async database session
            category_id: Category ID
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List[Product]: List of products in specified category
        """
        try:
            stmt = select(Product).where(Product.category_id == category_id).offset(skip).limit(limit)
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error filtering products by category {category_id}: {e}")
            return []
    
    async def filter_by_supplier(self, session: AsyncSession, supplier_id: int, *, skip: int = 0, limit: int = 100) -> List[Product]:
        """
        Filter products by supplier.
        
        Args:
            session: Async database session
            supplier_id: Supplier ID
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List[Product]: List of products from specified supplier
        """
        try:
            stmt = select(Product).where(Product.supplier_id == supplier_id).offset(skip).limit(limit)
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error filtering products by supplier {supplier_id}: {e}")
            return []
    
    async def filter_by_active_status(self, session: AsyncSession, is_active: bool, *, skip: int = 0, limit: int = 100) -> List[Product]:
        """
        Filter products by active status.
        
        Args:
            session: Async database session
            is_active: Active status
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List[Product]: List of products with specified active status
        """
        try:
            stmt = select(Product).where(Product.is_active == is_active).offset(skip).limit(limit)
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error filtering products by active status {is_active}: {e}")
            return []
    
    async def filter_by_price_range(self, session: AsyncSession, min_price: Decimal, max_price: Decimal, *, skip: int = 0, limit: int = 100) -> List[Product]:
        """
        Filter products by price range.
        
        Args:
            session: Async database session
            min_price: Minimum price
            max_price: Maximum price
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List[Product]: List of products in price range
        """
        try:
            stmt = (
                select(Product)
                .where(and_(Product.price >= min_price, Product.price <= max_price))
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error filtering products by price range: {e}")
            return []
    
    async def get_or_create(self, session: AsyncSession, defaults: Optional[dict] = None, **kwargs) -> Tuple[Product, bool]:
        """
        Get a product or create if it doesn't exist.
        
        Args:
            session: Async database session
            defaults: Default values for creation
            **kwargs: Criteria for lookup
        
        Returns:
            Tuple[Product, bool]: (Product instance, created flag)
        """
        try:
            if 'sku' in kwargs:
                product = await self.get_by_sku(session, kwargs['sku'])
                if product:
                    return product, False
            
            create_data = {**kwargs, **(defaults or {})}
            product = await self.create(session, **create_data)
            return product, True
        except Exception as e:
            logger.error(f"Error in get_or_create for product: {e}")
            raise
    
    async def update_or_create(self, session: AsyncSession, criteria: dict, updates: dict) -> Tuple[Product, bool]:
        """
        Update a product or create if it doesn't exist.
        
        Args:
            session: Async database session
            criteria: Criteria for lookup
            updates: Values to update/create
        
        Returns:
            Tuple[Product, bool]: (Product instance, created flag)
        """
        try:
            if 'sku' in criteria:
                product = await self.get_by_sku(session, criteria['sku'])
            else:
                # Try to find by any criteria
                conditions = [getattr(Product, key) == value for key, value in criteria.items()]
                stmt = select(Product).where(and_(*conditions))
                result = await session.execute(stmt)
                product = result.scalar_one_or_none()
            
            if product:
                # Update existing
                for key, value in updates.items():
                    if hasattr(product, key):
                        setattr(product, key, value)
                await session.commit()
                await session.refresh(product)
                return product, False
            else:
                # Create new
                product_data = {**criteria, **updates}
                product = await self.create(session, **product_data)
                return product, True
        except Exception as e:
            await session.rollback()
            logger.error(f"Error in update_or_create for product: {e}")
            raise
    
    async def get_with_inventory(self, session: AsyncSession, id: Any) -> Optional[Product]:
        """
        Get a product with its inventory loaded.
        
        Args:
            session: Async database session
            id: Product ID
        
        Returns:
            Optional[Product]: Product with inventory if found
        """
        try:
            stmt = select(Product).options(selectinload(Product.inventory)).where(Product.id == id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting product with inventory {id}: {e}")
            return None
    
    async def get_with_category(self, session: AsyncSession, id: Any) -> Optional[Product]:
        """
        Get a product with its category loaded.
        
        Args:
            session: Async database session
            id: Product ID
        
        Returns:
            Optional[Product]: Product with category if found
        """
        try:
            stmt = select(Product).options(selectinload(Product.category)).where(Product.id == id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting product with category {id}: {e}")
            return None
    
    async def get_with_supplier(self, session: AsyncSession, id: Any) -> Optional[Product]:
        """
        Get a product with its supplier loaded.
        
        Args:
            session: Async database session
            id: Product ID
        
        Returns:
            Optional[Product]: Product with supplier if found
        """
        try:
            stmt = select(Product).options(selectinload(Product.supplier)).where(Product.id == id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting product with supplier {id}: {e}")
            return None
    
    async def get_with_stock_movements(self, session: AsyncSession, id: Any) -> Optional[Product]:
        """
        Get a product with its stock movements loaded.
        
        Args:
            session: Async database session
            id: Product ID
        
        Returns:
            Optional[Product]: Product with stock movements if found
        """
        try:
            stmt = select(Product).options(selectinload(Product.stock_movements)).where(Product.id == id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting product with stock movements {id}: {e}")
            return None
    
    async def get_low_stock_products(self, session: AsyncSession, *, skip: int = 0, limit: int = 100) -> List[Product]:
        """
        Get products with low stock (using inventory relationship).
        
        Args:
            session: Async database session
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List[Product]: List of low stock products
        """
        try:
            from app.models.product_inventory import ProductInventory
            
            stmt = (
                select(Product)
                .join(Product.inventory)
                .where(
                    and_(
                        Product.is_active == True,
                        ProductInventory.quantity_available < Product.low_stock_threshold
                    )
                )
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting low stock products: {e}")
            return []
    
    async def get_expiring_products(self, session: AsyncSession, days: int = 30, *, skip: int = 0, limit: int = 100) -> List[Product]:
        """
        Get products expiring within specified days.
        
        Args:
            session: Async database session
            days: Number of days
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List[Product]: List of expiring products
        """
        try:
            from datetime import datetime, timedelta
            cutoff_date = datetime.utcnow().date() + timedelta(days=days)
            
            stmt = (
                select(Product)
                .where(
                    and_(
                        Product.is_active == True,
                        Product.expiry_date.is_not(None),
                        Product.expiry_date <= cutoff_date
                    )
                )
                .order_by(Product.expiry_date.asc())
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting expiring products: {e}")
            return []
    
    async def search_products(self, session: AsyncSession, search_term: str, *, skip: int = 0, limit: int = 100) -> List[Product]:
        """
        Search products by SKU, name, or description.
        
        Args:
            session: Async database session
            search_term: Search term
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List[Product]: List of matching products
        """
        try:
            search_pattern = f"%{search_term}%"
            stmt = (
                select(Product)
                .where(
                    or_(
                        Product.sku.ilike(search_pattern),
                        Product.name.ilike(search_pattern),
                        Product.description.ilike(search_pattern)
                    )
                )
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return []
    
    async def get_products_with_full_details(self, session: AsyncSession, *, skip: int = 0, limit: int = 100) -> List[Product]:
        """
        Get products with all related data loaded.
        
        Args:
            session: Async database session
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List[Product]: List of products with full details
        """
        try:
            stmt = (
                select(Product)
                .options(
                    selectinload(Product.category),
                    selectinload(Product.supplier),
                    selectinload(Product.inventory)
                )
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting products with full details: {e}")
            return []