from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Any, Dict, Iterable, List

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_CHUNK_SIZE = 250
DEFAULT_OVERLAP = 50
DEFAULT_INDEX_DIR = Path(__file__).resolve().parent / "index"
INDEX_FILENAME = "index.faiss"
METADATA_FILENAME = "metadata.pkl"
CONFIG_FILENAME = "config.json"


def load_products(products_path: Path) -> List[Dict[str, Any]]:
    products_path = products_path.resolve()
    if not products_path.exists():
        raise FileNotFoundError(f"Product data file not found: {products_path}")

    with products_path.open("r", encoding="utf-8") as handle:
        records = json.load(handle)

    return [normalize_product(record) for record in records]


def normalize_product(product: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": product.get("id", ""),
        "name": product.get("name") or product.get("title") or "Unnamed Product",
        "category": product.get("category", "Unknown"),
        "description": product.get("description", ""),
        "specifications": product.get("specifications", {}) or {},
        "reviews": product.get("reviews", []) or [],
    }


def product_to_text(product: Dict[str, Any]) -> str:
    sections: List[str] = [product["name"], product["category"], product["description"]]

    specifications = product.get("specifications", {})
    if specifications:
        spec_lines = [f"{key}: {value}" for key, value in specifications.items()]
        sections.append(". ".join(spec_lines))

    reviews = product.get("reviews", [])
    if reviews:
        sections.append(" Reviews: " + " ".join(reviews))

    return " \n ".join([section.strip() for section in sections if section])


def chunk_text(text: str, chunk_size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_OVERLAP) -> List[str]:
    words = text.split()
    if not words:
        return []

    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap")

    if len(words) <= chunk_size:
        return [" ".join(words)]

    chunks: List[str] = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start += chunk_size - overlap

    return chunks


def build_documents(
    products: Iterable[Dict[str, Any]],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
) -> List[Dict[str, Any]]:
    documents: List[Dict[str, Any]] = []
    for product in products:
        content = product_to_text(product)
        chunks = chunk_text(content, chunk_size=chunk_size, overlap=overlap)
        total_chunks = len(chunks)

        for chunk_index, chunk in enumerate(chunks, start=1):
            documents.append(
                {
                    "content": chunk,
                    "metadata": {
                        "id": product["id"],
                        "name": product["name"],
                        "category": product["category"],
                        "chunk_index": chunk_index,
                        "total_chunks": total_chunks,
                        "specifications": product["specifications"],
                        "reviews": product["reviews"],
                        "content": chunk,
                    },
                }
            )

    return documents


def load_embedding_model(model_name: str = DEFAULT_EMBEDDING_MODEL) -> SentenceTransformer:
    return SentenceTransformer(model_name)


def embed_texts(model: SentenceTransformer, texts: List[str]) -> np.ndarray:
    if not texts:
        return np.zeros((0, model.get_sentence_embedding_dimension()), dtype="float32")

    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    return normalize_embeddings(np.asarray(embeddings, dtype="float32"))


def normalize_embeddings(embeddings: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return embeddings / norms


def create_faiss_index(embedding_dim: int) -> faiss.Index:
    return faiss.IndexFlatIP(embedding_dim)


def save_vectorstore(
    index: faiss.Index,
    metadata: List[Dict[str, Any]],
    directory: Path,
) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(directory / INDEX_FILENAME))
    with open(directory / METADATA_FILENAME, "wb") as handle:
        pickle.dump(metadata, handle)


def load_vectorstore(directory: Path) -> tuple[faiss.Index, List[Dict[str, Any]]]:
    index_path = directory / INDEX_FILENAME
    metadata_path = directory / METADATA_FILENAME
    if not index_path.exists() or not metadata_path.exists():
        raise FileNotFoundError("FAISS index or metadata file is missing.")

    index = faiss.read_index(str(index_path))
    with open(metadata_path, "rb") as handle:
        metadata = pickle.load(handle)

    return index, metadata


def search_vectorstore(
    index: faiss.Index,
    metadata: List[Dict[str, Any]],
    model: SentenceTransformer,
    query: str,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    query_embedding = embed_texts(model, [query])
    distances, indices = index.search(query_embedding, top_k)
    results: List[Dict[str, Any]] = []
    for distance, index_position in zip(distances[0], indices[0]):
        if index_position < 0 or index_position >= len(metadata):
            continue
        document = metadata[index_position].copy()
        document["score"] = float(distance)
        results.append(document)
    return results


class VectorStore:
    def __init__(self, index: faiss.Index, metadata: List[Dict[str, Any]], model: SentenceTransformer):
        self.index = index
        self.metadata = metadata
        self.model = model

    @classmethod
    def from_products(
        cls,
        products_path: Path,
        index_dir: Path = DEFAULT_INDEX_DIR,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        overlap: int = DEFAULT_OVERLAP,
        model_name: str = DEFAULT_EMBEDDING_MODEL,
    ) -> "VectorStore":
        products = load_products(products_path)
        documents = build_documents(products, chunk_size=chunk_size, overlap=overlap)
        model = load_embedding_model(model_name)
        embeddings = embed_texts(model, [doc["content"] for doc in documents])
        index = create_faiss_index(embeddings.shape[1])
        index.add(embeddings)
        metadata = [doc["metadata"] for doc in documents]
        save_vectorstore(index, metadata, index_dir)
        return cls(index=index, metadata=metadata, model=model)

    @classmethod
    def load(
        cls,
        index_dir: Path = DEFAULT_INDEX_DIR,
        model_name: str = DEFAULT_EMBEDDING_MODEL,
    ) -> "VectorStore":
        index, metadata = load_vectorstore(index_dir)
        model = load_embedding_model(model_name)
        return cls(index=index, metadata=metadata, model=model)

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        return search_vectorstore(self.index, self.metadata, self.model, query, top_k=top_k)
