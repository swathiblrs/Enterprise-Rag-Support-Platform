from pathlib import Path
from typing import List, Dict

import chromadb
from sentence_transformers import SentenceTransformer


DATA_DIR = Path("data")
VECTOR_DB_DIR = "vectorstore/chroma"
COLLECTION_NAME = "support_kb"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def load_documents() -> List[Dict]:
    documents = []

    for file_path in DATA_DIR.glob("*.md"):
        text = file_path.read_text(encoding="utf-8")

        documents.append(
            {
                "source": file_path.name,
                "text": text,
            }
        )

    return documents


def chunk_text(text: str, chunk_size: int = 700, overlap: int = 100) -> List[str]:
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def ingest_documents() -> None:
    print("Loading documents...")
    documents = load_documents()

    if not documents:
        print("No documents found in data/ folder.")
        return

    print(f"Loaded {len(documents)} documents.")

    print("Loading embedding model...")
    embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    print("Connecting to ChromaDB...")
    client = chromadb.PersistentClient(path=VECTOR_DB_DIR)

    # Delete old collection if it exists, so re-ingestion is clean.
    existing_collections = [collection.name for collection in client.list_collections()]
    if COLLECTION_NAME in existing_collections:
        client.delete_collection(name=COLLECTION_NAME)

    collection = client.create_collection(name=COLLECTION_NAME)

    ids = []
    texts = []
    metadatas = []

    chunk_id = 0

    for document in documents:
        source = document["source"]
        chunks = chunk_text(document["text"])

        for index, chunk in enumerate(chunks):
            ids.append(f"chunk-{chunk_id}")
            texts.append(chunk)
            metadatas.append(
                {
                    "source": source,
                    "chunk_index": index,
                }
            )
            chunk_id += 1

    print(f"Created {len(texts)} chunks.")

    print("Creating embeddings...")
    embeddings = embedding_model.encode(texts).tolist()

    print("Storing chunks in ChromaDB...")
    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    print("Ingestion complete.")
    print(f"Vector DB saved at: {VECTOR_DB_DIR}")
    print(f"Collection name: {COLLECTION_NAME}")


if __name__ == "__main__":
    ingest_documents()