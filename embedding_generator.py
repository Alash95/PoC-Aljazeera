import openai
import numpy as np
import pandas as pd
import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_EMBEDDING_DEPLOYMENT")
AZURE_OPENAI_TYPE = os.getenv("AZURE_OPENAI_TYPE")

client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version=AZURE_OPENAI_API_VERSION,
)

def generate_embedding(text):
    clean_text = str(text).strip()
    if not clean_text:
        return []  # Return empty list if the string is empty
    response = client.embeddings.create(
        input=clean_text,
        model=AZURE_EMBEDDING_DEPLOYMENT
    )
    return response.data[0].embedding


def add_embeddings_to_df(df, text_column="Summary"):
    df["embedding"] = df[text_column].fillna("").apply(generate_embedding)
    return df

if __name__ == "__main__":
    from data_loader import load_csv_from_blob
    df = load_csv_from_blob()
    df = add_embeddings_to_df(df, text_column="Summary")
    df.to_csv("embedded_news_01.csv", index=False)
