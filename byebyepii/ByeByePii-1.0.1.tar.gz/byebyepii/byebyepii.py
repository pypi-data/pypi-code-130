import hashlib
import json


def hashString(s: str) -> str:
    """
    Hash a string using SHA256

    Args:
        s: string to hash

    Returns:
        hashed string
    """
    if s:
        return hashlib.sha256(s.encode("utf-8")).hexdigest()
    return None


def hashPii(
    pii_dict: dict, keys_to_hash: list, subkeys_to_hash: list, verify: bool = True
) -> dict:
    """
    Hash the PII in the given dictionary.

    Args:
        pii_dict: The dictionary to hash.
        keys_to_hash: The keys to hash.
        subkeys_to_hash: The subkeys to hash.
        verify: Whether to verify the hash.

    Returns:
        A dictionary with the hashed PII.
    """
    if keys_to_hash:
        for key in keys_to_hash:
            if key in pii_dict:
                if isinstance(pii_dict[key], dict):
                    for subkey in subkeys_to_hash:
                        if subkey in pii_dict[key]:
                            pii_dict[key][subkey] = hashString(
                                json.dumps(pii_dict[key][subkey]),
                            )
                elif isinstance(pii_dict[key], list):
                    for item in pii_dict[key]:
                        for subkey in subkeys_to_hash:
                            if subkey in item:
                                item[subkey] = hashString(
                                    json.dumps(item[subkey]),
                                )
                else:
                    pii_dict[key] = hashString(json.dumps(pii_dict[key]))
    if verify:
        for key in keys_to_hash:
            if key in pii_dict:
                if isinstance(pii_dict[key], dict):
                    for subkey in subkeys_to_hash:
                        if subkey in pii_dict[key]:
                            assert len(pii_dict[key][subkey]) == 64
                elif isinstance(pii_dict[key], list):
                    for item in pii_dict[key]:
                        for subkey in subkeys_to_hash:
                            if subkey in item:
                                assert len(item[subkey]) == 64
                else:
                    assert len(pii_dict[key]) == 64
    return pii_dict


def analyzeDict(pii_dict: dict):
    """
    Analyze the given dictionary and return a list of keys that you'd like to be hashed.

    Args:
        pii_dict: The dictionary to analyze.

    Returns:
        key_list: A list of keys that you'd like to be hashed.
        subkey_list: A list of subkeys that you'd like to be hashed.
    """
    key_list = []
    subkey_list = []

    if pii_dict:
        for key in pii_dict:
            if isinstance(pii_dict[key], dict):
                for subkey in pii_dict[key]:
                    if subkey:
                        add_subkey = input(f"Add {key} - {subkey} to hash list? (y/n) ")
                        if add_subkey == "y":
                            key_list.append(key)
                            subkey_list.append(subkey)
            else:
                add_key = input(f"Add {key} to hash list? (y/n) ")
                if add_key == "y":
                    key_list.append(key)

    print(f"\nKeys to hash: {key_list}\nSubkeys to hash: {subkey_list}")
    return key_list, subkey_list
