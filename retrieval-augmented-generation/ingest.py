"""Chunk docs/*.md, embed them locally, and store them in a local Chroma collection.

Chunking is section-based (split on '## ' headers) rather than fixed-size, so each
chunk stays a coherent, self-contained piece of the story instead of an arbitrary cut.

Re-running this script rebuilds the collection from scratch, so it always reflects
the current state of docs/ with no stale or duplicate chunks left behind.
"""

import hashlib
import re
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

PROJECT_ROOT = Path(__file__).parent
DOCS_DIR = PROJECT_ROOT / "docs"
CHROMA_DIR = PROJECT_ROOT / "chroma_db"
COLLECTION_NAME = "career_docs"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def parse_frontmatter(text):
    """Split a markdown file into (metadata dict, body). Assumes flat key: value frontmatter."""
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    metadata = {}
    for line in parts[1].strip().split("\n"):
        if ":" in line:
            key, _, value = line.partition(":")
            metadata[key.strip()] = value.strip()
    return metadata, parts[2].strip()


def extract_title(body):
    for line in body.split("\n"):
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def split_into_sections(body):
    """Split body into (section_title, section_text) pairs on '## ' headers.
    Falls back to one section covering the whole body if there are no '## ' headers."""
    sections = []
    current_title = None
    current_lines = []

    def flush():
        if current_lines:
            sections.append((current_title, "\n".join(current_lines).strip()))

    for line in body.split("\n"):
        if line.startswith("## "):
            flush()
            current_title = line[3:].strip()
            current_lines = []
        elif line.startswith("# "):
            continue  # title, handled separately
        else:
            current_lines.append(line)
    flush()

    return sections if sections else [(None, body.strip())]


def build_chunks(file_path):
    raw = file_path.read_text()
    metadata, body = parse_frontmatter(raw)
    body = HTML_COMMENT_RE.sub("", body).strip()
    title = extract_title(body)

    chunks = []
    for section_title, section_text in split_into_sections(body):
        if not section_text.strip():
            continue  # skip empty / TODO-only sections

        chunk_text = f"# {title}\n"
        if section_title:
            chunk_text += f"## {section_title}\n"
        chunk_text += section_text

        chunk_id = hashlib.sha256(f"{file_path}::{section_title or 'full'}".encode()).hexdigest()

        chunk_metadata = dict(metadata)
        chunk_metadata["source"] = str(file_path.relative_to(DOCS_DIR))
        chunk_metadata["section"] = section_title or "full"

        chunks.append((chunk_id, chunk_text, chunk_metadata))

    return chunks


def main():
    md_files = sorted(DOCS_DIR.rglob("*.md"))
    if not md_files:
        print(f"No markdown files found in {DOCS_DIR}")
        return

    all_chunks = []
    for file_path in md_files:
        try:
            file_chunks = build_chunks(file_path)
        except Exception as e:
            print(f"Skipping {file_path.name}: {e}")
            continue
        all_chunks.extend(file_chunks)
        print(f"{file_path.relative_to(DOCS_DIR)}: {len(file_chunks)} chunk(s)")

    if not all_chunks:
        print("No chunks to ingest.")
        return

    print(f"\nEmbedding {len(all_chunks)} chunks with {EMBEDDING_MODEL} ...")
    model = SentenceTransformer(EMBEDDING_MODEL)
    texts = [c[1] for c in all_chunks]
    embeddings = model.encode(texts, show_progress_bar=True).tolist()

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    existing_collections = [c.name for c in client.list_collections()]
    if COLLECTION_NAME in existing_collections:
        client.delete_collection(COLLECTION_NAME)
    collection = client.create_collection(COLLECTION_NAME)

    collection.add(
        ids=[c[0] for c in all_chunks],
        embeddings=embeddings,
        documents=texts,
        metadatas=[c[2] for c in all_chunks],
    )

    print(f"\nDone. Stored {len(all_chunks)} chunks in '{COLLECTION_NAME}' at {CHROMA_DIR}")
    print("\nSample chunks:")
    for chunk_id, text, meta in all_chunks[:3]:
        preview = text.replace("\n", " ")[:100]
        print(f"  [{meta['source']} / {meta['section']}] {preview}...")


if __name__ == "__main__":
    main()
