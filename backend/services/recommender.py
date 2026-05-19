import logging
from typing import Dict, List, Optional

import numpy as np
from models.product import Product
from services.products_service import product_service
from utils.logger import get_logger
from vectorstore.embed import DEFAULT_EMBEDDING_MODEL, load_embedding_model, normalize_embeddings

logger = get_logger("backend.recommender")

DEFAULT_USER_ID = "global"

class UserInteraction:
    def __init__(self) -> None:
        self.viewed_products: List[str] = []
        self.clicked_products: List[str] = []
        self.search_history: List[str] = []

    def record_view(self, product_id: str) -> None:
        if product_id not in self.viewed_products:
            self.viewed_products.append(product_id)

    def record_click(self, product_id: str) -> None:
        if product_id not in self.clicked_products:
            self.clicked_products.append(product_id)

    def record_search(self, query: str) -> None:
        query = query.strip()
        if query and query not in self.search_history:
            self.search_history.append(query)

    def interacted_products(self) -> List[str]:
        return list(dict.fromkeys(self.clicked_products + self.viewed_products))


class RecommenderService:
    def __init__(self):
        self.sessions: Dict[str, UserInteraction] = {}
        self.model = load_embedding_model(DEFAULT_EMBEDDING_MODEL)
        self.product_embeddings: Optional[np.ndarray] = None
        self.product_index: Dict[str, int] = {}
        self._build_embeddings()

    def _build_embeddings(self) -> None:
        products = product_service.products
        self.product_index = {product.id: idx for idx, product in enumerate(products)}
        texts = [self._product_text(product) for product in products]
        embeddings = self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        self.product_embeddings = normalize_embeddings(np.asarray(embeddings, dtype="float32"))
        logger.info("Built product embedding matrix for %d products", len(texts))

    def _product_text(self, product: Product) -> str:
        parts: List[str] = [product.name, product.category, product.description]
        if product.specifications:
            parts.append(" ".join(f"{k}: {v}" for k, v in product.specifications.items()))
        if product.reviews:
            parts.append(" ".join(product.reviews))
        return " \n ".join([part for part in parts if part])

    def _get_session(self, user_id: Optional[str] = None) -> UserInteraction:
        user_id = user_id or DEFAULT_USER_ID
        if user_id not in self.sessions:
            self.sessions[user_id] = UserInteraction()
        return self.sessions[user_id]

    def record_view(self, product_id: str, user_id: Optional[str] = None) -> None:
        self._get_session(user_id).record_view(product_id)

    def record_click(self, product_id: str, user_id: Optional[str] = None) -> None:
        self._get_session(user_id).record_click(product_id)

    def record_search(self, query: str, user_id: Optional[str] = None) -> None:
        self._get_session(user_id).record_search(query)

    def _query_profile(self, user_id: Optional[str]) -> Optional[np.ndarray]:
        session = self._get_session(user_id)
        if self.product_embeddings is None:
            return None

        vectors: List[np.ndarray] = []
        weights: List[float] = []

        for product_id in session.clicked_products:
            idx = self.product_index.get(product_id)
            if idx is not None:
                vectors.append(self.product_embeddings[idx])
                weights.append(0.6)

        for product_id in session.viewed_products:
            idx = self.product_index.get(product_id)
            if idx is not None:
                vectors.append(self.product_embeddings[idx])
                weights.append(0.3)

        if session.search_history:
            search_embeddings = self.model.encode(
                session.search_history,
                show_progress_bar=False,
                convert_to_numpy=True,
            )
            search_embeddings = normalize_embeddings(np.asarray(search_embeddings, dtype="float32"))
            for vector in search_embeddings:
                vectors.append(vector)
                weights.append(0.1)

        if not vectors:
            return None

        weighted = np.stack(vectors, axis=0) * np.array(weights, dtype="float32")[:, None]
        profile = weighted.sum(axis=0)
        normalized = profile / (np.linalg.norm(profile) + 1e-12)
        return normalized

    def recommend_also_liked(
        self,
        user_id: Optional[str] = None,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        session = self._get_session(user_id)
        product_ids = list(self.product_index.keys())
        if self.product_embeddings is None:
            return {"message": "No product embeddings available.", "recommendations": []}

        profile = self._query_profile(user_id)
        if profile is None:
            ranked = sorted(product_service.products, key=lambda item: item.rating, reverse=True)[:top_k]
            return {
                "headline": "Users interested in this also liked",
                "recommendations": [self._product_summary(product) for product in ranked],
                "source": "popular",
            }

        similarities = np.dot(self.product_embeddings, profile)
        interacted = set(session.interacted_products())
        scored = [
            (score, product_id)
            for product_id, score in zip(product_ids, similarities.tolist())
            if product_id not in interacted
        ]
        scored.sort(key=lambda item: item[0], reverse=True)
        recommendations = []
        for score, product_id in scored[:top_k]:
            product = product_service.get_product_by_id(product_id)
            if not product:
                continue
            recommendations.append(
                {
                    "id": product.id,
                    "name": product.name,
                    "brand": product.brand,
                    "category": product.category,
                    "price": product.price,
                    "rating": product.rating,
                    "score": float(score),
                }
            )

        return {
            "headline": "Users interested in this also liked",
            "recommendations": recommendations,
            "source": "content_based",
            "history": {
                "views": session.viewed_products,
                "clicks": session.clicked_products,
                "search_history": session.search_history,
            },
        }

    def recommend_similar_products(
        self,
        product_id: str,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        if self.product_embeddings is None:
            return []

        idx = self.product_index.get(product_id)
        if idx is None:
            return []

        query_vector = self.product_embeddings[idx]
        similarities = np.dot(self.product_embeddings, query_vector)
        scored = [
            (score, pid)
            for pid, score in zip(self.product_index.keys(), similarities.tolist())
            if pid != product_id
        ]
        scored.sort(key=lambda item: item[0], reverse=True)

        result = []
        for score, similar_id in scored[:top_k]:
            product = product_service.get_product_by_id(similar_id)
            if product:
                result.append(
                    {
                        "id": product.id,
                        "name": product.name,
                        "brand": product.brand,
                        "category": product.category,
                        "price": product.price,
                        "rating": product.rating,
                        "score": float(score),
                    }
                )
        return result

    def _product_summary(self, product: Product) -> Dict[str, Any]:
        return {
            "id": product.id,
            "name": product.name,
            "brand": product.brand,
            "category": product.category,
            "price": product.price,
            "rating": product.rating,
        }


recommender_service = RecommenderService()
