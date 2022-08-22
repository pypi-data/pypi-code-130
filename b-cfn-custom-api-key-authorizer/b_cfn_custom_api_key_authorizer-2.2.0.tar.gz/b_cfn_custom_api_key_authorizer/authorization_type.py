from enum import Enum, auto


class AuthorizationType(Enum):
    # If this is selected, then provide "ApiKey" & "ApiSecret" in headers.
    API_KEY_AND_SECRET_HEADERS = auto()
    # If this is selected, then provide "Authorization" in headers.
    AUTHORIZATION_HEADER = auto()

    def get_authorization_config(self):
        """
        Depending on authorization type, returns identity sources for api gateway.

        Read more:
        https://docs.aws.amazon.com/apigateway/latest/developerguide/configure-api-gateway-lambda-authorization-with-console.html
        https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-lambda-authorizer.html#http-api-lambda-authorizer.identity-sources

        :return: Identity sources.
        """
        if self == AuthorizationType.API_KEY_AND_SECRET_HEADERS:
            return [
                '$request.header.ApiKey',
                '$request.header.ApiSecret'
            ]

        if self == AuthorizationType.AUTHORIZATION_HEADER:
            return [
                '$request.header.Authorization'
            ]

        raise ValueError('Unsupported configuration.')
