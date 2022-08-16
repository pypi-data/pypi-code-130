from pydantic import BaseSettings, Field


class SlackSettings(BaseSettings):
    api_token: str = Field(env="SLACK_BOT_TOKEN")
    default_channel: str = Field(env="SLACK_BOT_DEFAULT_CHANNEL")
