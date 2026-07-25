"""Retrieve the most relevant career doc chunks for a question (+ optional company context).

Outputs exactly one JSON object to stdout and nothing else, so another process
(e.g. the NestJS backend) can safely parse it:
  {"chunks": [{"text": ..., "source": ..., "section": ...}, ...]}
or on failure:
  {"error": "..."}
"""

import json
import sys
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

PROJECT_ROOT = Path(__file__).parent
CHROMA_DIR = PROJECT_ROOT / "chroma_db"
COLLECTION_NAME = "career_docs"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TOP_K = 5


def parse_args(argv: list[str]) -> tuple[str | None, str]:
    company = None
    remaining = []
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--company":
            i += 1
            company = argv[i] if i < len(argv) else None
        else:
            remaining.append(arg)
        i += 1
    return company, " ".join(remaining).strip()


def retrieve(query_text: str, embed_model: SentenceTransformer, collection, top_k: int = TOP_K):
    query_embedding = embed_model.encode([query_text], show_progress_bar=False).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=top_k)
    return list(zip(results["documents"][0], results["metadatas"][0]))


def fail(message: str):
    print(json.dumps({"error": message}))
    sys.exit(1)


def main():
    company, question = parse_args(sys.argv[1:])
    if not question:
        fail("No question provided.")

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    try:
        collection = client.get_collection(COLLECTION_NAME)
    except Exception:
        fail(f"Collection '{COLLECTION_NAME}' not found. Run ingest.py first.")

    embed_model = SentenceTransformer(EMBEDDING_MODEL)
    retrieval_query = f"Target company/domain: {company}. {question}" if company else question
    chunks = retrieve(retrieval_query, embed_model, collection)

    print(json.dumps({
        "chunks": [
            {"text": text, "source": meta.get("source"), "section": meta.get("section")}
            for text, meta in chunks
        ]
    }))


if __name__ == "__main__":
    main()
