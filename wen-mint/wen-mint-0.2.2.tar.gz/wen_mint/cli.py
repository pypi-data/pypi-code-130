import argparse
from typing import Any
from warnings import simplefilter

from .__version__ import __version__
from . import (
    update_config_file,
    obtain_reddit_refresh_token,
    AddressConverter,
    CSVExtractor,
    RedditExtractor,
    TwitterExtractor,
)


def extract_from_csv(args: object, api: str):
    """Integrates the CLI with the csv extraction classes.

    Args:
        args (object): Parsed arguments object from argparse.
        api (str): Switches functionality to handle either the "csv_extractor"
            class or the "address_converter" class.
    """
    kwargs = {'verbose': args.verbose}
    update_kwargs_from_loop(kwargs, {'config_path': args.config_path})
    if api == 'csv_extractor':
        update_kwargs_from_loop(
            kwargs,
            {
                'post_column': args.post_column,
                'user_column': args.user_column,
                'low_precision': args.low_precision,
            },
        )
        scraper = CSVExtractor(**kwargs)
        scrape_kwargs = {
            'input_arg': args.input,
            'uniform_addresses': args.uniform_addresses,
        }
        scrape_func = scraper.extract_from_csv

    elif api == 'address_converter':
        update_kwargs_from_loop(kwargs, {'address_column': args.address_column})
        scraper = AddressConverter(**kwargs)
        scrape_kwargs = {'input_path': args.input}
        scrape_func = scraper.process_addresses
    else:
        raise ValueError('api string must specify "reddit" or "twitter"')

    update_kwargs_from_loop(
        scrape_kwargs, {'output_path': args.output, 'trim_random': args.random_sample}
    )
    scrape_func(**scrape_kwargs)
    if args.output is None:
        print(scraper)


def extract_from_scrape(args: object, api: str) -> None:
    """Integrates the CLI with the reddit and twitter scraping classes.

    Args:
        args (object): args (object): Parsed arguments object from argparse.
        api (str): Switches functionality to handle either the "reddit" class
            or the "twitter" class.

    Raises:
        ValueError: When "reddit" or "twitter" is not selected with the api
        argument.
    """
    kwargs = {'verbose': args.verbose}
    update_kwargs_from_loop(kwargs, {'config_path': args.config_path})

    if api == 'reddit':
        scraper = RedditExtractor(**kwargs)
        kwargs = {
            'input_arg': args.post_id,
            'uniform_addresses': args.uniform_addresses,
        }
    elif api == 'twitter':
        scraper = TwitterExtractor(**kwargs)
        kwargs = {
            'input_arg': args.conversation_id,
            'uniform_addresses': args.uniform_addresses,
            'following': args.following,
            'liked_only': args.liked_only,
            'retweeted_only': args.retweeted_only,
        }
    else:
        raise ValueError('api string must specify "reddit" or "twitter"')

    update_kwargs_from_loop(
        kwargs, {'output_path': args.output, 'trim_random': args.random_sample}
    )
    scraper.scrape_addresses(**kwargs)
    if args.output is None:
        print(scraper)


def get_refresh_token(args: object):
    """Integrates the CLI with the obtain_reddit_refresh_token function.

    Args:
        args (object): Parsed arguments object from argparse.
    """
    kwargs = {'manual_scopes': args.manual_scopes}
    update_kwargs_from_loop(kwargs, {'config_path': args.config_path})
    obtain_reddit_refresh_token(**kwargs)


def config_generation(args: object):
    """Integrates the CLI with the update_config_file function.

    Args:
        args (object): Parsed arguments object from argparse.
    """
    kwargs = {}
    update_kwargs_from_loop(
        kwargs,
        {
            'config_path': args.output,
            'reddit_client_id': args.reddit_client_id,
            'reddit_client_secret': args.reddit_client_secret,
            'reddit_refresh_token': args.reddit_refresh_token,
            'reddit_redirect_url': args.reddit_redirect_url,
            'twitter_bearer_token': args.twitter_bearer_token,
            'ethereum_provider_url': args.ethereum_provider,
            'ethereum_wait_milliseconds': args.ethereum_wait,
        },
    )
    update_config_file(**kwargs)


def update_kwargs_from_loop(kwargs: dict[str, Any], param_dict: dict[str, Any]):
    """Allows function defaults to stay intact when flags are unspecified by
    creating a dict of kwargs for only those that contain set values.

    Args:
        kwargs (dict[str, Any]): A dictionary of output keyword arguments to
            pass to the function that will be updated with set values.
        param_dict (dict[str, Any]): A dictionary of keys and values to
            extract when set obtained by argparse inputs.
    """

    for key, value in param_dict.items():
        if value is not None:
            kwargs.update({key: value})


