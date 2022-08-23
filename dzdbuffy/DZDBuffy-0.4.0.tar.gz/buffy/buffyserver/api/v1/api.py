from typing import Callable, List, Union, Dict, Type
import time
from fastapi import APIRouter, FastAPI, middleware, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import asyncio
from buffy.buffyserver.api.v1.models import (
    Response,
    Request,
    Request_in,
    Request_out,
    RequestCacheConfiguration,
)
from buffy.buffyserver.backend.storage.interface import StorageInterface
from buffy.buffyserver.backend.request_download_service.service import (
    RequestDownloaderService,
)
from fastapi.responses import StreamingResponse
import datetime
from fastapi import status, Response as FastApiResponse

tags_metadata = [
    {
        "name": "Request",
        "description": "Request a remote HTTP resource. Buffy will download this resource in the background and provide it via the `../response/` path",
    },
    {
        "name": "Response",
        "description": "The metadata of a Request outcome. The `../content` of a result can be a json document, a file, a binary file or whatever you requested :)",
        # "externalDocs": {
        #    "description": "External Docs",
        #    "url": "https://fastapi.tiangolo.com/",
        # },
    },
]


def get_v1_router(storage: StorageInterface):
    v1router = APIRouter()
    from fastapi.security import HTTPBearer, HTTPBasicCredentials
    from fastapi import Depends
    import functools

    @v1router.get(
        "/request/",
        tags=["Request"],
        response_model=List[Request_out],
        description="A List all existing requests",
        name="List all existing requests",
    )
    async def list_requests(group_name: str = None) -> List[Request_out]:
        return [
            Request_out.from_request(r)
            for r in storage.list_requests(group_name=group_name)
        ]

    @v1router.put(
        "/request/",
        tags=["Request"],
        response_model=Request_out,
        description="""If the request allready exists it will be returned otherwise a new request will be created.  
        A request is a 'ticket' for waiting and getting the outcoming responses metadata and content.  
        For existing Requests you can, if applicable, access earlier cached versions of the responses and accelerate your client code if freshness of the content is not your priority 🚀""",
        name="Find or create a request",
        status_code=status.HTTP_202_ACCEPTED,
        responses={201: {"model": Request_out}},
    )
    async def find_or_create_responses_request(
        request_in: Request_in, api_response: FastApiResponse
    ) -> Request_out:
        """
        matching_req = next(
            (
                req
                for req in storage.list_requests(group_name=request_in.group_name)
                if req.signature == request_in.signature
            ),
            None,
        )
        """
        ts = time.time()
        matching_req: Request = None
        for req in storage.list_requests(group_name=request_in.group_name):
            if req.signature == request_in.signature:
                matching_req = req
                break
        if matching_req:
            matching_req.latest_request_datetime_utc = datetime.datetime.utcnow()
            matching_req.latest_requests.append(ts)
            storage.update_request(matching_req)
            out_req = Request_out.from_request(matching_req)
            out_req.request_timestamp = ts
            return out_req
        api_response.status_code = status.HTTP_201_CREATED

        new_req = storage.create_request(request_in)
        new_req.latest_requests = [ts]
        new_req.inital_request_datetime_utc = datetime.datetime.utcnow()
        new_req = storage.update_request(new_req)
        out_req = Request_out.from_request(new_req)
        out_req.request_timestamp = ts
        return out_req

    @v1router.get(
        "/request/{request_id}",
        tags=["Request"],
        response_model=Request,
        description="""If you allready know the __id__ of your Request, you can explicitly demand a certain Request here""",
        name="Get a certain request",
    )
    async def get_request(request_id: str) -> Request_out:
        return storage.get_request(Request_out.from_request(request_id))

    @v1router.get(
        "/request/{request_id}/status/{request_timestamp}",
        tags=["Request"],
        status_code=status.HTTP_200_OK,
        responses={102: {}},
        description="Check if your request is registered by the backend. You can now try to query a Response object at the `/v1/response/*` endpoints. \
            **Hint**: This does not indicate that your response content is ready/available.",
    )
    async def get_response_by_request_timestamp(
        request_id: str, request_timestamp: float, api_response: FastApiResponse
    ):
        if not (
            request_timestamp
            in storage.get_request(request_id=request_id).latest_requests
        ):
            return {"status": "ok"}
        api_response.status_code = status.HTTP_102_PROCESSING
        return None

    @v1router.get(
        "/request/{request_id}/cache-config",
        tags=["Request"],
        response_model=RequestCacheConfiguration,
        description="""Get the (re)cache configuration of this request""",
        name="Get a certain requests (re)cache config",
    )
    async def get_request_cache_config(request_id: str) -> RequestCacheConfiguration:
        return storage.get_request(request_id).cache_configuration

    @v1router.put(
        "/request/{request_id}/cache-config",
        tags=["Request"],
        response_model=RequestCacheConfiguration,
        description="""Get the (re)cache configuration of this request""",
        name="Set or Update a certain requests (re)cache config",
    )
    async def updsert_request_cache_config(
        request_id: str,
        request_cache_config: RequestCacheConfiguration,
    ) -> Request:
        request: Request = storage.get_request(request_id)
        # update the config requets id, if the config was copied from another request
        request_cache_config.request_id = request_id
        request.cache_configuration = request_cache_config
        request = storage.update_request(request)
        return request.cache_configuration

    @v1router.get(
        "/request/{request_id}/response",
        tags=["Response"],
        response_model=List[Response],
        description="""Get a list of all cached/ongoing/failed Responses of a Request.""",
        name="List all responses of a request",
    )
    async def list_request_results(request_id: str):
        return storage.list_responses(request_id)

    @v1router.get(
        "/request/{request_id}/response/t/{tag}",
        tags=["Response"],
        response_model=List[Response],
    )
    async def list_responses_by_tag(request_id: str, tag: str):
        all_responses = storage.list_responses(request_id)
        return [res for res in all_responses if res.tags and tag in res.tags]

    @v1router.get(
        "/request/{request_id}/response/v/{version}",
        tags=["Response"],
        response_model=Response,
    )
    async def get_response(request_id: str, version: str = "latest"):
        return storage.get_response(request_id=request_id, version=version)

    @v1router.get(
        "/request/{request_id}/response/v/{version}/content",
        tags=["Response"],
        response_class=StreamingResponse,
        responses={
            200: {
                "content": {"any": {}},
                "description": "Return whatever the source response media type is.",
            }
        },
    )
    async def serve_responses_content(request_id: str, version: str):
        response = storage.get_response(request_id=request_id, version=version)
        is_text_like: bool = False
        if response.content_attributes.media_type:
            is_text_like = response.content_attributes.media_type in [
                "text",
                "json",
                "application/json",
            ] or response.content_attributes.media_type.startswith("text/")

        headers: Dict = {}
        if (
            response.content_attributes.content_size_bytes
            and response.content_attributes.content_size_bytes > 0
        ):
            headers["Content-Length"] = str(
                response.content_attributes.content_size_bytes
            )
        if response.content_attributes.content_disposition:
            headers[
                "Content-Disposition"
            ] = response.content_attributes.content_disposition
        return StreamingResponse(
            storage.read_response_content(response=response, as_text=is_text_like),
            headers=headers,
            media_type=response.content_attributes.media_type,
        )

    @v1router.put(
        "/request/{request_id}/response/v/{version}/pin",
        tags=["Response"],
        response_model=Response,
        description="""When a Response is marked as `valid`-ated an older Response version can be purged out of the cache.  
        If you pin a certain version, it will be keept no matter what.""",
        name="Pin a certain Response version in the cache",
    )
    async def update_response(request_id: str, version: str, value: bool):
        response = storage.get_response(request_id=request_id, version=version)
        if value in [True, "true", "True", 1, "1"]:
            response.pinned = True
        else:
            response.pinned = False
        return storage.update_response(response)

    @v1router.put(
        "/request/{request_id}/response/v/{version}/valid",
        tags=["Response"],
        response_model=Response,
        description="""This endpoint is intented for client side soundness validation. You can mark a file as corrupt or the opposite. it will not be offered anymore if not valid (except its explicitly requested).  
        Do not confuse "soundness","file corruption" validation with "the file is in the correct scheme for my purpose". For this case we have the `/request/{request_id}/response/v/{version}/operative/{tag}` endpoint.
    """,
        name="Mark a certain Response version in the cache as not corrupt",
    )
    async def update_response(request_id: str, version: str, value: bool):
        response = storage.get_response(request_id=request_id, version=version)
        if value in [True, "true", "True", 1, "1"]:
            response.valid = True
        else:
            response.valid = False
        return storage.update_response(response)

    @v1router.put(
        "/request/{request_id}/response/v/{version}/{tag}",
        tags=["Response"],
        response_model=Response,
        description="""Here you can tag a certain response version.  
        The `tag` could be your clients version.
        This way you can make your client, dependend on external resources, having a stable reproducibe state. as it will always get the same file served.  
        Which is the whole purpose of this venture :) 
    """,
        name="Mark a certain response version. E.g. as 'worked-for-me'",
    )
    async def update_response(request_id: str, version: str, tag: str):
        response = storage.get_response(request_id=request_id, version=version)
        if not response.tags:
            response.tags = []
        response.tags.append(tag)
        return storage.update_response(response)

    return v1router
