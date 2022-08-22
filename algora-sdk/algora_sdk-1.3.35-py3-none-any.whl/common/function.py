"""
Helper functions.
"""
import calendar
from datetime import date, time, datetime
from functools import reduce
from typing import Dict, Any, Union, List, Optional

import pandas as pd
import pytz
from aiohttp import ClientResponse
from pandas import DataFrame, to_datetime, bdate_range
from pandas_market_calendars import get_calendar
from requests import Response


def coalesce(*args):
    """
    Coalesce operator returns the first arg that isn't None.

    Args:
        *args: Tuple of args passed to the function

    Returns:
        The first non-None value in *args
    """
    return reduce(lambda x, y: x if x is not None else y, args)


def coalesce_callables(*args):
    """
    Coalesce operator returns the first arg that isn't None. If the arg is callable it will check that the value
    returned from calling the arg is not none and then return the value from calling it.

    WARNING: If an argument implements __call__ this method will evaluate the return of the __call__ method and return
    that instead of the argument itself. This is important when using python classes.

    Args:
        *args: Tuple of args passed to the function

    Returns:
        The first non-None value in *args
    """
    for arg in args:
        value = arg() if callable(arg) else arg
        if value is not None:
            return value
    return None


def transform_one_or_many(
        data: Union[List[Dict[str, Any]], Dict[str, List[Dict[str, Any]]]],
        key: Optional[str] = None
) -> Union[DataFrame, Dict[str, DataFrame]]:
    """
    Converts data to a dataframe or multiple dataframes.

    Args:
        data (Union[List[Dict[str, Any]], Dict[str, List[Dict[str, Any]]]]): Dict being transformed into Dataframes
        key (Optional[str]): Key for indexing the values of the data dict

    Returns:
        Union[DataFrame, Dict[str, DataFrame]]: A single dataframe or a map of names to dataframes
    """
    if isinstance(data, dict):
        for k in data.keys():
            data[k] = DataFrame(data[k][key])
        return data

    return DataFrame(data)


def to_pandas_with_index(data: Dict[str, Any], index: str = 'date') -> DataFrame:
    """
    Transform input data into pandas dataframe and assign index.

    Args:
        data (Dict[str, Any]): Input data as dict
        index (str): Index column name

    Returns:
        DataFrame: DataFrame
    """
    # necessary to drop column in order to avoid duplicates when converting to json
    return pd.DataFrame(data).set_index(index, drop=True)


def no_transform(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Passthrough data without any transformation.

    Args:
        data (Dict[str, Any]): Input data

    Returns:
        Dict[str, Any]: Output data
    """
    return data


def timestamp_to_datetime(timestamp: int) -> datetime:
    """
    Transform epoch timestamp in milliseconds to datetime.

    Args:
        timestamp (int): Epoch timestamp in milliseconds

    Returns:
        datetime: Python datetime
    """
    return datetime.fromtimestamp(timestamp / 1000)


def date_to_timestamp(as_of_date: date) -> int:
    """
    Convert date to epoch timestamp in milliseconds.

    Args:
        as_of_date (date): Python date

    Returns:
        int: Epoch timestamp in milliseconds
    """
    return calendar.timegm(as_of_date.timetuple()) * 1000


def datetime_to_timestamp(dt: datetime) -> int:
    """
    Convert datetime to epoch timestamp in milliseconds.

    Args:
        dt (datetime): Python datetime

    Returns:
        int: Epoch timestamp in milliseconds
    """
    return calendar.timegm(dt.utctimetuple()) * 1000


def datetime_to_utc(dt: datetime) -> datetime:
    """
    Standardize datetime to UTC. Assume that datetime where `tzinfo=None` is already in UTC.

    Args:
        dt (datetime): Python datetime

    Returns:
        datetime: Python datetime with standardized UTC timezone (`tzinfo=None`)
    """
    # assume that datetime without timezone is already in UTC
    if dt.tzinfo is None:
        return dt
    return dt.astimezone(pytz.utc).replace(tzinfo=None)


def date_to_datetime(as_of_date: date, as_of_time: time = datetime.min.time()) -> datetime:
    """
    Convert date and optional time to datetime. NOTE: time should not contain a timezone or else offset may not be
    correct.

    Args:
        as_of_date (date): Python date
        as_of_time (time): Python time

    Returns:
        datetime: Python datetime
    """
    return datetime.combine(as_of_date, as_of_time)


def create_dates_between(start: date, end: date, frequency: str = 'B') -> List[date]:
    """
    Create dates between start and end date (inclusive). Frequency used to determine which days of the week are used.

    Args:
        start (date): Python date
        end (date): Python date
        frequency (str): Frequency for date range

    Returns:
        List[date]: List of dates
    """
    return [dt.date() for dt in to_datetime(bdate_range(start=start, end=end, freq=frequency).to_list())]


def create_market_dates_between(start: date, end: date, name: str = 'NYSE') -> List[date]:
    """
    Create dates between start and end date (inclusive) given exchange calendar.

    Args:
        start (date): Python date
        end (date): Python date
        name (str): Calendar name, such as 'NYSE'

    Returns:
        List[date]: List of dates
    """
    return [dt.date() for dt in
            to_datetime(get_calendar(name).schedule(start_date=start, end_date=end).index).to_list()]


async def build_response_obj(aio_response: ClientResponse) -> Response:
    """
    Construct a requests Response object from an aiohttp Client Response object

    Args:
        aio_response (ClientResponse): Response object from aiohttp

    Returns:
        Response: A requests Response object
    """
    content = await aio_response.content.read()

    response = Response()
    response._content = content
    response.url = str(aio_response.url)
    response.status_code = aio_response.status
    headers = {row[0]: row[1] for row in aio_response.headers.items()}
    response.headers = headers
    return response