def run_cmd_line():
    """Runs the argparse CLI functions."""

    # web3.py currently does not seem to have a way to suppress a specific
    # future warning. Remove once resolved.
    simplefilter(action='ignore', category=FutureWarning)

    parser = argparse.ArgumentParser(
        prog='Wen Mint',
        description='A command line interface for extracting Ethereum addresses from Reddit and Twitter',
    )
    parser.add_argument(
        '--version', version=f'%(prog)s {__version__}', action='version'
    )

    subparsers = parser.add_subparsers(help='Commands', dest='command')
    config = subparsers.add_parser(
        'generate_config',
        help='Generates a config file with API authentication credentials captured from the optional arguments',
    )
    reddit = subparsers.add_parser(
        'reddit', help='Scrapes addresses from a comment thread on Reddit'
    )
    twitter = subparsers.add_parser(
        'twitter', help='Scrapes addresses from replies to a post on Twitter'
    )
    csv_extractor = subparsers.add_parser(
        'csv', help='Extracts addresses from a generated csv file.'
    )
    address_converter = subparsers.add_parser(
        'convert_addresses',
        help='Opens a csv of already scraped Ethereum adddresses and converts them to hexadecimal hashes.',
    )
    refresh = subparsers.add_parser(
        'get_reddit_refresh_token',
        help='Facilitates obtaining a reddit refresh token using the reddit redirect url specified in the config file',
    )

    for subparser in [refresh, reddit, twitter, csv_extractor, address_converter]:
        subparser.add_argument(
            '--config_path',
            '-c',
            help='The path to the config json',
            metavar='FILEPATH',
            type=str,
        )

    for subparser in [reddit, twitter, csv_extractor, address_converter]:
        subparser.add_argument(
            '--output',
            '-o',
            help='The path to the output csv. If empty, unique addresses will only be printed',
            metavar='FILEPATH',
            type=str,
        )
        subparser.add_argument(
            '--random_sample',
            '-r',
            help='Use this to optionally random sample a specific amount from unique addresses after a filter on one post (with address) per user is applied. If unspecified, results are untrimmed.',
            metavar='AMOUNT',
            type=int,
        )
        subparser.add_argument(
            '--verbose',
            '-v',
            help='Verbose mode for detailed messages.',
            action='store_true',
        )
    for subparser in [reddit, twitter, csv_extractor]:
        subparser.add_argument(
            '--uniform_addresses',
            '-u',
            help='Use this to replace all instances of ENS addresses with the hexadecimal hash that they point to. (Requires and "Ethereum_provider_url" to be set in the config file) ',
            action='store_true',
        )

    config.add_argument(
        '--output',
        '-o',
        help='The path to the output json. If it already exists it will be loaded first and overwritten using only specified flags.',
        metavar='FILEPATH',
        type=str,
    )
    config.add_argument(
        '--reddit_client_id',
        help='The client ID for the Reddit API',
        metavar='ID',
        type=str,
    )
    config.add_argument(
        '--reddit_client_secret',
        help='The client secret for the Reddit API',
        metavar='SECRET',
        type=str,
    )
    config.add_argument(
        '--reddit_refresh_token',
        help='The refresh token for the Reddit API',
        metavar='TOKEN',
        type=str,
    )
    config.add_argument(
        '--reddit_redirect_url',
        help='When a new refresh token is required, use this to match the url you provided in your app settings',
        metavar='URL',
        type=str,
    )
    config.add_argument(
        '--twitter_bearer_token',
        help='The bearer token for the Twitter API',
        metavar='TOKEN',
        type=str,
    )
    config.add_argument(
        '--ethereum_provider',
        help='The url of the ethereum provider for ENS address lookup (supports http or websockets)',
        metavar='URL',
        type=str,
    )
    config.add_argument(
        '--ethereum_wait',
        help='The amount of time in milliseconds to wait in between ENS requests if converting ENS addresses to hashes',
        metavar='MS',
        type=int,
    )

    refresh.add_argument(
        '--manual_scopes',
        help='Enable this flag to be prompted for the desired scopes for the token',
        action='store_true',
    )

    reddit.add_argument(
        'post_id',
        help='The ID of the Reddit post (without prefix)',
        metavar='ID',
        type=str,
    )

    twitter.add_argument(
        'conversation_id',
        help='The conversation ID of the Twitter thread',
        metavar='ID',
        type=int,
    )

    twitter.add_argument(
        '--following',
        help='Eliminate results that do not match the input usernames or user IDs. Usernames are allowed for convenience must contain an @ symbol before them for the program to distinguish them from the ids. (Uses additional api calls to get the follow list with one extra if any usernames need to be converted to user IDs)',
        metavar='USER',
        type=str,
        nargs='+',
    )

    twitter.add_argument(
        '--liked_only',
        help='Enable this to restrict results only to users that have given a like to the giveaway. (Uses additional API calls to see who liked the post)',
        action='store_true',
    )

    twitter.add_argument(
        '--retweeted_only',
        help='Enable this to restrict results only to users that have given a retweet to the giveaway. (Uses additional API calls to see who retweeted the post)',
        action='store_true',
    )

    csv_extractor.add_argument(
        'input', help='The path to the input CSV', metavar='FILEPATH', type=str
    )
    csv_extractor.add_argument(
        '--low_precision',
        help='Use this to be extra aggressive about catching addresses. Not reccomended unless the input csv has done something wrong like stripping out newline characters',
        action='store_true',
    )
    csv_extractor.add_argument(
        '--post_column',
        help='Use this to set the default name for the post column to match the input csv',
        metavar='COLUMN',
        type=str,
    )
    csv_extractor.add_argument(
        '--user_column',
        help='Use this to set the default name for the user column to match the input csv',
        metavar='COLUMN',
        type=str,
    )
    address_converter.add_argument(
        'input', help='The path to the input CSV', metavar='FILEPATH', type=str
    )
    address_converter.add_argument(
        '--address_column',
        help='Use this to set the default name for the address column to match the input csv',
        metavar='COLUMN',
        type=str,
    )

    args = parser.parse_args()

    if args.command == 'generate_config':
        config_generation(args)
    elif args.command == 'get_reddit_refresh_token':
        get_refresh_token(args)
    elif args.command == 'reddit':
        extract_from_scrape(args, api='reddit')
    elif args.command == 'twitter':
        extract_from_scrape(args, api='twitter')
    elif args.command == 'csv':
        extract_from_csv(args, api='csv_extractor')
    elif args.command == 'convert_addresses':
        extract_from_csv(args, api='address_converter')


def main():
    run_cmd_line()


if __name__ == '__main__':
    main()
