import pandas as pd
from azure.storage.blob import BlobServiceClient
import io
from config import BLOB_CONNECTION_STRING, BLOB_CONTAINER_NAME, BLOB_FILE_NAME


def load_csv_from_blob() -> pd.DataFrame:
    """
    Loads a CSV file from Azure Blob Storage into a Pandas DataFrame.
    """
    try:
        # Connect to blob storage
        blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)
        blob_client = blob_service_client.get_blob_client(container=BLOB_CONTAINER_NAME, blob=BLOB_FILE_NAME)
        
        # Download the blob as bytes
        blob_data = blob_client.download_blob().readall()
        df = pd.read_csv(io.BytesIO(blob_data))
        
        print(f"✅ Loaded {len(df)} rows from blob.")
        return df
    
    except Exception as e:
        print(f"❌ Failed to load data from blob: {e}")
        raise

if __name__ == "__main__":
    df = load_csv_from_blob()
    print(df.head())  # show first few rows

