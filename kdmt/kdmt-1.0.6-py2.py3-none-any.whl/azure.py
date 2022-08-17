from azure.storage.blob import BlobServiceClient
from io import BytesIO

def upload_file(connect_str, container_name, local_file, blob_name):

    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    container_client=None
    if not blob_client:
        container_client = blob_service_client.create_container(container_name)
        # Create a blob client using the local file name as the name for the blob
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    print("\nUploading to Azure Storage as blob")

    # Upload the created file
    try:
        with open(local_file, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
    except Exception as e:
        raise e

    return container_client

def get_file(connect_str, container_name, blob_file):

    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    try:
        blob_client = blob_service_client.get_container_client(container=container_name)
    except Exception as e:
        raise e

    downloaded_buffer = blob_client.download_blob(blob_file).readall()

    inmemoryfile = BytesIO(downloaded_buffer)

    return inmemoryfile


def get_blob(connect_str, container_name, blob_file):

    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    try:
        blob_client = blob_service_client.get_container_client(container=container_name)
    except Exception as e:
        raise e

    downloaded_buffer = blob_client.download_blob(blob_file).readall()

    return downloaded_buffer