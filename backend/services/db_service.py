import asyncio
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from models.db import AsyncSessionLocal, Base, engine, ProductTable
from services.products_service import product_service
from utils.env import get_env
from utils.logger import get_logger

logger = get_logger("backend.db_service")

async def init_db() -> None:
    db_url = get_env("DATABASE_URL")
    if not db_url:
        logger.warning("DATABASE_URL is not set. Skipping database initialization.")
        return

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await _sync_products()
        logger.info("Database initialized successfully.")
    except SQLAlchemyError as exc:
        logger.warning("Failed to initialize database: %s", exc)

async def _sync_products() -> None:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            existing = await session.execute(select(ProductTable.id))
            existing_ids = {row[0] for row in existing.fetchall()}
            for product in product_service.products:
                if product.id not in existing_ids:
                    session.add(
                        ProductTable(
                            id=product.id,
                            title=product.title,
                            brand=product.brand,
                            category=product.category,
                            price=product.price,
                            rating=product.rating,
                            description=product.description,
                            image_url=product.image_url,
                        )
                    )
        await session.commit()
        logger.info("Product catalog synchronized with PostgreSQL.")

async def get_product_by_id(product_id: str) -> Optional[ProductTable]:
    async with AsyncSessionLocal() as session:
        return await session.get(ProductTable, product_id)
