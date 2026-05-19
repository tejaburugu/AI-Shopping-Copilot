from sqlalchemy import Column, Float, Integer, String, Text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from utils.env import get_env

DATABASE_URL = get_env("DATABASE_URL", default="postgresql+asyncpg://postgres:postgres@db:5432/ai_shopping_copilot")

Base = declarative_base()
engine = create_async_engine(DATABASE_URL, future=True, echo=False)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class ProductTable(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    rating = Column(Float, nullable=False)
    description = Column(Text, nullable=False)
    image_url = Column(String, nullable=True)

    def as_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "brand": self.brand,
            "category": self.category,
            "price": self.price,
            "rating": self.rating,
            "description": self.description,
            "image_url": self.image_url,
        }
