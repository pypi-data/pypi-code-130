import logging
import os
import re
import shlex
import signal
from subprocess import PIPE, Popen, TimeoutExpired

import pytest

log = logging.getLogger('pytest-pyppeteer')


def pytest_configure(config):
    config.addinivalue_line('markers', 'pyppeteer: This is a pyppeteer test.')


def is_pyppeteer_enabled(request):
    """Determine if the pyppeteer mark was specified when invoking pytest."""
    return 'pyppeteer' in request.config.getoption('markexpr')


def skip_if_pyppeteer_disabled(request):
    """Skip the test if the pyppeteer mark was not specified when invoking pytest."""
    if not is_pyppeteer_enabled(request):
        pytest.skip('pyppeteer mark not specified')


@pytest.fixture(scope='session')
def _pyppeteer_config(request):
    # We cannot use skip_if_pyppeteer_disabled here because this fixture is session scoped.
    # Instead, just don't return anything. Anything that would use this fixture would skip anyway.
    if is_pyppeteer_enabled(request):
        config = {
            # The default configuration
            'VUE_APP_API_ROOT': '{live_server}/api/v1',
            'VUE_APP_OAUTH_API_ROOT': '{live_server}/oauth/',
            'VUE_APP_OAUTH_CLIENT_ID': 'test-oauth-client-id',
            # Any env vars that start with "PYPPETEER_" with the prefix trimmed
            **{
                key[10:]: value
                for (key, value) in os.environ.items()
                if key.startswith('PYPPETEER_')
            },
        }
        required_settings = ['TEST_CLIENT_COMMAND', 'TEST_CLIENT_DIR']
        for required_setting in required_settings:
            if required_setting not in config:
                pytest.fail(
                    f'Required environment variable PYPPETEER_{required_setting} not defined'
                )
        return config


