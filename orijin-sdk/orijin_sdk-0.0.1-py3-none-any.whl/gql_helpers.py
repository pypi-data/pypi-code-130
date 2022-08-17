from . import types, mutations, queries
from .gql import useQueryAsOn, useMutationAsOn

def upload_sku(sku: types.UpdateSku, token: str, gql_endpoint: str = "https://staging.orijinplusserver.com/api/gql/query"):
    """Use GQL mutation.skuCreate
    
    Args:
        sku: (UpdateSku): The sku data to be uploaded
    
    Returns:
        New id of sku just uploaded.
    """
    r = useMutationAsOn(mutations.skuCreate, sku, token, gql_endpoint)
    try: 
        return r["data"]["skuCreate"]["id"]
    except:
        return

def upload_order(order: types.UpdateOrder, token: str, gql_endpoint: str = "https://staging.orijinplusserver.com/api/gql/query"):
    """Use GQL mutation.___Create
    
    Args:
        ___: (___): The ___ data to be uploaded
    
    Returns:
        New id of ___ just uploaded.
    """
    r = useMutationAsOn(mutations.orderCreate, order, token, gql_endpoint)
    try:
        return r["data"]["orderCreate"]["id"]
    except:
        return

def upload_container(container: types.CreateContainer, token: str, gql_endpoint: str = "https://staging.orijinplusserver.com/api/gql/query"):
    """Use GQL mutation.___Create
    
    Args:
        ___: (___): The ___ data to be uploaded
    
    Returns:
        True/False of success
    """
    r = useMutationAsOn(mutations.containerCreate, container, token, gql_endpoint)
    try:
        return r["data"]["containerCreate"]
    except:
        return

def upload_pallet(pallet: types.CreatePallet, token: str, gql_endpoint: str = "https://staging.orijinplusserver.com/api/gql/query"):
    """Use GQL mutation.___Create
    
    Args:
        ___: (___): The ___ data to be uploaded
    
    Returns:
        True/False of success
    """
    r = useMutationAsOn(mutations.palletCreate, pallet, token, gql_endpoint)

    try:
        return r["data"]["palletCreate"]
    except:
        return

def upload_carton(carton: types.CreateCarton, token: str, gql_endpoint: str = "https://staging.orijinplusserver.com/api/gql/query"):
    """Use GQL mutation.___Create
    
    Args:
        ___: (___): The ___ data to be uploaded
    
    Returns:
        True/False of success
    """
    r = useMutationAsOn(mutations.cartonCreate, carton, token, gql_endpoint)

    try:
        return r["data"]["cartonCreate"]
    except:
        return

def upload_product(product: types.UpdateProduct, token: str, gql_endpoint: str = "https://staging.orijinplusserver.com/api/gql/query"):
    """Use GQL mutation.___Create
    
    Args:
        ___: (___): The ___ data to be uploaded
    
    Returns:
        New id of ___ just uploaded.
    """
    r = useMutationAsOn(mutations.productCreate, product, token, gql_endpoint)
    try:
        return r["data"]["productCreate"]["id"]
    except:
        return
