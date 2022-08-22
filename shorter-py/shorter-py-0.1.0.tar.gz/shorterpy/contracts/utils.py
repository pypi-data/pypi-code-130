import pkgutil


def get_abi(contract_name: str):
    """
    Get the abi for a contract
    Args:
        contract_name: The name of the contract
    """
    data = pkgutil.get_data(__name__, f"./abi/{contract_name}.json")
    if data is not None:
        return data.decode("utf-8")
    else:
        raise Exception(f"{contract_name} not found")
