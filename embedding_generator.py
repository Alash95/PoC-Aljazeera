import openai
import pandas as pd
from config import OPENAI_API_KEY, OPENAI_ENDPOINT, OPENAI_API_VERSION, EMBEDDING_DEPLOYMENT_NAME

openai.api_key = OPENAI_API_KEY
openai.api_base = OPENAI_ENDPOINT
openai.api_type = "azure"
openai.api_version = OPENAI_API_VERSION

def generate_embedding(text):
    response = openai.Embedding.create(
        input=[text],
        engine=EMBEDDING_DEPLOYMENT_NAME
    )
    return response["data"][0]["embedding"]

def add_embeddings_to_df(df, text_column="Summary"):
    df["embedding"] = df[text_column].fillna("").apply(generate_embedding)
    return df

if __name__ == "__main__":
    from data_loader import load_csv_from_blob
    df = load_csv_from_blob()
    df = add_embeddings_to_df(df, text_column="Summary")
    df.to_csv("embedded_news.csv", index=False)
