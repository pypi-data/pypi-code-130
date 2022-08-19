import os

from azure.storage.blob import BlobClient


def read_jsonlines_blob(blob: str, encoding: str = 'UTF-8',
                        attr: str = None, logging_enable: bool = True,
                        conn_str: str = os.getenv('AzureWebJobsStorage'),
                        container: str = os.getenv('AZCONTAINER_PATH')):
    """Reads jsonlines document from the specified blob.
    
    Args:
        blob (str): Blob name.
        container (str): Container path. Defaults to ``os.getenv('AZCONTAINER_PATH')``.
        conn_str (str): Azure connection string. Defaults to ``os.getenv('AzureWebJobsStorage')``.
        attr (str): Use this if you want to yield values only from a specific attribute from the document.
        encoding (str): Encoding type. Defaults to ``UTF-8``.
        logging_enable(bool) : If you want to enable logging or not. Defaults to ``True``.
        
    Yields:
        JSON Object or value from the specified attribute.
    """
    blob_client = BlobClient.from_connection_string(
        conn_str=conn_str,
        container_name=container,
        blob_name=blob,
        logging_enable=logging_enable)
    
    content = blob_client.download_blob().content_as_text(encoding=encoding).splitlines()
    
    if attr is not None and attr in content[0]:
        attr = f'"{attr}": "'
        
        for line in content:
            idx = line.find(attr)
            value = line[idx + len(attr):]
            idx = value.find('"')
            yield value[:idx]
    else:
        yield from content
