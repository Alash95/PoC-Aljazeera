import numpy as np
import pandas as pd
import os
from dotenv import load_dotenv
from openai import AzureOpenAI
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_EMBEDDING_DEPLOYMENT")
AZURE_OPENAI_TYPE = os.getenv("AZURE_OPENAI_TYPE")
AZURE_CHAT_DEPLOYMENT_NAME = os.getenv("AZURE_CHAT_DEPLOYMENT_NAME")

# Initialize Azure client

client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version=AZURE_OPENAI_API_VERSION,
)

# Load the embeddings CSV
df = pd.read_csv("embedded_news.csv")
df["embedding"] = df["embedding"].apply(eval).apply(np.array)
def embed_text(text):
    """Generate embedding for the user prompt"""
    response = client.embeddings.create(
        input=[text],
        model=AZURE_EMBEDDING_DEPLOYMENT
    )
    return np.array(response.data[0].embedding)


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