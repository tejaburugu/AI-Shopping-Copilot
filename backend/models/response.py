from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

from models.product import Product


class AskResponse(BaseModel):
    query: str
    answer: str
    contextual_query: Optional[str] = None
    structured_answer: Optional[Dict[str, Any]] = None
    context: Optional[str] = None
    previous_queries: List[str] = Field(default_factory=list)
    products: List[Product]
