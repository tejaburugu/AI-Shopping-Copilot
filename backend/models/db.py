from sqlalchemy import Column, DateTime, Float, Integer, String, Text, func
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


class UserTable(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def as_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "created_at": self.created_at,
        }
