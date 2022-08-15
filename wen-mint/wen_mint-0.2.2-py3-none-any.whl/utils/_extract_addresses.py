import datetime as dt
import functools
from lib2to3.pytree import convert
import os
import re
import time
from typing import Any, Callable, Union

import pandas as pd

from ._api_conn import (
    create_reddit_api_conn,
    connect_to_tweepy_api_v2,
    connect_to_ethereum_provider_url,
    load_config_file,
)


def extract_and_output(func: Callable) -> object:
    """A decorator to modify the Ethereum address extraction methods of child
    classes of GeneralExtractor.

    Args:
        func (Callable): This affects the function where the decorator is
            applied.

    Returns:
        object: A pandas DataFrame with Ethereum addresses appended.
    """

    @functools.wraps(func)
    def wrapper(
        self,
        input_arg: Union[int, str],
        output_path: str = None,
        trim_random: int = None,
        uniform_addresses: bool = False,
        *args,
        **kwargs,
    ) -> object:
        df = func(self, input_arg, output_path, trim_random, *args, **kwargs)
        df[self.address_column] = replace_text_with_addresses(
            df, self.post_column, whats_a_newline=self.low_precision
        )
        self.df = df
        if uniform_addresses:
            self._trim_column = self.hash_column
            self.df = self.replace_ens_addresses_with_hashes()
            self.df = self.df[self.final_columns]
        else:
            self._trim_column = self.address_column
            self.df = self.df[
                [column for column in self.final_columns if column != self.hash_column]
            ]
        if trim_random:
            self.df = self.sample_results(trim_random)
        if output_path is not None:
            self._verbose_message(f'Saving CSV to {output_path}')
            self.df.to_csv(output_path)
        return self.df

    return wrapper


def replace_text_with_addresses(
    df: object, post_column: str, whats_a_newline: bool = False
) -> object:
    """Extracts Ethereum addresses from a post column.

    Args:
        df (object): A pandas dataframe.
        post_column (str): The name of the column that contains the text data
            to search for addresses.
        whats_a_newline (bool, optional): Use this in situations when you are
            stuck with an input where newline characters have been dropped
            without replacement. Defaults to True.

    Returns:
        object: A pandas series containing the extracted Ethereum addresses.
    """
    capture_group_label = 'capture_group'
    if whats_a_newline:
        address_regex = re.compile(
            r'\b(?P<' + capture_group_label + r'>\w+(?:[\-\.]\w+)*\.eth|0x[\da-f]{40})',
            flags=re.I,
        )
    else:
        address_regex = re.compile(
            r'(?<!\S)(?:"|\()?\b(?P<'
            + capture_group_label
            + r'>\w+(?:[\-\.]\w+)*\.eth|0x[\da-f]{40})\b',
            flags=re.I,
        )
    return df[post_column].str.extract(address_regex)[capture_group_label].str.lower()


def create_ens_to_address_hash_dict(
    ens_addresses: list[str], ns: object, wait_ms: int = None
) -> dict[str, str]:
    """Creates a dictionary pointing to the ethereum addresses of a list
    of ENS strings.

    Args:
        ens_addresses (list[str]): A list of ENS addresses to convert.
        ns (object): An authenticated web3.py ENS object.
        wait_ms (int, optional): Minimum amount of wait time in between
            requests. Defaults to None.

    Returns:
        dict[str, str]: A dictionary of ens addresses and mapped to their
        hexidecimal address hashes.
    """

    if not ens_addresses or len(ens_addresses) == 0:
        return {}
    wait = dt.timedelta(milliseconds=wait_ms) if wait_ms is not None else None
    request_time = dt.datetime.now()
    ens_dict = {ens_addresses[0]: ns.address(name=ens_addresses.pop(0))}

    for ens in ens_addresses:
        # Rate limiting is not built into web3.py so it's done manually here
        if wait is not None and dt.datetime.now() - request_time < wait:
            remainder = request_time + wait - dt.datetime.now()
            time.sleep(remainder.total_seconds())
        request_time = dt.datetime.now()
        ens_dict[ens] = ns.address(name=ens)
    return ens_dict


