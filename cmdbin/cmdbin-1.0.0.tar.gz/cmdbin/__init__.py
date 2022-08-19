def __clean_endpoint(endpoint: str) -> str:
    """
    guarantees that the endpoint ends with a "/"
    """
    if not endpoint.endswith("/"):
        endpoint += "/"
    return endpoint
