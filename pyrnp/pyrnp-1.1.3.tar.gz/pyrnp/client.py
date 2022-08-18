import os
from pyrnp.util import get_file_from_path, require_keys, validate
from pyrnp.exception import InvalidFileError
import requests
import json

PLATFORMS = {"eduplay_test": "https://hmg.eduplay.rnp.br/services/", "eduplay": "https://eduplay.rnp.br/services/"}

SUPPORTED_FILETYPES = [
    ".mp4",
    ".flv",
    ".ogv",
    ".wmv",
    ".avi",
    ".webm",
    ".3gp",
    ".mov",
    ".ogg",
    ".mkv",
]


class RNP:
    def __init__(
        self,
        client_key: str,
        client_id: str,
        platform: str = "eduplay",
        username: str = None,
        token: str = None,
        oauth: bool = False,
    ):
        self.client_key = client_key
        self.client_id = client_id
        self.username = username
        self.oauth = oauth
        self.token = token

        if platform not in PLATFORMS:
            raise NameError("Invalid platform selected. Available platforms: eduplay, rnp, rnp_test")
        else:
            self.url = PLATFORMS[platform]

    def get_request(self, api_url: str = None):
        return requests.get(f"{self.url}{api_url}", headers=self.get_header())

    def post_request(
        self,
        api_url: str = None,
        custom_headers: dict = None,
        files: dict = None,
    ):
        headers = self.get_header()

        if custom_headers is not None:
            for k, v in custom_headers.items():
                headers[k] = v

        return requests.post(
            api_url
            if ("apps.kloud.rnp.br/media/" in api_url or "media-prd-nh.eduplay.rnp.br/media/" in api_url)
            else f"{self.url}{api_url}",
            headers=headers,
            files=files,
        )

    def get_header(self):
        headers = {
            "Accept-Encoding": None,
            "clientkey": self.client_key,
            "User-Agent": "curl/7.68.0",  # Keep this
        }

        if self.oauth and self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        return headers

    @validate
    def upload(self, **kwargs):
        require_keys(kwargs, ["filename", "id"])

        if os.path.splitext(kwargs.get("filename"))[1] not in SUPPORTED_FILETYPES:
            raise InvalidFileError("This filetype is not supported")

        parsed_filename = get_file_from_path(kwargs.get("filename"))
        return_data = self.get_request(api_url=f"video/upload/url/{kwargs.get('id')}/{parsed_filename}").json()

        if return_data["operationCode"] != 0:
            raise ConnectionError(f"Could not fetch upload URL: {return_data}")

        with open(kwargs.get("filename"), "rb") as f:
            req = self.post_request(return_data["result"], files={parsed_filename: f})

        if "files" in req.json():
            return req
        else:
            raise ConnectionError("Upload failed: ", req.content)

    @validate
    def publish(self, **kwargs):
        require_keys(kwargs, ["title", "keywords", "filename", "id"])

        thumbnail = kwargs.get("thumbnail") or "thumb.png"
        username = kwargs.get("username") or self.username
        thumb_file = kwargs.get("thumb_file") or open(thumbnail, "rb")

        api_url = f"video/{username}/save/{kwargs.pop('id')}/{get_file_from_path(kwargs.pop('filename'))}"

        video_data = {
            "video": (None, json.dumps(kwargs), "application/json"),
            "file": (thumbnail, thumb_file, "image/png"),
        }

        return_data = self.post_request(
            api_url=api_url,
            files=video_data,
            custom_headers={"Content-Disposition": get_file_from_path(thumbnail)},
        )

        thumb_file.close()

        return return_data

    @validate
    def change_video(self, **kwargs):
        require_keys(kwargs, ["filename", "id"])
        username = kwargs.get("username") or self.username

        return_data = self.post_request(
            api_url=f"video/{username}/change/file/default/{kwargs.get('id')}/{get_file_from_path(kwargs.get('filename'))}"  # noqa: E501
        )

        return return_data

    @validate
    def change_data(self, **kwargs):
        require_keys(kwargs, ["id", "title", "keywords"])
        username = kwargs.get("username") or self.username
        change_association = kwargs.get("changeAssociation") or "false"

        api_url = f"video/{username}/update/{kwargs.pop('id')}?changeAssociation={change_association}"

        video_data = {"video": (None, json.dumps(kwargs), "application/json")}

        return self.post_request(api_url=api_url, files=video_data)

    @validate
    def delete(self, **kwargs):
        require_keys(kwargs, "id")
        username = kwargs.get("username") or self.username

        return requests.delete(f"{self.url}video/{username}/delete/{kwargs.get('id')}", headers=self.get_header())

    @validate
    def get_user_videos(self, **kwargs):
        return self.get_request(api_url=f"video/{kwargs.get('username') or self.username}/list")

    @validate
    def get_video(self, **kwargs):
        require_keys(kwargs, ["id"])
        return self.get_request(api_url=f"video/origin/versions/{kwargs.get('id')}")