class GeneralExtractor:
    """Base class for Ethereum address extractor classes."""

    def __init__(self, config_path: str = 'config.json', verbose: bool = False) -> None:
        """Common initializations for all child Ethereum address scraper classes.

        Args:
            config_path (str, optional): The path to the config json. Defaults
                to 'config.json'.
            verbose (bool, optional): Verbose output. Defaults to False.
        """
        self.client = None
        self._response = None
        self._ns = None
        self._ns_wait = None

        self.verbose = verbose

        self.id_column = 'ID'
        self.post_column = 'Post Text'
        self.address_column = 'Address'
        self.hash_column = 'Address Hash'
        self.user_column = 'Username'
        self.user_id_column = 'User ID'
        self.created_column = 'Created'

        self._trim_column = self.address_column

        self.final_columns = [
            self.user_id_column,
            self.user_column,
            self.hash_column,
            self.address_column,
            self.post_column,
            self.created_column,
        ]

        self.df = None

        if os.path.exists(config_path):
            self._initialize_ens(config_path)

    def __repr__(self) -> str:
        """Determines how the object is displayed in string format.

        Returns:
            str: A string with some basic info and the extracted addresses.
        """
        output = 'Ethereum Address Extractor: '
        if self.df is None:
            return output + 'Scraping uninilitialized.'
        else:
            return output + self._get_address_string()

    def __str__(self) -> str:
        """Determines how the object appears when printed.

        Returns:
            str: A string of space seperated extracted addresses.
        """
        return '' if self.df is None else self._get_address_string()

    def _verbose_message(self, message: str):
        """Optionally prints a message if the object is verbose enabled.

        Args:
            message (str): The message to print if in verbose mode.
        """
        if self.verbose:
            print(message)

    def _initialize_ens(self, config_path: str = 'config.json') -> None:
        """Creates an attribute that contains the authenticated ENS object
        object for ENS hex substitution.

        Args:
            config_path (str, optional): The path to the config json. Defaults
                to 'config.json'.
        """
        config = load_config_file(config_path)
        if config['Ethereum_provider_url']:
            self._ns_wait = config['Ethereum_wait_milliseconds']
            self._ns = connect_to_ethereum_provider_url(config_path)

    def _trim_results(self) -> object:
        """Reduces the scraped dataframe to rows that contain addresses,
        with no duplicates across addresses and users.

        Returns:
            object: A Pandas DataFrame with incompletes and duplicates
            dropped.
        """
        if self.df is None:
            return
        if not self.verbose:
            return (
                self.df.dropna(subset=[self._trim_column])
                .drop_duplicates(subset=[self._trim_column])
                .drop_duplicates(subset=self.user_column, keep='last')
            )
        if self.verbose:
            dropped = self.df[self._trim_column].isna()
            if dropped.any():
                self._verbose_message(
                    f'{dropped.sum()} rows with no addresses dropped.'
                )
            df = self.df[~dropped]
            dropped = df[self._trim_column].duplicated()
            if dropped.any():
                self._verbose_message(f'{dropped.sum()} duplicate addresses dropped.')
            df = df[~dropped]
            dropped = df[self.user_column].duplicated(keep='last')
            if dropped.any():
                self._verbose_message(
                    f'Duplicate addresses detected from {df[self.user_column][dropped].unique().tolist()}'
                )
            return df[~dropped]

    def _get_address_list(self) -> list[str]:
        """Extracts list of addresses that have been trimmed from the scraped
        DataFrame.

        Returns:
            list[str]: A list of Ethereum addresses.
        """
        if self.df is not None:
            return self._trim_results()[self._trim_column].to_numpy().tolist()

    def _get_address_string(self) -> str:
        """Extracts a space seperated string of Ethereum addresses that have
        been trimmed from the scraped dataframe.

        Returns:
            str: Ethereum addresses seperated by a single space.
        """
        if self.df is not None:
            return ' '.join(self._get_address_list())

    def replace_ens_addresses_with_hashes(self) -> object:
        """After extracting the addresses, this function will convert all
        ens's to their hexadecimal hashes if an Ethereum provider url is
        present in the config file.

        Returns:
            object: A pandas DataFrame where all ENS addresses have been
            replaced with hexadecimal hashes.
        """
        if self.df is None:
            return
        df = self.df.copy()
        if df.empty or df[self.address_column].isna().all():
            df[self.hash_column] = None
            return df
        elif self._ns is None:
            raise ValueError(
                'Cannot convert ENS addresses without a valid "Ethereum_provider_url" in the config'
            )
        is_ens = df[self.address_column].str.endswith('.eth', na=False)
        # List of all ens addresses
        address_key = df[is_ens][self.address_column].dropna().unique().tolist()
        # A dictionary with the original list mapped to the hashes found online.
        self._verbose_message(f'Converting ENS addresses to hexadecimal hashes.')
        address_key = create_ens_to_address_hash_dict(
            address_key, self._ns, self._ns_wait
        )
        # The original hashes will be mapped to themselves.
        hashes = df[~is_ens][self.address_column].dropna().unique()
        address_key.update(dict(zip(hashes, hashes)))
        address_key = pd.Series(address_key).rename(self.hash_column).str.lower()
        df[self.hash_column] = df.join(address_key, how='left', on=self.address_column)[
            self.hash_column
        ]
        if self.verbose:
            missing = ~df[self.address_column].isna() & df[self.hash_column].isna()
            if missing.any():
                missing = df[missing][self.address_column]
                self._verbose_message(
                    f'Hashes for {missing.unique().tolist()} not found.'
                )
        return df

    def sample_results(self, n: int) -> object:
        """Performs a random sample of the scraped data after it has been trimmed
        to exclude missing addresses and duplicates.

        Args:
            n (int): The size of the sample (if too big it will return the
                remaining length after trimming)

        Returns:
            object: A sample of n rows from the trimmed DataFrame
        """
        if self.df is None:
            return None
        reduced = self._trim_results()
        rows = reduced.shape[0]
        if n >= rows:
            self._verbose_message(
                f'Sample size of {n} is greater than the remaining {rows} replies.'
            )
            return reduced
        else:
            # To avoid the scenario of someone gaming giveaways by exploiting
            # the pseudorandomness, the random state is dependant on the time
            # that the function is run.
            random_state = int(dt.datetime.now().timestamp()) % 100000
            self._verbose_message(
                f'Sample size of {n} taken from the remaining {rows} replies.'
            )
            return reduced.sample(n=n, random_state=random_state)


