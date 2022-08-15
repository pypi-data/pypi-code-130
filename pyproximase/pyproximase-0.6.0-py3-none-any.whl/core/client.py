import abc

from .types import ProximaSeException
from .types import _build_get_document_request
from .types import _build_list_condition
from .types import WriteRequest
from .types import _check_version
from .types import _Timer
from .types import _TimerStage

from .handlers import HttpHandler
from .handlers import GrpcHandler
from .handlers import AsyncGrpcHandler


class BaseClient(abc.ABC):
    """
    BaseClient.
    """

    @abc.abstractmethod
    def __init__(self, handler):
        self._handler = handler
        self._check_version()

    def create_collection(self, collection_config):
        """
        Create collection.

        Args:
            collection_config (CollectionConfig): collection config.

        Returns:
            ProximaSeStatus: status
        """
        return self._handler.create_collection(collection_config.to_pb())

    def describe_collection(self, collection_name):
        """
        Describe collection.

        Args:
            collection_name (str):  collection name

        Returns:
            tuple: 2-element tuple containing
              * :class:`ProximaSeStatus`: status
              * :class:`CollectionInfo`: collection information
        """
        return self._handler.describe_collection(collection_name)

    def drop_collection(self, collection_name):
        """
        Drop collection.

        Args:
            collection_name (str): collection name

        Returns:
            ProximaSeStatus: status
        """
        return self._handler.drop_collection(collection_name)

    def stats_collection(self, collection_name):
        """
        Stats collection.

        Args:
            collection_name (str): collection name

        Returns:
            tuple: 2-element tuple containing
              * :class:`ProximaSeStatus`: status
              * :class:`CollectionStats`: collection statistics
        """
        return self._handler.stats_collection(collection_name)

    def list_collections(self, repository_name=None):
        """
        List all collections.

        Args:
            repository_name (Optional[str]): repository name

        Returns:
            tuple: 2-element tuple containing
              * :class:`ProximaSeStatus`: status
              * List[:class:`CollectionInfo`]: list of collection info
        """
        return self._handler.list_collections(
            _build_list_condition(repository_name))

    def query(self, query_request, **kwargs):
        """
        Query documents using vector search.

        Args:
            query_request (QueryRequest): query request

        Returns:
            tuple: 2-element tuple containing
              * :class:`ProximaSeStatus`: status
              * :class:`QueryResponse`: query response, with ``batch_count`` number of :class:`QueryResponse.Result` s,
                each with at most ``topk`` number of :class:`Document` s.

        Examples:
            >>> # For knn vector search
            >>> # first construct knn_param
            >>> knn_param = QueryRequest.KnnQueryParam(
            ...     column_name='index_column1',
            ...     features=[1.0, 2.0, ...],  # features can be list or bytes
            ...     data_type=Datatype.VECTOR_FP32)
            >>> # second construct query_filter
            >>> query_filter = QueryRequest.QueryFilter(
            ...     filter_node=QueryRequest.QueryFilterNode(
            ...         logic_type=QueryRequest.QueryLogicType.AND,
            ...         expressions=[QueryRequest.QueryFilterExpression(
            ...             column_name="forward_column1",
            ...             rel_type=QueryRequest.QueryRelType.GT,
            ...             value=10
            ...         )]
            ...     )
            ... )
            >>> # third construct query_request
            >>> knn_query_request = QueryRequest(
            ...     collection_name='collection_xxx',
            ...     topk=3,
            ...     knn_param=knn_param,
            ...     query_filter=query_filter)
            >>> # query
            >>> status, rsp = client.query(knn_query_request)

        """
        debug = query_request.debug_mode or kwargs.get("debug", False)
        timer = None
        if debug:
            timer = _Timer()
        req_pb = query_request.to_pb()
        _Timer.end_stage_helper(timer, _TimerStage.build_pb_obj.name)
        return self._handler.query(req_pb, timer=timer)

    def query_by_sql(self, sql_request, **kwargs):
        """
        Query documents using sql

        Args:
            sql_request (SqlQueryRequest): sql query request

        Returns:
            tuple: 2-element tuple containing
              * :class:`ProximaSeStatus`: status
              * :class:`QueryResponse`: query response, with ``batch_count`` number of :class:`QueryResponse.Result` s,
                each with at most ``topk`` number of :class:`Document` s.

        Examples:
            >>> # For knn vector search
            >>> sql_query_request = SqlQueryRequest(sql='select * from collection_xxx where forward_column1 < 10')
            >>> status, rsp = client.query(sql_query_request)

        """
        debug = sql_request.debug_mode or kwargs.get("debug", False)
        timer = None
        if debug:
            timer = _Timer()
        sql_req_pb = sql_request.to_pb()
        _Timer.end_stage_helper(timer, _TimerStage.build_pb_obj.name)
        return self._handler.query_by_sql(sql_req_pb, timer=timer)

    def get_document_by_key(self, collection_name, primary_key):
        """
        Query document by primary key.

        Args:
            collection_name (str): collection name
            primary_key (long): primary key

        Returns:
            tuple: 2-element tuple containing
              * :class:`ProximaSeStatus`: status. status.ok() if server succeeds(including key not exists).
              * :class:`Document`: document. None if key not exists.

        """
        req = _build_get_document_request(collection_name, primary_key)
        return self._handler.get_document_by_key(req)

    def write(self, write_request):
        """
        Write batch documents to proxima se.

        Args:
            write_request (WriteRequest): write request.

        Returns:
            ProximaSeStatus: status

        """
        return self._handler.write(write_request.to_pb())

    def delete_document_by_keys(self, collection_name, primary_keys):
        """
        Delete documents by key.

        Args:
            collection_name (str): collection name
            primary_keys (List[long]): primary keys

        Returns:
            ProximaSeStatus: status

        """
        if not isinstance(primary_keys, list):
            primary_keys = [primary_keys]
        rows = []
        for pk in primary_keys:
            row = WriteRequest.Row(
                primary_key=pk,
                operation_type=WriteRequest.OperationType.DELETE,
            )
            rows.append(row)
        delete_request = WriteRequest(
            collection_name=collection_name,
            rows=rows
        )
        return self.write(delete_request)

    def close(self):
        """
        Close connection.

        Returns: None
        """
        return self._handler.close()

    def _check_version(self):
        status, version = self._handler.get_version()
        _check_version(status, version)


class Client(BaseClient):
    def __init__(self, host, port=16000, handler='grpc', timeout=10):
        """
        Constructor.

        Args:
            host (str): hostname
            port (int): port
            handler (str): use grpc or http, defaults to grpc.
            timeout (Optional[float]): timeout in seconds, default to 10. Passing None means no timeout.
        """
        if handler.lower() == 'http':
            handler = HttpHandler(host, port, timeout)
        elif handler.lower() == 'grpc':
            handler = GrpcHandler(host, port, timeout)
        else:
            raise ProximaSeException(f"Invalid handler type[{handler}]")
        super().__init__(handler)


class AsyncClient(BaseClient):
    def __init__(self, host, port=16000, handler='grpc', timeout=10):
        """
        Constructor.

        Args:
            host (str): hostname
            port (int): port
            handler (str): only grpc is supported for now.
            timeout (Optional[float]): timeout in seconds, default to 10. Passing None means no timeout.
        """
        if handler.lower() != 'grpc':
            raise ProximaSeException("AsyncClient only support grpc")
        super().__init__(AsyncGrpcHandler(host, port, timeout))
