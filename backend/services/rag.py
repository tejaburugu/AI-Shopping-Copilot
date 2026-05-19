import json
from typing import Any, Dict, List, Optional

from models.product import Product
from services.llm import llm_service
from services.memory import memory_service
from services.products_service import product_service
from services.vector_service import vector_service
from utils.logger import get_logger
from vectorstore.embed import DEFAULT_EMBEDDING_MODEL, DEFAULT_INDEX_DIR, VectorStore

logger = get_logger("backend.rag")

DEFAULT_PROMPT = """You are an AI shopping assistant.
Use the retrieved product context and customer reviews to answer the user's query.

Query:
{query}

Context:
{context}

Product List:
{product_list}

Return a JSON object with keys:
- summary: a concise recommendation
- top_products: a list of product names that best match the request
- reasons: why those products are recommended
- shopping_advice: practical buying guidance

If the query asks for comparisons, compare the relevant products directly.
Only return valid JSON. Do not include any extra commentary outside the JSON object."""


class RAGService:
    def __init__(self):
        self.gemini_api_key = get_env("GEMINI_API_KEY", default=os.getenv("GEMINI_API_KEY"))
        self.model_name = get_env("GEMINI_MODEL", default="gemini-pro")
        self.llm = None
        if self.gemini_api_key:
            try:
                self.llm = GoogleGemini(model=self.model_name, api_key=self.gemini_api_key)
            except Exception as exc:
                logger.warning("Failed to initialize Gemini LLM: %s", exc)
                self.llm = None

        self.store: Optional[VectorStore] = None

    async def initialize(self) -> None:
        if vector_service.store:
            self.store = vector_service.store
            logger.info("RAG service connected to shared vector store.")
            return

        try:
            self.store = VectorStore.load(DEFAULT_INDEX_DIR, model_name=DEFAULT_EMBEDDING_MODEL)
            logger.info("RAG service loaded FAISS vector store from %s", DEFAULT_INDEX_DIR)
        except Exception as exc:
            logger.warning("RAG service failed to load vector store: %s", exc)
            self.store = None

    def retrieve_relevant_documents(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if not self.store:
            logger.warning("Vector store not available during RAG retrieval.")
            return []

        return self.store.search(query, top_k=top_k)

    def retrieve_top_products(self, documents: List[Dict[str, Any]]) -> List[Product]:
        product_ids: List[str] = []
        products: List[Product] = []

        for document in documents:
            product_id = document.get("id")
            if not product_id or product_id in product_ids:
                continue

            product = product_service.get_product_by_id(product_id)
            if product:
                products.append(product)
                product_ids.append(product_id)

        return products

    def create_context(self, documents: List[Dict[str, Any]]) -> str:
        if not documents:
            return "No retrieved context available."

        context_lines: List[str] = []
        for document in documents:
            product_name = document.get("name", "Unknown product")
            category = document.get("category", "Unknown category")
            context_lines.append(f"Product: {product_name} ({category})")

            specifications = document.get("specifications", {})
            if specifications:
                spec_text = "; ".join(f"{key}: {value}" for key, value in specifications.items())
                context_lines.append(f"Specifications: {spec_text}")

            reviews = document.get("reviews", [])
            if reviews:
                review_text = " | ".join(reviews[:2])
                context_lines.append(f"Reviews: {review_text}")

            content = document.get("content")
            if content:
                snippet = content.strip().replace("\n", " ")
                context_lines.append(f"Document snippet: {snippet[:400]}")

            chunk_index = document.get("chunk_index")
            total_chunks = document.get("total_chunks")
            score = document.get("score")
            context_lines.append(
                f"Source chunk: {chunk_index}/{total_chunks} · score: {score:.4f}"
                if chunk_index and total_chunks
                else "Source chunk metadata unavailable."
            )
            context_lines.append("---")

        return "\n".join(context_lines)

    def create_context_from_products(self, products: List[Product]) -> str:
        if not products:
            return "No product context available."

        context_lines: List[str] = []
        for product in products:
            context_lines.append(f"Product: {product.name} ({product.category})")
            context_lines.append(f"Description: {product.description}")
            if product.specifications:
                spec_text = "; ".join(f"{key}: {value}" for key, value in product.specifications.items())
                context_lines.append(f"Specifications: {spec_text}")
            if product.reviews:
                review_text = " | ".join(product.reviews[:2])
                context_lines.append(f"Reviews: {review_text}")
            context_lines.append("---")

        return "\n".join(context_lines)

    def build_product_list(self, products: List[Product]) -> str:
        lines: List[str] = []
        for product in products:
            lines.append(
                f"- {product.name} by {product.brand} for ₹{product.price:,.0f} · Rating {product.rating}/5 · {product.category}"
            )
        return "\n".join(lines)

    def _parse_json(self, text: str) -> Optional[Dict[str, Any]]:
        if not text:
            return None

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}")
            if start >= 0 and end >= 0 and end > start:
                candidate = text[start : end + 1]
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    return None
            return None

    def _build_prompt(self, query: str, context: str, products: List[Product]) -> Dict[str, Any]:
        return {
            "query": query,
            "context": context,
            "product_list": self.build_product_list(products),
        }

    def generate_response(
        self, query: str, context: str, products: List[Product]
    ) -> tuple[str, Optional[Dict[str, Any]]]:
        raw = llm_service.generate_answer(query, context, products)
        structured = self._parse_json(raw)
        return raw, structured

    def _fallback_response(self, query: str, products: List[Product]) -> str:
        if not products:
            return "I couldn't find matching products in our catalog. Try a broader search or use different keywords."

        product_lines = [
            f"{product.name} by {product.brand} for ₹{product.price:,.0f}, rated {product.rating}/5."
            for product in products[:4]
        ]
        if "compare" in query.lower():
            product_lines.append(
                "Compare the products above by price, brand, and rating to choose the best fit."
            )
        else:
            product_lines.append(
                "Choose the product that fits your budget and priorities, such as performance, battery life, or review strength."
            )

        return " ".join(product_lines)

    async def answer_query(
        self, query: str, top_k: int = 5, session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        contextual_query = memory_service.build_contextual_query(query, session_id=session_id)
        documents = self.retrieve_relevant_documents(contextual_query, top_k=top_k)
        products = self.retrieve_top_products(documents)

        if not products:
            products = product_service.search(contextual_query, limit=top_k)

        context = (
            self.create_context(documents)
            if documents
            else self.create_context_from_products(products)
        )

        answer_text, structured_answer = self.generate_response(contextual_query, context, products)
        memory_service.save_turn(query, answer_text, session_id=session_id)

        return {
            "query": query,
            "contextual_query": contextual_query,
            "answer": answer_text,
            "structured_answer": structured_answer,
            "context": context,
            "products": products,
            "previous_queries": memory_service.get_previous_queries(session_id=session_id),
        }


rag_service = RAGService()
