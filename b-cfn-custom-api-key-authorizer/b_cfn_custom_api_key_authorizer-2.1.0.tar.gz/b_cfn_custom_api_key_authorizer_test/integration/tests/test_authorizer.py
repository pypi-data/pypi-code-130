import urllib3

from b_cfn_custom_api_key_authorizer_test.integration.infrastructure.main_stack import MainStack


def test_FUNCTION_authorizer_WITH_valid_credentials_EXPECT_request_allowed_to_pass(api_keys) -> None:
    """
    Tests whether the authorizer allows the request to pass through, if the
    api key and api secret are valid.

    :return: No return.
    """
    api_key, api_secret = api_keys

    response = urllib3.PoolManager().request(
        method='GET',
        url=MainStack.get_output(MainStack.API_ENDPOINT1),
        headers={
            'ApiKey': api_key,
            'ApiSecret': api_secret
        },
    )

    # Make sure response is successful.
    assert response.status == 200

    data = response.data
    data = data.decode()

    # Response from a dummy lambda function defined in the infrastructure main stack.
    assert data == 'Hello World!'


def test_FUNCTION_authorizer_WITH_valid_basic_auth_EXPECT_request_allowed_to_pass(api_keys) -> None:
    """
    Tests whether the authorizer allows the request to pass through, if the valid basic auth is given.

    :return: No return.
    """
    api_key, api_secret = api_keys

    response = urllib3.PoolManager().request(
        method='GET',
        url=MainStack.get_output(MainStack.API_ENDPOINT2),
        headers=urllib3.make_headers(basic_auth=f'{api_key}:{api_secret}')
    )

    # Make sure response is successful.
    assert response.status == 200, str(response.data)

    data = response.data
    data = data.decode()

    # Response from a dummy lambda function defined in the infrastructure main stack.
    assert data == 'Hello World!'


def test_authorizer_with_no_key_secret() -> None:
    """
    Tests whether the authorizer denies the request to pass through, if the
    api key and api secret are invalid.

    :return: No return.
    """
    response = urllib3.PoolManager().request(
        method='GET',
        url=MainStack.get_output(MainStack.API_ENDPOINT1),
        headers={},
    )

    assert response.status == 401


def test_authorizer_with_non_existent_api_key_secret() -> None:
    """
    Tests whether the authorizer denies the request to pass through, if the
    api key and api secret are invalid.

    :return: No return.
    """
    response = urllib3.PoolManager().request(
        method='GET',
        url=MainStack.get_output(MainStack.API_ENDPOINT1),
        headers={
            'ApiKey': '123',
            'ApiSecret': '123'
        },
    )

    assert response.status == 403


def test_authorizer_with_invalid_key_secret(api_keys) -> None:
    """
    Tests whether the authorizer denies the request to pass through, if the
    api key and api secret are invalid.

    :return: No return.
    """
    api_key, api_secret = api_keys

    response = urllib3.PoolManager().request(
        method='GET',
        url=MainStack.get_output(MainStack.API_ENDPOINT1),
        headers={
            'ApiKey': api_key,
            'ApiSecret': '123'
        },
    )

    assert response.status == 403

    response = urllib3.PoolManager().request(
        method='GET',
        url=MainStack.get_output(MainStack.API_ENDPOINT1),
        headers={
            'ApiKey': '123',
            'ApiSecret': api_secret
        },
    )

    assert response.status == 403
