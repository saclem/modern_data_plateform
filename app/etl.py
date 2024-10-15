import os
import requests
import shutil
import boto3
from botocore.exceptions import NoCredentialsError

IMDB_DATASETS = {
    "name_basics": "https://datasets.imdbws.com/name.basics.tsv.gz",
    "title_akas": "https://datasets.imdbws.com/title.akas.tsv.gz",
    "title_basics": "https://datasets.imdbws.com/title.basics.tsv.gz",
    "title_crew": "https://datasets.imdbws.com/title.crew.tsv.gz",
    "title_episode": "https://datasets.imdbws.com/title.episode.tsv.gz",
    "title_principals": "https://datasets.imdbws.com/title.principals.tsv.gz",
    "title_ratings": "https://datasets.imdbws.com/title.ratings.tsv.gz"
}

TEMP_DIR = "./temp_dl"

MINIO_BUCKET = "imdb"
MINIO_ACCESS_KEY = "admin"
MINIO_SECRET_KEY = "password"
MINIO_ENDPOINT_URL = "http://localhost:9000"

os.makedirs(TEMP_DIR, exist_ok=True)

s3_client = boto3.client('s3',
                         aws_access_key_id=MINIO_ACCESS_KEY,
                         aws_secret_access_key=MINIO_SECRET_KEY,
                         endpoint_url=MINIO_ENDPOINT_URL)


def download_imdb_file(url: str, file_name: str):
    """Download IMDb file from the URL and save it in the project temp directory."""
    file_path = os.path.join(TEMP_DIR, file_name)

    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(file_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

    print(f"Downloaded {file_name} to {file_path}")
    return file_path


# Function to upload file to MinIO
def upload_to_minio(file_path, file_name):
    """Upload a file to the specified MinIO bucket."""
    try:
        s3_client.upload_file(file_path, MINIO_BUCKET, file_name)
        print(f"Uploaded {file_name} to MinIO bucket {MINIO_BUCKET}")
    except FileNotFoundError:
        print(f"File {file_name} not found for upload.")
    except NoCredentialsError:
        print("Credentials not available for MinIO")


def process_files():
    """Download file & upload file to minio"""
    for dataset_name, url in IMDB_DATASETS.items():
        file_name = f"{dataset_name}.tsv.gz"
        local_file_path = download_imdb_file(url, file_name)
        upload_to_minio(local_file_path, file_name)


def cleanup_temp_files():
    """Delete the temporary files after loading them to MinIO."""
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
        print(f"Temporary files in {TEMP_DIR} deleted.")


if __name__ == "__main__":
    process_files()
    cleanup_temp_files()
