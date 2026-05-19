import json
import re
from pathlib import Path
from typing import List

from models.product import Product
from utils.logger import get_logger

logger = get_logger("backend.products_service")

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "products.json"

class ProductService:
    def __init__(self):
        self.products = self._load_products()

    def _load_products(self) -> List[Product]:
        logger.info("Loading products from JSON data...")
        with open(DATA_PATH, "r", encoding="utf-8") as handle:
            records = json.load(handle)
        products = [Product(**entry) for entry in records]
        logger.info("Loaded %d products", len(products))
        return products

    def get_product_by_id(self, product_id: str) -> Product | None:
        return next((product for product in self.products if product.id == product_id), None)

    def get_products_by_ids(self, product_ids: List[str]) -> List[Product]:
        return [product for product in self.products if product.id in product_ids]

    def _parse_budget(self, query: str) -> float | None:
        match = re.search(r"under\s*₹?\s*([0-9,]+)", query, re.IGNORECASE)
        if not match:
            return None
        return float(match.group(1).replace(",", ""))

    def search(self, query: str, limit: int = 8) -> List[Product]:
        budget = self._parse_budget(query)
        text = query.lower()
        scored = []

        for product in self.products:
            haystack = " ".join([
                product.name,
                product.brand,
                product.category,
                product.description,
            ]).lower()
            if budget is not None and product.price > budget:
                continue

            score = 0
            if any(term in haystack for term in text.split()):
                score += 1
            if product.category.lower() in text:
                score += 2
            if product.brand.lower() in text:
                score += 2
            if "gaming" in text and "gaming" in haystack:
                score += 3
            if "battery" in text and "battery" in haystack:
                score += 3
            if "laptop" in text and "laptop" in haystack:
                score += 2

            if score > 0:
                scored.append((score, product))

        scored.sort(key=lambda item: (-item[0], item[1].price))
        results = [item[1] for item in scored][:limit]

        if not results:
            results = sorted(self.products, key=lambda item: item.rating, reverse=True)[:limit]

        return results

product_service = ProductService()
