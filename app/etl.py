import dlt
import requests
import os
import shutil

# IMDb dataset URLs
IMDB_DATASETS = {
    "name_basics": "https://datasets.imdbws.com/name.basics.tsv.gz",
    "title_akas": "https://datasets.imdbws.com/title.akas.tsv.gz",
    "title_basics": "https://datasets.imdbws.com/title.basics.tsv.gz",
    "title_crew": "https://datasets.imdbws.com/title.crew.tsv.gz",
    "title_episode": "https://datasets.imdbws.com/title.episode.tsv.gz",
    "title_principals": "https://datasets.imdbws.com/title.principals.tsv.gz",
    "title_ratings": "https://datasets.imdbws.com/title.ratings.tsv.gz"
}

# Directory where the temp files will be downloaded
TEMP_DIR = "./temp_dl"

# Ensure the temp directory exists
os.makedirs(TEMP_DIR, exist_ok=True)


# Function to download IMDb file and save locally to the custom temp directory
def download_imdb_file(url: str, file_name: str):
    """Download IMDb file from the URL and save it in the project temp directory."""
    file_path = os.path.join(TEMP_DIR, file_name)

    # Download file and save it to the temp directory
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Ensure the request was successful

    with open(file_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

    return file_path


# DLT resource to yield IMDb data from local temp directory
@dlt.resource(name="imdb_data", write_disposition="replace")
def my_filesystem_pipeline_imdb():
    """Yield IMDb data from local temp directory after download."""
    for dataset_name in IMDB_DATASETS.keys():
        # Locate the file in the temp directory
        file_name = f"{dataset_name}.tsv.gz"
        local_file_path = os.path.join(TEMP_DIR, file_name)

        # Check if the file exists in the temp directory
        if os.path.exists(local_file_path):
            # Yield the file's path (for loading to MinIO or other destinations)
            yield {"file_name": file_name, "local_file_path": local_file_path}
        else:
            print(f"File {file_name} not found in {TEMP_DIR}.")


# Source function to combine all IMDb resources
@dlt.source(name="imdb_pipeline_source")
def my_filesystem_pipeline_source():
    """Group all IMDb data into one source."""
    return my_filesystem_pipeline_imdb()


def load_stuff() -> None:
    # Specify the pipeline name, destination and dataset name when configuring pipeline
    p = dlt.pipeline(
        pipeline_name='my_filesystem_pipeline',
        destination='filesystem',
        dataset_name='imdb_data',
        progress="log"
    )

    # Run the pipeline to load data from the local temp files to MinIO
    load_info = p.run(my_filesystem_pipeline_source())

    # Pretty print the information on data that was loaded
    print(load_info)  # noqa: T201

    # Cleanup the temp directory after successful load
    cleanup_temp_files()


def cleanup_temp_files():
    """Delete the temporary files after loading them to MinIO."""
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
        print(f"Temporary files in {TEMP_DIR} deleted.")


if __name__ == "__main__":
    load_stuff()
