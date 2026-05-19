import os
from typing import List

from langchain import LLMChain
from langchain.llms import GoogleGemini
from langchain.prompts import PromptTemplate

from models.product import Product
from utils.env import get_env
from utils.logger import get_logger

logger = get_logger("backend.ai_service")

DEFAULT_PROMPT = """You are an AI shopping assistant. The user asked: {query}

Here are some matching products:
{product_list}

Write a concise recommendation with practical shopping advice, comparing products when appropriate, and include product features, price context, and review highlights."""

class AIService:
    def __init__(self):
        self.gemini_api_key = get_env("GEMINI_API_KEY", default=os.getenv("GEMINI_API_KEY"))
        self.model_name = get_env("GEMINI_MODEL", default="gemini-pro")
        self.llm = None
        if self.gemini_api_key:
            try:
                self.llm = GoogleGemini(model=self.model_name, api_key=self.gemini_api_key)
            except Exception as exc:
                logger.warning("Failed to initialize Gemini client: %s", exc)
                self.llm = None

    async def generate_response(self, query: str, products: List[Product]) -> str:
        payload = self._build_context(query, products)
        if self.llm:
            try:
                prompt = PromptTemplate(template=DEFAULT_PROMPT, input_variables=["query", "product_list"])
                chain = LLMChain(llm=self.llm, prompt=prompt)
                response = chain.run(**payload)
                return response.strip()
            except Exception as exc:
                logger.warning("Gemini request failed: %s", exc)

        return self._fallback_response(query, products)

    def _build_context(self, query: str, products: List[Product]) -> dict:
        product_lines = []
        for product in products:
            product_lines.append(
                f"- {product.title} ({product.brand}) for ₹{product.price:,.0f} · Rating {product.rating}/5 · {product.category}: {product.description}"
            )
        return {
            "query": query,
            "product_list": "\n".join(product_lines) if product_lines else "No products matched the query.",
        }

    def _fallback_response(self, query: str, products: List[Product]) -> str:
        if not products:
            return "I couldn't find matching products in our catalog. Try a broader search or use different keywords."

        summary = [f"I found {len(products)} products matching your request:"]
        for product in products[:4]:
            summary.append(
                f"{product.title} by {product.brand} for ₹{product.price:,.0f}, rated {product.rating}/5."
            )
        if "compare" in query.lower():
            summary.append("Use the list above to compare price, brand, and rating head-to-head.")
        elif "review" in query.lower() or "summarize" in query.lower():
            summary.append("These products have strong reviews for performance and build quality. Focus on the ones with higher ratings and recent customer praise.")
        else:
            summary.append("Pick the product that fits your budget and preferred brand, and look for battery life or performance in the description.")
        return " ".join(summary)

ai_service = AIService()