class RedditExtractor(GeneralExtractor):
    """Class that scrapes for Ethereum address comments on a Reddit post using
    PRAW and extracts them.
    """

    def __init__(self, config_path: str = 'config.json', verbose: bool = False) -> None:
        """Initializes the Reddit scraper and extractor object.

        Args:
            config_path (str, optional): The path to the config json. Defaults
                to 'config.json'.
            verbose (bool, optional): Verbose output. Defaults to False.
        """
        super().__init__(config_path, verbose)
        self.low_precision = False
        self._initialize_client(config_path)

    def _initialize_client(self, config_path: str = 'config.json') -> None:
        """Creates an attribute that contains the authenticated PRAW Reddit
        object for scraping.

        Args:
            config_path (str, optional): The path to the config json. Defaults
                to 'config.json'.
        """
        self._verbose_message('Initializing connection to the Reddit API')
        self.client = create_reddit_api_conn(config_path)

    @extract_and_output
    def scrape_addresses(
        self,
        post_id: str,
        output_path: str = None,
        trim_random: int = None,
        uniform_addresses: bool = False,
    ) -> object:
        """Scrapes for comments on a Reddit post using PRAW to a DataFrame,
        adding a column for the extracted Ethereum Addresses.

        Args:
            post_id (str): The post id to scrape for Reddit comments.
            output_path (str, optional): If provided, this will output a csv
                of the scrape with a column containing the extracted Ethereum
                address. Defaults to None.
            trim_random (int, optional): If selected, this will trim the
                output to a random selection of the amount specified across
                unique (and one address per user). Defaults to None.
            uniform_addresses (bool, optional): Whether or not to replace the
                ENS addresses with the hexadecimal hashes that they point to.
                Requires an api connection to an ethereum provider. Defaults
                to False.

        Returns:
            object: A Pandas DataFrame of the scrape and the Ethereum
            addresses.
        """
        self._verbose_message('Scraping from Reddit')
        self._response = self.client.submission(post_id)
        self._response.comments.replace_more(limit=None)

        df = pd.DataFrame(
            [
                [
                    comment.id,
                    comment.author_fullname,
                    comment.author,
                    comment.body,
                    comment.created_utc,
                ]
                for comment in self._response.comments.list()
                if comment.author is not None
            ]
        )
        df.columns = [
            self.id_column,
            self.user_id_column,
            self.user_column,
            self.post_column,
            self.created_column,
        ]
        df = df.set_index(self.id_column, drop=True).sort_index()
        df[self.created_column] = pd.to_datetime(df[self.created_column], unit='s')

        return df


