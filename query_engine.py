import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from vector_store import load_faiss_index

# Load the same model used for embedding
model = SentenceTransformer("all-MiniLM-L6-v2")

def get_query_embedding(query: str) -> np.ndarray:
    """
    Converts the user query into an embedding vector.

    Args:
        query (str): User's question or search term

    Returns:
        np.ndarray: Embedding vector (1, 384)
    """
    return np.array(model.encode([query])).astype("float32")


def search(query: str, k: int = 3):
    """
    Searches for the top-k most relevant news articles based on the query.

    Args:
        query (str): User's question
        k (int): Number of top results to return
    """
    index, metadata = load_faiss_index()
    query_vector = get_query_embedding(query)

    # Perform search
    distances, indices = index.search(query_vector, k)

    results = []
    for i in indices[0]:
        article = metadata.iloc[i]
        results.append({
            "headline": article["Headline"],
            "summary": article["Summary"],
            "url": article["URL"]
        })

    return results


if __name__ == "__main__":
    user_input = input("Ask me about the news: ")
    results = search(user_input)

    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"Headline: {result['headline']}")
        print(f"Summary: {result['summary']}")
        print(f"URL: {result['url']}")