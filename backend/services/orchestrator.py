import json
from typing import Any, Dict, List, Optional

from langchain import LLMChain
from langchain.prompts import PromptTemplate

from models.product import Product
from services.llm import llm_service
from services.products_service import product_service
from services.vector_service import vector_service
from utils.logger import get_logger

logger = get_logger("backend.orchestrator")

PRODUCT_SEARCH_PROMPT = """You are a product search agent.
Use the user query to identify the most relevant products from the provided list.
Return a concise list of the top product IDs and names in JSON with keys:
- top_products
- rationale
"""

REVIEW_ANALYSIS_PROMPT = """You are a review analysis agent.
Given the product list and reviews, summarize the key review themes.
Return a JSON object with:
- review_summary
- pros
- cons
"""

RECOMMENDATION_PROMPT = """You are a recommendation agent.
Based on the query, products, and review analysis, recommend the best products.
Return a JSON object with:
- recommended_products
- reasons
- suggested_alternatives
"""

COMPARISON_PROMPT = """You are a comparison agent.
Compare the relevant products by performance, price, reviews, and tradeoffs.
Return a JSON object with:
- comparison_summary
- best_for
- tradeoffs
"""


def _parse_json(text: str) -> Optional[Dict[str, Any]]:
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end >= 0 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                return None
        return None


def _format_products(products: List[Product]) -> str:
    if not products:
        return "No products found."
    lines = []
    for product in products:
        line = (
            f"ID: {product.id}\n"
            f"Name: {product.name}\n"
            f"Brand: {product.brand}\n"
            f"Category: {product.category}\n"
            f"Price: ₹{product.price:,.0f}\n"
            f"Rating: {product.rating}/5\n"
            f"Description: {product.description}\n"
        )
        if product.specifications:
            spec_text = "; ".join(f"{key}: {value}" for key, value in product.specifications.items())
            line += f"Specifications: {spec_text}\n"
        if product.reviews:
            line += f"Reviews: {' | '.join(product.reviews[:3])}\n"
        lines.append(line.strip())
    return "\n\n".join(lines)


class BaseAgent:
    def __init__(self):
        self.llm = llm_service.llm

    def _run(self, prompt_template: str, variables: List[str], payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self.llm:
            logger.warning("LLM unavailable for agent execution.")
            return None
        prompt = PromptTemplate(template=prompt_template, input_variables=variables)
        chain = LLMChain(llm=self.llm, prompt=prompt)
        raw = chain.run(**payload)
        return _parse_json(raw)


class ProductSearchAgent(BaseAgent):
    def search(self, query: str, top_k: int = 5) -> List[Product]:
        semantic_results = vector_service.semantic_search(query, k=top_k)
        keyword_results = product_service.search(query, limit=top_k)
        if semantic_results:
            return semantic_results
        return keyword_results

    def summarize(self, query: str, products: List[Product]) -> Dict[str, Any]:
        payload = {
            "query": query,
            "products": _format_products(products),
        }
        parsed = self._run(PRODUCT_SEARCH_PROMPT, ["query", "products"], payload)
        return parsed or {"top_products": [product.id for product in products], "rationale": "Used the top matching products."}


class ReviewAnalysisAgent(BaseAgent):
    def analyze(self, products: List[Product]) -> Dict[str, Any]:
        payload = {
            "products": _format_products(products),
        }
        parsed = self._run(REVIEW_ANALYSIS_PROMPT, ["products"], payload)
        return parsed or {
            "review_summary": "Reviews highlight product performance and value.",
            "pros": "Strong reviews for build quality and features.",
            "cons": "Some users mention battery life and price.",
        }


class RecommendationAgent(BaseAgent):
    def recommend(self, query: str, products: List[Product], review_insights: Dict[str, Any]) -> Dict[str, Any]:
        payload = {
            "query": query,
            "products": _format_products(products),
            "review_analysis": json.dumps(review_insights, ensure_ascii=False),
        }
        parsed = self._run(RECOMMENDATION_PROMPT, ["query", "products", "review_analysis"], payload)
        return parsed or {
            "recommended_products": [product.id for product in products[:3]],
            "reasons": "These products balance performance, price, and customer satisfaction.",
            "suggested_alternatives": "Consider products with similar ratings if these are unavailable.",
        }


class ComparisonAgent(BaseAgent):
    def compare(self, query: str, products: List[Product], review_insights: Dict[str, Any]) -> Dict[str, Any]:
        payload = {
            "query": query,
            "products": _format_products(products),
            "review_analysis": json.dumps(review_insights, ensure_ascii=False),
        }
        parsed = self._run(COMPARISON_PROMPT, ["query", "products", "review_analysis"], payload)
        return parsed or {
            "comparison_summary": "These products differ mainly by price, features, and user reviews.",
            "best_for": "Choose based on budget and desired feature set.",
            "tradeoffs": "Higher-end models offer better performance but cost more.",
        }


class Orchestrator:
    def __init__(self):
        self.search_agent = ProductSearchAgent()
        self.review_agent = ReviewAnalysisAgent()
        self.recommendation_agent = RecommendationAgent()
        self.comparison_agent = ComparisonAgent()

    def orchestrate(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        products = self.search_agent.search(query, top_k=top_k)
        review_insights = self.review_agent.analyze(products)
        recommendation = self.recommendation_agent.recommend(query, products, review_insights)
        comparison = self.comparison_agent.compare(query, products, review_insights)

        final_answer = {
            "query": query,
            "search_results": [
                {
                    "id": product.id,
                    "name": product.name,
                    "brand": product.brand,
                    "category": product.category,
                    "price": product.price,
                    "rating": product.rating,
                }
                for product in products
            ],
            "review_insights": review_insights,
            "recommendation": recommendation,
            "comparison": comparison,
            "combined_output": {
                "recommended_products": recommendation.get("recommended_products"),
                "reasons": recommendation.get("reasons"),
                "comparison_summary": comparison.get("comparison_summary"),
                "tradeoffs": comparison.get("tradeoffs"),
            },
        }
        return final_answer


orchestrator = Orchestrator()
