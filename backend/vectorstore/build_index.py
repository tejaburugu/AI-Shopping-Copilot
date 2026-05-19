from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from vectorstore.embed import (
    DEFAULT_CHUNK_SIZE,
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_INDEX_DIR,
    DEFAULT_OVERLAP,
    VectorStore,
    load_products,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a FAISS vector store from products.json.")
    parser.add_argument(
        "--source",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data" / "products.json",
        help="Path to the products JSON file.",
    )
    parser.add_argument(
        "--index-dir",
        type=Path,
        default=DEFAULT_INDEX_DIR,
        help="Directory where the FAISS index will be saved.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_EMBEDDING_MODEL,
        help="HuggingFace sentence-transformers model name.",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=DEFAULT_CHUNK_SIZE,
        help="Maximum word count for each document chunk.",
    )
    parser.add_argument(
        "--overlap",
        type=int,
        default=DEFAULT_OVERLAP,
        help="Word overlap between adjacent chunks.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(f"Loading products from {args.source}")
    products = load_products(args.source)
    print(f"Loaded {len(products)} product records.")

    print("Building vector store...")
    VectorStore.from_products(
        products_path=args.source,
        index_dir=args.index_dir,
        chunk_size=args.chunk_size,
        overlap=args.overlap,
        model_name=args.model,
    )
    print(f"FAISS index saved to: {args.index_dir}")


if __name__ == "__main__":
    main()
