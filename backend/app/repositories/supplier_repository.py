from typing import Optional, List, Tuple, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from models import Supplier
import logging

logger = logging.getLogger(__name__)


class SupplierRepository:
    """Repository for Supplier model operations."""

    __slots__ = ()

    async def create(self, session: AsyncSession, **kwargs) -> Supplier:
        """
        Create a new supplier.

        Args:
            session: Async database session
            **kwargs: Supplier attributes

        Returns:
            Supplier: Created supplier instance

        Raises:
            ValueError: If required fields are missing
        """
        try:
            supplier = Supplier(**kwargs)
            session.add(supplier)
            await session.commit()
            await session.refresh(supplier)
            return supplier
        except Exception as e:
            await session.rollback()
            logger.error(f"Error creating supplier: {e}")
            raise

    async def get(self, session: AsyncSession, id: Any) -> Optional[Supplier]:
        """
        Get a supplier by ID.

        Args:
            session: Async database session
            id: Supplier ID

        Returns:
            Optional[Supplier]: Supplier if found, None otherwise
        """
        try:
            stmt = select(Supplier).where(Supplier.id == id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting supplier by ID {id}: {e}")
            return None

    async def get_all(
        self, session: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Supplier]:
        """
        Get all suppliers with pagination.

        Args:
            session: Async database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Supplier]: List of suppliers
        """
        try:
            stmt = select(Supplier).offset(skip).limit(limit)
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting all suppliers: {e}")
            return []

    async def update(
        self, session: AsyncSession, id: Any, **kwargs
    ) -> Optional[Supplier]:
        """
        Update a supplier by ID.

        Args:
            session: Async database session
            id: Supplier ID
            **kwargs: Attributes to update

        Returns:
            Optional[Supplier]: Updated supplier if found, None otherwise
        """
        try:
            supplier = await self.get(session, id)
            if not supplier:
                return None

            for key, value in kwargs.items():
                if hasattr(supplier, key):
                    setattr(supplier, key, value)

            await session.commit()
            await session.refresh(supplier)
            return supplier
        except Exception as e:
            await session.rollback()
            logger.error(f"Error updating supplier {id}: {e}")
            return None

    async def delete(self, session: AsyncSession, id: Any) -> bool:
        """
        Delete a supplier by ID.

        Args:
            session: Async database session
            id: Supplier ID

        Returns:
            bool: True if deleted, False otherwise
        """
        try:
            supplier = await self.get(session, id)
            if not supplier:
                return False

            await session.delete(supplier)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            logger.error(f"Error deleting supplier {id}: {e}")
            return False

    async def get_by_name(self, session: AsyncSession, name: str) -> Optional[Supplier]:
        """
        Get a supplier by name.

        Args:
            session: Async database session
            name: Supplier name

        Returns:
            Optional[Supplier]: Supplier if found, None otherwise
        """
        try:
            stmt = select(Supplier).where(Supplier.name == name)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting supplier by name {name}: {e}")
            return None

    async def get_by_email(
        self, session: AsyncSession, email: str
    ) -> Optional[Supplier]:
        """
        Get a supplier by contact email.

        Args:
            session: Async database session
            email: Contact email

        Returns:
            Optional[Supplier]: Supplier if found, None otherwise
        """
        try:
            stmt = select(Supplier).where(Supplier.contact_email == email)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting supplier by email {email}: {e}")
            return None

    async def get_by_phone(
        self, session: AsyncSession, phone: str
    ) -> Optional[Supplier]:
        """
        Get a supplier by contact phone.

        Args:
            session: Async database session
            phone: Contact phone

        Returns:
            Optional[Supplier]: Supplier if found, None otherwise
        """
        try:
            stmt = select(Supplier).where(Supplier.contact_phone == phone)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting supplier by phone {phone}: {e}")
            return None

    async def filter_by_active_status(
        self, session: AsyncSession, is_active: bool, *, skip: int = 0, limit: int = 100
    ) -> List[Supplier]:
        """
        Filter suppliers by active status.

        Args:
            session: Async database session
            is_active: Active status
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Supplier]: List of suppliers with specified active status
        """
        try:
            stmt = (
                select(Supplier)
                .where(Supplier.is_active == is_active)
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error filtering suppliers by active status {is_active}: {e}")
            return []

    async def filter_by_country(
        self, session: AsyncSession, country: str, *, skip: int = 0, limit: int = 100
    ) -> List[Supplier]:
        """
        Filter suppliers by country.

        Args:
            session: Async database session
            country: Country name
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Supplier]: List of suppliers in specified country
        """
        try:
            stmt = (
                select(Supplier)
                .where(Supplier.country == country)
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error filtering suppliers by country {country}: {e}")
            return []

    async def filter_by_city(
        self, session: AsyncSession, city: str, *, skip: int = 0, limit: int = 100
    ) -> List[Supplier]:
        """
        Filter suppliers by city.

        Args:
            session: Async database session
            city: City name
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Supplier]: List of suppliers in specified city
        """
        try:
            stmt = (
                select(Supplier).where(Supplier.city == city).offset(skip).limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error filtering suppliers by city {city}: {e}")
            return []

    async def get_or_create(
        self, session: AsyncSession, defaults: Optional[dict] = None, **kwargs
    ) -> Tuple[Supplier, bool]:
        """
        Get a supplier or create if it doesn't exist.

        Args:
            session: Async database session
            defaults: Default values for creation
            **kwargs: Criteria for lookup

        Returns:
            Tuple[Supplier, bool]: (Supplier instance, created flag)
        """
        try:
            if "name" in kwargs:
                supplier = await self.get_by_name(session, kwargs["name"])
                if supplier:
                    return supplier, False

            create_data = {**kwargs, **(defaults or {})}
            supplier = await self.create(session, **create_data)
            return supplier, True
        except Exception as e:
            logger.error(f"Error in get_or_create for supplier: {e}")
            raise

    async def update_or_create(
        self, session: AsyncSession, criteria: dict, updates: dict
    ) -> Tuple[Supplier, bool]:
        """
        Update a supplier or create if it doesn't exist.

        Args:
            session: Async database session
            criteria: Criteria for lookup
            updates: Values to update/create

        Returns:
            Tuple[Supplier, bool]: (Supplier instance, created flag)
        """
        try:
            if "name" in criteria:
                supplier = await self.get_by_name(session, criteria["name"])
            elif "contact_email" in criteria:
                supplier = await self.get_by_email(session, criteria["contact_email"])
            else:
                # Try to find by any criteria
                conditions = [
                    getattr(Supplier, key) == value for key, value in criteria.items()
                ]
                stmt = select(Supplier).where(and_(*conditions))
                result = await session.execute(stmt)
                supplier = result.scalar_one_or_none()

            if supplier:
                # Update existing
                for key, value in updates.items():
                    if hasattr(supplier, key):
                        setattr(supplier, key, value)
                await session.commit()
                await session.refresh(supplier)
                return supplier, False
            else:
                # Create new
                supplier_data = {**criteria, **updates}
                supplier = await self.create(session, **supplier_data)
                return supplier, True
        except Exception as e:
            await session.rollback()
            logger.error(f"Error in update_or_create for supplier: {e}")
            raise

    async def get_with_products(
        self, session: AsyncSession, id: Any
    ) -> Optional[Supplier]:
        """
        Get a supplier with their products loaded.

        Args:
            session: Async database session
            id: Supplier ID

        Returns:
            Optional[Supplier]: Supplier with products if found
        """
        try:
            stmt = (
                select(Supplier)
                .options(selectinload(Supplier.products))
                .where(Supplier.id == id)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting supplier with products {id}: {e}")
            return None

    async def get_with_purchase_orders(
        self, session: AsyncSession, id: Any
    ) -> Optional[Supplier]:
        """
        Get a supplier with their purchase orders loaded.

        Args:
            session: Async database session
            id: Supplier ID

        Returns:
            Optional[Supplier]: Supplier with purchase orders if found
        """
        try:
            stmt = (
                select(Supplier)
                .options(selectinload(Supplier.purchase_orders))
                .where(Supplier.id == id)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting supplier with purchase orders {id}: {e}")
            return None

    async def get_active_suppliers_by_region(
        self,
        session: AsyncSession,
        country: str,
        state: Optional[str] = None,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Supplier]:
        """
        Get active suppliers by region (country and optionally state).

        Args:
            session: Async database session
            country: Country name
            state: State/province name (optional)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Supplier]: List of active suppliers in specified region
        """
        try:
            conditions = [Supplier.country == country, Supplier.is_active]
            if state:
                conditions.append(Supplier.state == state)

            stmt = select(Supplier).where(and_(*conditions)).offset(skip).limit(limit)
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting active suppliers by region: {e}")
            return []

    async def search_suppliers(
        self,
        session: AsyncSession,
        search_term: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Supplier]:
        """
        Search suppliers by name, email, or phone.

        Args:
            session: Async database session
            search_term: Search term
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Supplier]: List of matching suppliers
        """
        try:
            search_pattern = f"%{search_term}%"
            stmt = (
                select(Supplier)
                .where(
                    or_(
                        Supplier.name.ilike(search_pattern),
                        Supplier.contact_email.ilike(search_pattern),
                        Supplier.contact_phone.ilike(search_pattern),
                        Supplier.contact_person_name.ilike(search_pattern),
                    )
                )
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error searching suppliers: {e}")
            return []
