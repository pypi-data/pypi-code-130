from pydantic import BaseSettings


class Settings(BaseSettings):
    ENVIRONMENT: str = 'dev'

    DEV_API_GATEWAY_ENDPOINT: str = 'https://rywe6a9co8.execute-api.ap-southeast-1.amazonaws.com'


settings = Settings()
