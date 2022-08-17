from typing import Any, Optional, Union

from aiohttp import ClientResponse, ClientResponseError, ClientSession, \
    ContentTypeError
from aiohttp.typedefs import StrOrURL

from .container import ClientResponseContextManager, HttpClientExcData
from .exc import AIOHTTP_EXCEPTION_MAP, HttpClientAuthenticationError, \
    HttpClientAuthorizationError, HttpClientRequestError, \
    HttpClientResponseContentError, HttpClientResponseError
from ..typing import JsonContentOrText

__all__ = [
    'make_request',
    'read_request',
]


def _raise_for_status(
    resp: ClientResponse,
    exc_data: Optional[HttpClientExcData] = None,
) -> None:
    """Raise for status wrapper."""
    try:
        resp.raise_for_status()

    except ClientResponseError as err:

        if resp.status == 401:
            raise HttpClientAuthenticationError(data=exc_data) from err

        if resp.status == 403:
            raise HttpClientAuthorizationError(data=exc_data) from err

        raise HttpClientResponseContentError(data=exc_data) from err


async def make_request(
    session: ClientSession,
    method: str,
    url: StrOrURL,
    raise_for_status: bool = True,
    **params: Any,
) -> ClientResponse:
    """Make request with client session."""
    try:
        resp = await session.request(
            method,
            url,
            raise_for_status=False,
            **params,
        )

    except Exception as err:
        exc_cls = AIOHTTP_EXCEPTION_MAP.get(
            type(err), HttpClientRequestError,
        )
        raise exc_cls(data=HttpClientExcData(url, method, params)) from err

    if raise_for_status:
        _raise_for_status(resp, HttpClientExcData(url, method, params))

    return resp


async def read_request(
    session: ClientSession,
    method: str,
    url: StrOrURL,
    raise_for_status: bool = True,
    **params: Any,
) -> Union[JsonContentOrText, bytes]:
    """Make request and read it`s response."""
    with ClientResponseContextManager(
        await make_request(
            session,
            method,
            url,
            raise_for_status=raise_for_status,
            **params,
        ),
    ) as resp:
        try:
            content_type = resp.headers.get('content-type')

            if content_type is None:
                return await resp.read()

            # https://www.ietf.org/rfc/rfc2045.txt
            # Content Type string can contain additional params
            # like charset.
            if content_type.startswith('application/json'):
                # Server responsed with json, let's read it.
                return await resp.json()

            if content_type.startswith('text/'):
                # Server responsed with text, let's read it.
                return await resp.text()

            return await resp.read()

        except ContentTypeError as err:
            raise HttpClientResponseError(
                data=HttpClientExcData(url, method, params)
            ) from err

        except Exception as err:
            raise HttpClientResponseContentError(
                data=HttpClientExcData(url, method, params)
            ) from err