class TwitterExtractor(GeneralExtractor):
    def __init__(self, config_path: str = 'config.json', verbose: bool = False) -> None:
        """Initializes the Twitter scraper and extractor object.

        Args:
            config_path (str, optional): The path to the config json. Defaults
                to 'config.json'.
            verbose (bool, optional): Verbose output. Defaults to False.
        """
        super().__init__(config_path, verbose)
        self.low_precision = False
        self._initialize_client(config_path)

    def _initialize_client(self, config_path: str = 'config.json') -> None:
        """Creates an attribute that contains the authenticated Tweepy client
        object that will scrape using the V2 API.

        Args:
            config_path (str, optional): The path to the config json. Defaults
                to 'config.json'.
        """
        self._verbose_message('Initializing connection to the Twitter API')
        self.client = connect_to_tweepy_api_v2(config_path)

    def _extract_tweet_fields(self) -> list[tuple[int, str, int, object]]:
        """Extracts specific Tweet data from a Tweepy response object.

        Returns:
            list[tuple[int, str, int, object]]: A list containing the relevant
            Tweet data extracted from the Tweepy response object.
        """
        data = self._response.data
        if data is None:
            return []
        return [
            (tweet.id, tweet.text, tweet.author_id, tweet.created_at) for tweet in data
        ]

    def _extract_user_fields(self) -> list[tuple[int, str]]:
        """Extracts specific user data from the "includes" section of a
        Tweepy response object.

        Returns:
            list[tuple[int, str]]: A list containing user ids and usernames
                from the search.
        """
        data = self._response.includes['users']
        if data is None:
            return []
        return [(user.id, user.username) for user in data]

    def _extract_ids(self) -> list[tuple[int]]:
        """Extracts id fields from the data section of a Tweepy response object

        Returns:
            list[tuple[int]]: The relevant user ids.
        """
        data = self._response.data
        if data is None:
            return []
        return [(item.id,) for item in data]

    def _extract_user_ids(self) -> list[tuple[int]]:
        """Extracts id fields from the data section of a Tweepy response object

        Returns:
            list[tuple[int]]: The relevant user ids.
        """
        data = self._response.data
        if data is None:
            return []
        return [(item.author_id,) for item in data]

    def _update_query(self, query: str) -> None:
        """The Twitter V2 API search fields are a bit cumbersome, most of the
        parameters are stored in an attribute that contains them as keyword
        arguments. This function will update the dictionary to include
        information about the actual search query.

        Args:
            query (str): The Twitter API V2 seach query text.
        """
        self.kwargs.update({'query': query})

    def _get_paginated_replies(
        self,
        kwargs: dict[str, Any],
        scrape_func: Callable,
        extraction_funcs: tuple[Callable, ...],
        paginated_token_name: list = ['next_token'],
    ) -> tuple[list[tuple[Any, ...]], ...]:
        """Extracts results from a Twitter search through pagination until Twitter
        returns no further results from a query.

        Args:
            kwargs (dict[str, Any]): The keyword arguments for the search.
            extraction_funcs (tuple[Callable]): A tuple of the extraction
                functions used.

        Returns:
            tuple[list[tuple[Any, ...]], ...]:
            Lists containing the combined data extracted from each section of
            the paginated search.
        """
        output = tuple([] for _ in range(len(extraction_funcs)))
        self._response = scrape_func(**kwargs)
        next_token = self._response.meta.get('next_token', None)
        for func, result in zip(extraction_funcs, output):
            result.extend(func())
        if not next_token:
            return output

        while next_token is not None:
            self._response = scrape_func(**{paginated_token_name: next_token}, **kwargs)
            for func, result in zip(extraction_funcs, output):
                result.extend(func())
            next_token = self._response.meta.get('next_token', None)
        return output

    def _get_lists_from_tweets(
        self, conversation_id: Union[str, int]
    ) -> tuple[list[tuple[Any, ...]], ...]:
        """Executes the main tweet search getting all results through the pagination.

        Args:
            conversation_id (Union[str, int]): The conversation ID for the
                Twitter thread

        Returns:
            tuple[list[tuple[Any, ...]], ...]: The resulting tweet and user data.
        """
        kwargs = {
            'query': f'conversation_id:{conversation_id}',
            'tweet_fields': ['author_id', 'created_at'],
            'user_fields': ['username'],
            'expansions': ['author_id'],
            'max_results': 100,
        }
        self._verbose_message('Scraping Tweets with user data from Twitter.')
        scrape_func = self.client.search_recent_tweets
        extraction_funcs = (self._extract_tweet_fields, self._extract_user_fields)
        paginated_token_name = 'next_token'
        return self._get_paginated_replies(
            kwargs, scrape_func, extraction_funcs, paginated_token_name
        )

    def _get_list_from_likes_retweets_followers(
        self, tweet_id: Union[str, int], kind: str
    ) -> list[tuple[Any, ...]]:
        """Executes an additional tweet search getting all results through the
        pagination for "likes" "retweets" or "followers".

        Args:
            tweet_id (int): (Union[str, int]): The Tweet id to get matches for.
            kind (str): The type of search to execute. can be "likes", "retweets" or "followers"

        Returns:
            list[tuple[Any, ...]: A list of user ids that match the search.
        """
        kwargs = {
            'id': tweet_id,
            'max_results': 100,
        }
        if kind == 'likes':
            self._verbose_message('Scraping likes from Twitter.')
            scrape_func = self.client.get_liking_users
        elif kind == 'retweets':
            self._verbose_message('Scraping retweets from Twitter.')
            scrape_func = self.client.get_retweeters
        elif kind == 'followers':
            self._verbose_message('Scraping followers from Twitter.')
            kwargs.update({'max_results': 1000})
            scrape_func = self.client.get_users_followers
        else:
            raise ValueError('Must choose a kind of "likes", "tweets", or "followers"')
        extraction_funcs = (self._extract_ids,)
        paginated_token_name = 'pagination_token'
        return self._get_paginated_replies(
            kwargs, scrape_func, extraction_funcs, paginated_token_name
        )[0]

    def _get_list_from_quote_tweets(
        self,
        tweet_id: Union[str, int],
    ) -> list[int]:
        """Executes a tweet search getting user IDs who have "quote tweeted" a
        specific Tweet.

        Args:
            tweet_id (int): (Union[str, int]): The Tweet id to get matches for.

        Returns:
            list[int]: A list of user IDs.
        """
        kwargs = {
            'id': tweet_id,
            'tweet_fields': ['author_id'],
            'max_results': 100,
        }
        scrape_func = self.client.get_quote_tweets
        extraction_funcs = (self._extract_user_ids,)
        paginated_token_name = 'pagination_token'
        return self._get_paginated_replies(
            kwargs, scrape_func, extraction_funcs, paginated_token_name
        )[0]

    def _get_user_ids_from_handles(self, user_ids: list[Union[str, int]]) -> list[int]:
        """Takes a list of usernames and user IDs, converting any usernames to
        user IDs.

        Args:
            user_ids (list[Union[str, int]]): A mixed list of numerical user IDs
                and usernames indicated with an @ symbol before them.

        Raises:
            ValueError: If any strings without an @ handle cannot be converted
                to integers
            ValueError: If there are over 100 handles to convert. The search
                would never need to be that restricted.

        Returns:
            list[int]: A list of user IDs
        """
        unconverted, output = [], []
        for user_id in user_ids:
            if isinstance(user_id, str) and user_id.startswith('@'):
                unconverted.append(user_id[1:])
            else:
                try:
                    user_id = int(user_id)
                except ValueError:
                    raise ValueError(
                        'User ids must be in the form of a numerical id or a username (with @ handle included)'
                    )
                output.append(user_id)
        if len(unconverted) > 100:
            raise ValueError('Too many @handles to convert.')
        if len(unconverted) > 0:
            self._response = self.client.get_users(
                usernames=unconverted, user_fields=['id']
            )
            output.extend([user_id[0] for user_id in self._extract_ids()])
        return output

    def _get_list_from_followers(
        self, following: Union[list[Union[int, str]], int, str]
    ) -> list[list[int]]:
        """Executes a tweet search getting followers of a list of users.

        Args:
            following (Union[list[Union[int, str]], int, str]): A list of user
                IDs and/or usernames to scrape followers from.

        Returns:
            list[int]: A list of lists containing user IDs who follow the
            accounts queried.
        """
        output = []
        if isinstance(following, (int, str)):
            following = [following]
        follow_ids = self._get_user_ids_from_handles(following)
        for follow_id in follow_ids:
            output.append(
                self._get_list_from_likes_retweets_followers(
                    follow_id, kind='followers'
                )
            )
        return output

    def _restrict_to_user_approvals(
        self, df: object, user_approvals: list[list[int]], condition_names: list[str]
    ) -> object:
        """Iterates through lists of whitelisted users who fufilled a condition
        removing any names not included.

        Args:
            df (object): A Pandas DataFrame of Tweet results.
            user_approvals (list[list[int]]): A list of scraped usernames who
                pass the whitelist conditions of the desired engagement.
            condition_names (list[str]): A list of human readable names that
                to indicate the categories for verbose output.

        Returns:
            object: An updated DataFrame keeping only the users who fufilled
            the conditions.
        """
        approved_column = 'approved'
        for approval_list, condition_name in zip(user_approvals, condition_names):
            approval_list = pd.Series(
                True,
                index=[approval[0] for approval in approval_list],
                name=approved_column,
            )
            df = df.join(approval_list, on=self.user_id_column, how='left')
            missing = df[approved_column].isna()
            if missing.any() and self.verbose:
                usernames = df[missing][self.user_column]
                self._verbose_message(
                    f'Dropped {usernames.unique().tolist()} for not {condition_name}'
                )
            df = df[~missing]
            df = df.drop(columns=[approved_column])
        return df

    @extract_and_output
    def scrape_addresses(
        self,
        conversation_id: Union[str, int],
        output_path: str = None,
        trim_random: int = None,
        uniform_addresses: bool = False,
        following: Union[list[Union[int, str]], int, str] = None,
        liked_only: bool = False,
        retweeted_only: bool = False,
    ) -> object:
        """Scrapes a Twitter thread from a conversation ID using API
        credentials provided in a config file. Twitter API use for free users
        will likely restrict to showing only results one week old or less.

        Args:
            conversation_id (Union[str, int]): The conversation ID for the
                Twitter thread
            output_path (str, optional): If an output is desired, specify the
                output path. Defaults to None.
            trim_random (int, optional): If selected, this will trim the
                output to a random selection of the amount specified across
                unique (and one address per user). Defaults to None.
            uniform_addresses (bool, optional): Whether or not to replace the
                ENS addresses with the hexadecimal hashes that they point to.
                Requires an api connection to an ethereum provider. Defaults
                to False.
            following (Union[list[Union[int, str]]), int, str]: A list of
                addresses that participants must be following in order to
                avoid being excluded.
            liked_only (bool): Only include participants that have liked
                the giveaway post.
            retweeted_only (bool): Only include participants that have retweeted
                the giveaway post.

        Returns:
            object: A DataFrame of the the Tweet thread with the Ethereum
            addresses extracted in a seperate field.
        """

        user_approvals = []
        conditions = []
        if following is not None:
            results = self._get_list_from_followers(following)
            user_approvals.extend(results)
            conditions.extend(['following'] * len(results))
        if liked_only:
            results = self._get_list_from_likes_retweets_followers(
                conversation_id, kind='likes'
            )
            user_approvals.append(results)
            conditions.append('liking')
        if retweeted_only:
            results = self._get_list_from_likes_retweets_followers(
                conversation_id, kind='retweets'
            )
            results.extend(self._get_list_from_quote_tweets(conversation_id))
            user_approvals.append(results)
            conditions.append('retweeting')
        tweets, users = self._get_lists_from_tweets(conversation_id)
        df = pd.DataFrame(tweets)
        df.columns = [
            self.id_column,
            self.post_column,
            self.user_id_column,
            self.created_column,
        ]
        users = pd.DataFrame(users)
        users.columns = [self.user_id_column, self.user_column]
        users = users.drop_duplicates(subset=[self.user_id_column]).set_index(
            self.user_id_column, drop=True
        )
        df = (
            df.join(users, how='left', on=self.user_id_column)
            .set_index(self.id_column, drop=True)
            .sort_index()
        )
        df = self._restrict_to_user_approvals(df, user_approvals, conditions)
        return df


