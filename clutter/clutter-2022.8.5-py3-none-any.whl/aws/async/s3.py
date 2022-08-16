import aioboto3
import fnmatch


async def list_objects(bucket, prefix=None, session=None, session_opts=None):
    # correct
    prefix = prefix if prefix else ""
    pattern = "*" + pattern if pattern else pattern
    session_opts = session_opts if session_opts else {}

    # get list of objects
    contents = []
    session = session if session else aioboto3.Session(**session_opts)
    async with session.client("s3") as client:
        paginator = client.get_paginator("list_objects_v2")
        async for response in paginator.paginate(Bucket=bucket, Prefix=prefix):
            for content in response.get("Contents", []):
                if not pattern or fnmatch.fnmatch(content["Key"], pattern):
                    contents.append(content)

    return contents
