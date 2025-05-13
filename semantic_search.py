import numpy as np
import pandas as pd
import openai
from sklearn.metrics.pairwise import cosine_similarity
from config import ( OPENAI_API_KEY, OPENAI_API_VERSION, EMBEDDING_DEPLOYMENT_NAME, OPENAI_ENDPOINT, OPENAI_TYPE)

openai.api_key = OPENAI_API_KEY
openai.api_base = OPENAI_ENDPOINT
openai.api_version = OPENAI_API_VERSION
openai.api_type = OPENAI_TYPE

# Load the embeddings CSV
df = pd.read_csv("embedded_news.csv")
df["embedding"] = df["embedding"].apply(eval).apply(np.array)

def embed_text(text):
    """Generate embedding for the user prompt"""
    response = openai.Embedding.create(
        input=[text],
        engine=EMBEDDING_DEPLOYMENT_NAME
    )
    return np.array(response["data"][0]["embedding"])

def search_similar_articles(query, k=3):
    """Return top k articles similar to the query"""
    query_embedding = embed_text(query)
    df["similarity"] = df["embedding"].apply(lambda x: cosine_similarity([x], [query_embedding])[0][0])
    return df.sort_values("similarity", ascending=False).head(k)

if __name__ == "__main__":
    query = input("Enter your query: ")
    results = search_similar_articles(query)
    for i, row in results.iterrows():
        print(f"\nHeadline: {row['Headline']}")
        print(f"Summary: {row['Summary']}")
        print(f"Similarity Score: {row['similarity']:.4f}")