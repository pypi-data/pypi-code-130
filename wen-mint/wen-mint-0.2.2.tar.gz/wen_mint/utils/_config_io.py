from json import load, dump
from os.path import exists
from typing import Union


def load_config_file(config_path: str = 'config.json') -> dict[str, Union[str, int]]:
    """Loads a dictionary of API connection arguments from a config file.

    Args:
        config_path (str, optional): The path to the config json. Defaults to
            'config.json'.

    Returns:
        dict[str, Union[str, int]]: A dictionary of API connection arguments.
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        config = load(f)
    return config


def update_config_file(
    config_path: str = 'config.json',
    reddit_client_id: str = '',
    reddit_client_secret: str = '',
    reddit_refresh_token: str = '',
    reddit_redirect_url: str = '',
    twitter_bearer_token: str = '',
    ethereum_provider_url: str = '',
    ethereum_wait_milliseconds: int = None,
) -> None:
    """_summary_

    Args:
        config_path (str, optional): The path to the config json. Defaults to
            'config.json'.
        reddit_client_id (str, optional): The Reddit client ID. Defaults to ''.
        reddit_client_secret (str, optional): The Reddit client secret.
            Defaults to ''.
        reddit_refresh_token (str, optional): The Reddit refresh token.
            Defaults to ''.
        reddit_redirect_url (str, optional): If using the external script
            to obtain a Reddit refresh token, this url is where you will log
            on to Reddit to authorize with your credentials. Defaults to ''.
        twitter_bearer_token (str, optional): The bearer token used to connect.
            to the Twitter V2 API. Defaults to ''.
        ethereum_provider_url (str, optional): The http or websockets url that
            will connect to your web3 API of choice. Defaults to ''.
        ethereum_wait_milliseconds (int, optional): The minimum amount of
            time to wait in between ENS address requests. Defaults to None.
    """
    json_kwargs = {
        'Reddit_client_id': reddit_client_id,
        'Reddit_client_secret': reddit_client_secret,
        'Reddit_refresh_token': reddit_refresh_token,
        'Reddit_redirect_url': reddit_redirect_url,
        'Twitter_bearer_token': twitter_bearer_token,
        'Ethereum_provider_url': ethereum_provider_url,
        'Ethereum_wait_milliseconds': ethereum_wait_milliseconds,
    }

    if exists(config_path):
        config = load_config_file(config_path)
        config.update({key: value for key, value in json_kwargs.items() if value})
    else:
        config = json_kwargs
    with open(config_path, 'w', encoding='utf-8') as f:
        dump(config, f, indent=4)