class CSVExtractor(GeneralExtractor):
    """This class will extract addresses from an already exported CSV file
    with the ability to toggle the regex precision to work situations in which
    you are stuck using someone else's platform where they completely botch
    the post data by dropping newline characters without any replacement.
    """

    def __init__(
        self,
        config_path: str = 'config.json',
        verbose: bool = False,
        post_column: str = None,
        user_column: str = None,
        low_precision: bool = True,
    ) -> None:
        """Creates a csv extractor obhect.

        Args:
            config_path (str, optional): The path to the config json. Defaults
                to 'config.json'.
            verbose (bool, optional): Verbose output. Defaults to False.
            post_column (str, optional): Use this to overwrite the default post
                column from the parent class to fit the schema of the csv you
                are using. Defaults to None.
            user_column (str, optional): Use this to overwrite the default user
                column from the parent class to fit the schema of the csv you
                are using. Defaults to None.
            low_precision (bool, optional): Use this in situations when you
                are stuck with an input where newline characters have been
                dropped without replacement. Defaults to True.
        """
        super().__init__(config_path, verbose)
        self.low_precision = low_precision
        if post_column is not None:
            self.post_column = post_column
        if user_column is not None:
            self.user_column = user_column
        self.final_columns = [
            self.user_column,
            self.hash_column,
            self.address_column,
            self.post_column,
        ]

    @extract_and_output
    def extract_from_csv(
        self,
        input_path: str,
        output_path: str = None,
        trim_random: int = None,
        uniform_addresses: bool = False,
    ) -> object:
        """Extracts Ethereum addresses from a csv file.

        Args:
            input_path (str): The path to the csv.
            output_path (str, optional): The path to export the new csv. If
                unset, it will only return a dataframe without saving to disk.
                Defaults to None.
            trim_random (int, optional): If selected, this will trim the
                output to a random selection of the amount specified across
                unique (and one address per user). Defaults to None.
            uniform_addresses (bool, optional): Whether or not to replace the
                ENS addresses with the hexadecimal hashes that they point to.
                Requires an api connection to an ethereum provider. Defaults
                to False.

        Returns:
            object: A DataFrame that contains a column for the extracted
            address.
        """
        df = pd.read_csv(input_path)[[self.user_column, self.post_column]]
        return df


