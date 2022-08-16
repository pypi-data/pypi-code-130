import logging
from typing import Optional

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.web.slack_response import SlackResponse

from hartware_lib.exceptions.slack import ApiError
from hartware_lib.settings.slack import SlackSettings

logger = logging.getLogger(__name__)


class SlackAdapter:
    def __init__(self, settings: SlackSettings):
        self.settings = settings
        self.client = WebClient(token=self.settings.api_token)

    def send(self, message: str, channel: Optional[str] = None) -> SlackResponse:
        try:
            return self.client.chat_postMessage(
                channel=channel or self.settings.default_channel, text=message
            )
        except SlackApiError:
            api_error = ApiError()
            logger.warning(api_error.message)

            raise api_error