@pytest.fixture(scope='session')
def webpack_server(request, _pyppeteer_config, live_server):
    """
    The URL of the test frontend.

    Using this fixture has the side affect of starting a node server in a background process.

    Configuring the server is done via environment variables. Any environment variables prefixed
    with `PYPPETEER_` have that prefix stripped off, and are then passed to the environment of the
    background process. Additionally, all of those variables are formatted with the following
    values:

    Key|Value
    ---|---
    `live_server`|`live_server.url`, the URL of the
    [`live_server` fixture](https://pytest-django.readthedocs.io/en/latest/helpers.html#live-server)

    For example, if `PYPPETEER_VUE_APP_API_URL_ROOT` was set to `{live_server}/api/v3/` in your
    `tox.ini`, the environment variable `VUE_APP_API_URL_ROOT` might be set to something like
    `http://localhost:48201/api/v3/` in the webpack server context when tests are run, depending
    on which port the `live_server` is allocated.

    This fixture uses two environment variables when starting the server:

    * **`PYPPETEER_TEST_CLIENT_COMMAND`** - The command to run the server. Generally `npm run serve`
    *   or `yarn run serve`.
    * **`PYPPETEER_TEST_CLIENT_DIR`** - The directory containing the frontend project.
    *   `PYPPETEER_TEST_CLIENT_COMMAND` will be run inside this directory.
    """
    skip_if_pyppeteer_disabled(request)
    env = {
        # The path must be passed so that npm/yarn can be found
        **{'PATH': os.getenv('PATH')},
        # Pass everything from the pyppeteer config, formatted for the current environment
        **{
            key: value.format(live_server=live_server.url)
            for (key, value) in _pyppeteer_config.items()
        },
    }
    command = ['/usr/bin/env'] + shlex.split(_pyppeteer_config['TEST_CLIENT_COMMAND'])
    log.debug(f'Launching node server with {command}')
    process = Popen(
        command,
        cwd=_pyppeteer_config['TEST_CLIENT_DIR'],
        env=env,
        stdout=PIPE,
        stderr=PIPE,
        preexec_fn=os.setsid,
    )
    try:
        # Wait until the server starts by polling stdout
        max_timeout = 60
        retry_interval = 3
        err = b''
        for _ in range(0, max_timeout // retry_interval):
            try:
                _out, err = process.communicate(timeout=retry_interval)
            except TimeoutExpired as e:
                match = re.search(
                    b'App running at:\n  - Local:   (http[s]?://[a-z]+:[0-9]+/?) \n', e.stdout
                )
                if match:
                    url = match.group(1).decode('utf-8')
                    break
        else:
            raise Exception(f'webpack server failed to start: {err}')
        yield url
    finally:
        # Kill every process in the webpack server's process group
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            # TODO set up some signal handlers to ensure it always gets cleaned up
        except ProcessLookupError:
            # The process has already terminated, no need to intervene
            pass


@pytest.fixture
async def page(request, _pyppeteer_config):
    """
    A pyppeteer page in a fresh browser environment with some sane defaults set.

    Pyppeteer offers a number of arguments to configure the browser during initialization.
    Currently, a subset of these arguments are configurable using environment variables:

    Environment Variable|Pyppeteer Equivalent|Values|Default
    ---|---|---|---
    PYPPETEER_BROWSER_IGNORE_HTTPS_ERRORS|ignoreHTTPSErrors|"True"/"1" or "False"/"0"|"True"
    PYPPETEER_BROWSER_HEADLESS|headless|"True"/"1" or "False"/"0"|"True"
    PYPPETEER_BROWSER_WIDTH|defaultViewport.width|int|1024
    PYPPETEER_BROWSER_HEIGHT|defaultViewport.height|int|800
    PYPPETEER_BROWSER_DUMPIO|dumpio|"True"/"1" or "False"/"0"|"True"

    You can set these in your `tox.ini` `setenv` block, or name them in the `passenv` section and
    set them manually in the shell prior to running tox.
    """
    skip_if_pyppeteer_disabled(request)
    from pyppeteer.errors import BrowserError
    from pyppeteer.launcher import Launcher
    import pytest_asyncio  # noqa: F401

    launch_kwargs = {
        'ignoreHTTPSErrors': True,
        'headless': True,
        'defaultViewport': {'width': 1024, 'height': 800},
        'args': ['--no-sandbox'],
        'dumpio': True,
    }

    def parse_bool(value):
        if value in ('True', '1'):
            return True
        elif value in ('False', '0'):
            return False
        raise ValueError(f"invalid boolean: '{value}'")

    for key, value in _pyppeteer_config.items():
        if key == 'BROWSER_IGNORE_HTTPS_ERRORS':
            launch_kwargs['ignoreHTTPSErrors'] = parse_bool(value)
        if key == 'BROWSER_HEADLESS':
            launch_kwargs['headless'] = parse_bool(value)
        if key == 'BROWSER_WIDTH':
            launch_kwargs['defaultViewport']['width'] = int(value)
        if key == 'BROWSER_HEIGHT':
            launch_kwargs['defaultViewport']['height'] = int(value)
        if key == 'BROWSER_DUMPIO':
            launch_kwargs['dumpio'] = parse_bool(value)

    launcher = Launcher(**launch_kwargs)
    try:
        browser = await launcher.launch()
    except BrowserError as e:
        launch_command = ' '.join(launcher.cmd)
        log.error('The pyppeteer browser failed to launch.')
        log.error(
            'You may be able to get more information on the error'
            ' by starting the browser process yourself:'
        )
        log.error(launch_command)

        raise e
    page = await browser.newPage()

    @page.on('console')
    def _console_log_handler(message):
        log.debug(f'{message.type} {message.args} {message.text}')

    yield page
    await browser.close()


@pytest.fixture
def oauth_application(_pyppeteer_config, webpack_server: str):
    """
    An OAuth2 Application that can be used to log in to the `webpack_server`.

    This fixture assumes that you are using the `oauth2_provider` from
    [django-oauth-toolkit](https://github.com/jazzband/django-oauth-toolkit).
    It will generate an OAuth Application that is configured to work with the
    `webpack_server` fixture.

    The `client_id` of the application defaults to `test-oauth-client-id`, but can be overriden by
    specifying the `PYPPETEER_VUE_APP_OAUTH_CLIENT_ID` environment variable.
    """
    from oauth2_provider.models import get_application_model

    Application = get_application_model()  # noqa: N806
    application = Application(
        name='test-client-application',
        client_id=_pyppeteer_config['VUE_APP_OAUTH_CLIENT_ID'],
        client_secret='',
        client_type='public',
        redirect_uris=webpack_server if webpack_server.endswith('/') else f'{webpack_server}/',
        authorization_grant_type='authorization-code',
        skip_authorization=True,
    )
    application.save()
    return application


@pytest.fixture
def page_login(live_server, webpack_server, oauth_application, client):
    """
    A function that logs a user into the page.

    This fixture fakes a login for a given user by generating the cookie that would have been
    generated from a successful login and setting that cookie directly in the given `page`.

    Note this fixture will only authenticate the user with the API server. To authenticate with the
    web client, the full OAuth flow must be completed. This involves the web client redirecting the
    user to the API server, which sees the injected cookie, generates a session token, and
    redirects back to the web client, which keeps the session token in local storage.

    The UX of this flow is different for different apps, so it is recommended that you write your
    own fixture that performs the necessary steps in the web client to initiate/complete the login
    process.

    This fixture relies on the `oauth_application` fixture to provide the OAuth Application to log
    in to.
    """

    async def _page_login(page, user):
        client.force_login(user)
        sessionid = client.cookies['sessionid'].value
        await page.setCookie(
            {
                'name': 'sessionid',
                'value': sessionid,
                'url': live_server.url,
                'path': '/',
            }
        )
        await page.waitFor(2_000)  # TODO more reliable wait

    return _page_login
