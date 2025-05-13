import faiss
import numpy as np
import pandas as pd
import pickle
from typing import Tuple

def build_faiss_index(embeddings: list) -> faiss.IndexFlatL2:
    """
    Builds a FAISS index from a list of embedding vectors.

    Args:
        embeddings (list): List of embedding vectors (each a list of floats)

    Returns:
        faiss.IndexFlatL2: Trained FAISS index
    """
    array = np.array(embeddings).astype("float32")
    index = faiss.IndexFlatL2(array.shape[1])  # L2 distance
    index.add(array)
    return index


def save_faiss_index(index: faiss.IndexFlatL2, df: pd.DataFrame, path: str = "faiss_store"):
    """
    Saves FAISS index and associated metadata (pandas DataFrame).

    Args:
        index (faiss.IndexFlatL2): The FAISS index
        df (pd.DataFrame): DataFrame with at least 'Headline', 'Summary', 'URL', and 'embedding'
        path (str): Base path to save index and metadata
    """
    faiss.write_index(index, f"{path}/index.faiss")
    df.drop(columns=["embedding"]).to_pickle(f"{path}/metadata.pkl")


def load_faiss_index(path: str = "faiss_store") -> Tuple[faiss.IndexFlatL2, pd.DataFrame]:
    """
    Loads FAISS index and metadata.

    Returns:
        Tuple[faiss.IndexFlatL2, pd.DataFrame]: The FAISS index and metadata DataFrame
    """
    index = faiss.read_index(f"{path}/index.faiss")
    df = pd.read_pickle(f"{path}/metadata.pkl")
    return index, df

if __name__ == "__main__":
    from data_loader import load_csv_from_blob
    from embedding_generator import add_embeddings_to_df

    df = load_csv_from_blob()
    df = add_embeddings_to_df(df, text_column="Summary")

    import os
    os.makedirs("faiss_store", exist_ok=True)

    from vector_store import build_faiss_index, save_faiss_index

    index = build_faiss_index(df["embedding"].tolist())
    save_faiss_index(index, df)
    print("FAISS index and metadata saved.")
