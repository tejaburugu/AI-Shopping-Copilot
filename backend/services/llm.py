import os
from typing import List, Optional

from langchain import LLMChain
from langchain.llms import GoogleGemini
from langchain.prompts import PromptTemplate

from models.product import Product
from utils.env import get_env
from utils.logger import get_logger

logger = get_logger("backend.llm")

SYSTEM_PROMPT = """You are an intelligent AI shopping assistant for an e-commerce platform.

You help users:
- discover products
- compare products
- summarize reviews
- explain tradeoffs
- provide recommendations

Given:
Retrieved products
Descriptions
Reviews

Return:
Recommended Products
Pros
Cons
Reasoning
Suggested alternatives

Keep responses concise and conversational."""

LLM_PROMPT = """{system_prompt}

User question:
{query}

Retrieved products:
{product_list}

Context:
{context}

Respond using the section headings exactly as requested.
Keep the answer concise and conversational.
"""


class LLMService:
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

    def build_product_list(self, products: List[Product]) -> str:
        lines = []
        for product in products:
            lines.append(
                f"- {product.name} by {product.brand} for ₹{product.price:,.0f} · Rating {product.rating}/5 · {product.category}"
            )
        return "\n".join(lines) if lines else "No products available."

    def generate_answer(self, query: str, context: str, products: List[Product]) -> str:
        if not self.llm:
            return self._fallback_response(query, products)

        prompt = PromptTemplate(
            template=LLM_PROMPT,
            input_variables=["system_prompt", "query", "product_list", "context"],
        )
        payload = {
            "system_prompt": SYSTEM_PROMPT,
            "query": query,
            "product_list": self.build_product_list(products),
            "context": context,
        }

        try:
            chain = LLMChain(llm=self.llm, prompt=prompt)
            return chain.run(**payload).strip()
        except Exception as exc:
            logger.warning("Gemini generation failed: %s", exc)
            return self._fallback_response(query, products)

    def _fallback_response(self, query: str, products: List[Product]) -> str:
        if not products:
            return "I couldn't find matching products in our catalog. Try a broader search or use different keywords."

        product_lines = [
            f"{product.name} by {product.brand} for ₹{product.price:,.0f}, rated {product.rating}/5."
            for product in products[:4]
        ]
        return (
            "Here are some top suggestions: "
            + " ".join(product_lines)
            + " Consider price, performance, and reviews to make your final choice."
        )


llm_service = LLMService()