class AddressConverter(GeneralExtractor):
    """This will convert addresses to hashes from a csv that already contains
    a mix of ENS addresses and hexadecimal hashes. It can also optionally drop
    duplicates after converting.
    """

    def __init__(
        self,
        config_path: str = 'config.json',
        verbose: bool = False,
        address_column: str = None,
    ) -> None:
        """Creates an address converter object.

        Args:
            config_path (str, optional): The path to the config json. Defaults
                to 'config.json'.
            verbose (bool, optional): Verbose output. Defaults to False.
            address_column (str, optional): Use this to overwrite the default
                address column from the parent class to fit the schema of the csv
                you are using. Defaults to None.
        """
        super().__init__(config_path, verbose)
        if address_column is not None:
            self.address_column = address_column
        self._trim_column = self.hash_column

    def process_addresses(
        self, input_path: str, output_path: str = None, trim_random: int = None
    ) -> object:
        """Imports a csv with already existing Ethereum addresses and creates
        a new hexadecimal hash column that converts any ENSes

        Args:
            input_path (str): The path to the csv.
            output_path (str, optional): The path to export the new csv. If
                unset, it will only return a dataframe without saving to disk.
                Defaults to None.
            trim_random (int, optional): If selected, this will trim the
                output to a random selection of the amount specified across
                unique (and one address per user). Defaults to None.
        Returns:
            object: A DataFrame that contains a new column for the extracted
            hexadecimal hash addresses.
        """
        self.df = pd.read_csv(input_path)
        self.df = self.replace_ens_addresses_with_hashes()
        if trim_random:
            self.df = self.sample_results(trim_random)
        if output_path is not None:
            self.df.to_csv(output_path, index=False)
        return self.df
