from typing import List, Dict

import chromadb
from sentence_transformers import SentenceTransformer


VECTOR_DB_DIR = "vectorstore/chroma"
COLLECTION_NAME = "support_kb"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def retrieve_relevant_chunks(query: str, top_k: int = 3) -> List[Dict]:
    embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    client = chromadb.PersistentClient(path=VECTOR_DB_DIR)
    collection = client.get_collection(name=COLLECTION_NAME)

    query_embedding = embedding_model.encode([query]).tolist()[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    retrieved_chunks = []

    for document, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        retrieved_chunks.append(
            {
                "text": document,
                "source": metadata["source"],
                "chunk_index": metadata["chunk_index"],
                "distance": distance,
            }
        )

    return retrieved_chunks


if __name__ == "__main__":
    question = "My VPN is not working after I reset my password"

    chunks = retrieve_relevant_chunks(question)

    print(f"\nQuestion: {question}\n")
    print("Retrieved Chunks:\n")

    for i, chunk in enumerate(chunks, start=1):
        print(f"--- Result {i} ---")
        print(f"Source: {chunk['source']}")
        print(f"Chunk Index: {chunk['chunk_index']}")
        print(f"Distance: {chunk['distance']}")
        print(chunk["text"])
        print()