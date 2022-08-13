from typing import Type, Any

from fuo_bilibili.api.schema.requests import VideoInfoRequest, PlayUrlRequest, BaseRequest, VideoHotCommentsRequest
from fuo_bilibili.api.schema.responses import VideoInfoResponse, PlayUrlResponse, BaseResponse, VideoGetRelatedResponse, \
    VideoHotCommentsResponse


class VideoMixin:
    API_BASE = 'https://api.bilibili.com/x/web-interface'
    PLAYER_API_BASE = 'https://api.bilibili.com/x/player'
    APIX_BASE = 'https://api.bilibili.com/x'

    def get(self, url: str, param: BaseRequest, clazz: Type[BaseResponse]) -> Any:
        pass

    def video_get_info(self, request: VideoInfoRequest) -> VideoInfoResponse:
        url = f'{self.API_BASE}/view'
        return self.get(url, request, VideoInfoResponse)

    def video_get_url(self, request: PlayUrlRequest) -> PlayUrlResponse:
        url = f'{self.PLAYER_API_BASE}/playurl'
        return self.get(url, request, PlayUrlResponse)

    def video_get_related(self, request: VideoInfoRequest) -> VideoGetRelatedResponse:
        url = f'{self.API_BASE}/archive/related'
        return self.get(url, request, VideoGetRelatedResponse)

    def video_get_hot_comments(self, request: VideoHotCommentsRequest) -> VideoHotCommentsResponse:
        url = f'{self.APIX_BASE}/v2/reply'
        return self.get(url, request, VideoHotCommentsResponse)
