import os
from pathlib import Path
from typing import List, Optional

from models.product import Product
from services.products_service import product_service
from utils.env import get_env
from utils.logger import get_logger
from vectorstore.embed import DEFAULT_EMBEDDING_MODEL, VectorStore, load_embedding_model

logger = get_logger("backend.vector_service")
VECTOR_DIR = Path(__file__).resolve().parents[1] / "vectorstore" / "index"

class VectorService:
    def __init__(self):
        self.store: Optional[VectorStore] = None
        self.model = load_embedding_model(DEFAULT_EMBEDDING_MODEL)

    async def initialize(self):
        VECTOR_DIR.mkdir(parents=True, exist_ok=True)
        try:
            self.store = VectorStore.load(VECTOR_DIR, model_name=DEFAULT_EMBEDDING_MODEL)
            logger.info("Loaded existing FAISS vector store from %s", VECTOR_DIR)
        except Exception as exc:
            logger.info("Building FAISS vector store because loading failed: %s", exc)
            self.store = VectorStore.from_products(
                products_path=Path(__file__).resolve().parents[1] / "data" / "products.json",
                index_dir=VECTOR_DIR,
                model_name=DEFAULT_EMBEDDING_MODEL,
            )

    def semantic_search(self, query: str, k: int = 4) -> List[Product]:
        if not self.store:
            logger.warning("Vector search index is not initialized. Falling back to keyword search.")
            return []

        matches = self.store.search(query, top_k=k)
        products: List[Product] = []
        for item in matches:
            product_id = item.get("id")
            matched = next((product for product in product_service.products if product.id == product_id), None)
            if matched:
                products.append(matched)
        return products

vector_service = VectorService()
