from pydantic import BaseModel
from typing import Any, Dict, List, Optional

class Product(BaseModel):
    id: str
    name: str
    brand: str
    category: str
    price: float
    rating: float
    description: str
    reviews: List[str]
    specifications: Optional[Dict[str, Any]] = None
    image_url: Optional[str] = None

    @property
    def title(self) -> str:
        return self.name
