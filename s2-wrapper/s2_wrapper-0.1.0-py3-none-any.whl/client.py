from typing import Union

from httpx import Client

from s2_wrapper.api.academic_graph.v1.endpoints import AcademicGraphEndpointsV1

BASE_URL = "https://api.semanticscholar.org"


class SemanticScholarClient:
    """A client for the Semantic Scholar API.

    Attributes:
        _api_key: Semantic Scholar API key.
        _timeout: `httpx` client timeout.
        _client: `httpx` client.
        academic_graph_v1: Semantic Scholar Academic Graph V1 endpoints.
    """

    _api_key: Union[str, None]
    _timeout: Union[float, None]
    _client: Client
    academic_graph_v1: AcademicGraphEndpointsV1

    def __init__(
        self, api_key: Union[str, None] = None, timeout: Union[float, None] = 10.0
    ) -> None:
        """Inits `SemanticScholarClient` class instance.

        Args:
            api_key: Semantic Scholar API key. To use the API is not mandatory to have an
                API key. Defaults to `None`.
            timeout: the `httpx` client timeout. If `None`, then the timeouts will be disabled.
                Defaults to `10.0`.
        """
        self._api_key = api_key
        self._timeout = timeout
        self._client = Client(
            base_url=BASE_URL,
            timeout=timeout,
            headers={"x-api-key": self._api_key} if self._api_key else None,
        )

        # Instantiate API endpoints clients
        self.academic_graph_v1 = AcademicGraphEndpointsV1(client=self._client)

    @property
    def api_key(self) -> str:
        """Returns the Semantic Scholar API key.

        Returns:
            The key or an empty string if not provided.
        """
        return self._api_key if self._api_key else ""

    @property
    def timeout(self) -> Union[float, None]:
        """Returns the `httpx` client timeout.

        Args:
            The timeout.
        """
        return self._timeout
