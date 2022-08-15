import struct
from enum import Enum
from enum import IntEnum
import base64
import json

import time
from ..proto import common_pb2
from ..proto import proxima_se_pb2
from ..proto import proxima_se_pb2_grpc  # NOQA

from ..version import __version__


class IndexType(IntEnum):
    UNDEFINED = 0
    PROXIMA_GRAPH_INDEX = 1
    INVERT_INDEX = 2


class DataType(IntEnum):
    UNDEFINED = 0
    BINARY = 1
    STRING = 2
    BOOL = 3
    INT32 = 4
    INT64 = 5
    UINT32 = 6
    UINT64 = 7
    FLOAT = 8
    DOUBLE = 9
    VECTOR_BINARY32 = 20
    VECTOR_BINARY64 = 21
    VECTOR_FP16 = 22
    VECTOR_FP32 = 23
    VECTOR_FP64 = 24
    VECTOR_INT4 = 25
    VECTOR_INT8 = 26
    VECTOR_INT16 = 27


class ProximaSeException(Exception):
    pass


class ProximaSeStatus:
    """
    ProximaSe Status

    Attributes:
        code (int): Status code, 0 for success, otherwise for failure.
        reason (str): Error details.
        failure_detail_status (Optional[dict]): Failure detail status.
    """

    def __init__(self, code, reason, failure_detail_status=None):
        """
        Args:
            code (int): status code
            reason (str): error details
            failure_detail_status (Optional[dict]): Failure detail status.
        """
        self.code = code
        self.reason = reason
        self.failure_detail_status = failure_detail_status
        self.timer_report = None

    def ok(self):
        """
        Returns:
            bool: if ok.
        """
        return self.code == 0

    def update_timer_report(self, timer):
        if timer is not None:
            self.timer_report = timer.timer_report

    def __str__(self):
        if self.code == 0:
            return 'success'
        if not self.failure_detail_status:
            return f'{self.reason}({self.code})'
        detail_status_str = json.dumps({k: str(v) for k, v in self.failure_detail_status.items()})
        return f'{self.reason}({self.code}) [{detail_status_str}]'

    @staticmethod
    def from_pb(pb_status):
        code = pb_status.code
        reason = pb_status.reason
        detail_status = {}
        for k, v in pb_status.failure_detail_status.items():
            detail_status[k] = ProximaSeStatus(v.code, v.reason)
        return ProximaSeStatus(code, reason, detail_status)


class _Printable:
    def __str__(self):
        return _stringify(self)

    def __repr__(self):
        return _stringify(self)


class IndexColumnParam(_Printable):
    """
    Column index params.

    Attributes:
        name (str): Column name.
        dimension (Optional[int]): Vector dimension, None for invert search
        index_type (IndexType): IndexType enum value or string, default IndexType.PROXIMA_GRAPH_INDEX for knn search
        data_type (DataType): DataType enum value or string, default DataType.VECTOR_FP32 for knn search
        extra_params (dict): Extended parameters.

    """

    # pylint: disable=too-many-arguments
    def __init__(self,
                 name,
                 dimension=None,
                 index_type=IndexType.PROXIMA_GRAPH_INDEX,
                 data_type=DataType.VECTOR_FP32,
                 extra_params=None):
        """
        Constructor

        Args:
            name (str): Column name.
            dimension (int): Vector dimension.
            index_type (int or str): IndexType enum value or string.
            data_type (int or str): DataType enum value or string.
            extra_params (Optional[dict]): Extended parameters.
        """
        # column name
        self.name = name
        # vector dimension
        self.dimension = dimension
        # IndexType enum
        self.index_type = _parse_enum_value_or_string(IndexType,
                                                      common_pb2.IndexType,
                                                      index_type, 'IT_')
        # DataType enum
        self.data_type = _parse_enum_value_or_string(DataType,
                                                     common_pb2.DataType,
                                                     data_type, 'DT_')
        # Extra parameters.
        self.extra_params = _default_if_none(extra_params, {})

    def to_pb(self):
        """Return corresponding protobuf message."""
        param = proxima_se_pb2.CollectionConfig.IndexColumnParam()
        param.column_name = self.name
        param.index_type = self.index_type.value
        param.data_type = self.data_type.value
        if self.dimension:
            param.dimension = self.dimension
        param.extra_params.extend(
            _key_value_pair(key, value)
            for key, value in self.extra_params.items())
        return param

    @staticmethod
    def from_pb(pb_column):
        """Parse from corresponding protobuf type."""
        extra_params = {}
        for extra_param in pb_column.extra_params:
            extra_params[extra_param.key] = extra_param.value
        return IndexColumnParam(pb_column.column_name, pb_column.dimension,
                                pb_column.index_type, pb_column.data_type,
                                extra_params)


class ForwardColumnParam(_Printable):
    """
    Forward column params.

    Attributes:
        column_name (str): forward column name.
        data_type (DataType): dataType enum value or string.
        extra_params (dict): extra parameters.

    """

    # pylint: disable=too-many-arguments
    def __init__(self,
                 column_name,
                 data_type=DataType.STRING,
                 extra_params=None):
        """
        Constructor

        Args:
            column_name (str): column name.
            data_type (int or str): DataType enum value or string.
            extra_params (Optional[dict]): extra parameters.
        """
        # column name
        self.column_name = column_name
        # DataType enum
        self.data_type = _parse_enum_value_or_string(DataType,
                                                     common_pb2.DataType,
                                                     data_type, 'DT_')
        # Extra parameters.
        self.extra_params = _default_if_none(extra_params, {})

    def to_pb(self):
        """Return corresponding protobuf message."""
        param = proxima_se_pb2.CollectionConfig.ForwardColumnParam()
        param.column_name = self.column_name
        param.data_type = self.data_type.value
        param.extra_params.extend(
            _key_value_pair(key, value)
            for key, value in self.extra_params.items())
        return param

    @staticmethod
    def from_pb(pb_column):
        """Parse from corresponding protobuf type."""
        extra_params = {}
        for extra_param in pb_column.extra_params:
            extra_params[extra_param.key] = extra_param.value
        return ForwardColumnParam(pb_column.column_name,
                                  pb_column.data_type,
                                  extra_params)


class DatabaseRepository(_Printable):
    """
    Database Repository.

    Attributes:
        repository_name (str): repository name
        connection_uri (str): database connection uri
        table_name (str): table name
        user (str): database user name
        password (str): database password
    """

    # pylint: disable=too-many-arguments
    def __init__(self, repository_name, connection_uri, 
                    table_name, user, password, 
                    sharding_count=1):
        """
        Constructor.

        Args:
            repository_name (str): repository name
            connection_uri (str): database connection uri, e.g. mysql://localhost/database
            table_name (str): table name
            user (str): database user name
            password (str): database password
            sharding_count(Optional[int]): database sharding_count 
        """
        self.repository_name = repository_name
        self.connection_uri = connection_uri
        self.table_name = table_name
        self.user = user
        self.password = password
        self.sharding_count = sharding_count 

    def to_pb(self):
        """Return corresponding protobuf message."""
        repo = proxima_se_pb2.CollectionConfig.RepositoryConfig()
        repo.repository_type = proxima_se_pb2.CollectionConfig.RepositoryConfig.RepositoryType.RT_DATABASE
        repo.repository_name = self.repository_name
        repo.sharding_count = self.sharding_count
        db = repo.database
        db.connection_uri = self.connection_uri
        db.table_name = self.table_name
        db.user = self.user
        db.password = self.password
        return repo

    @staticmethod
    def from_pb(pb_repo):
        """Parse from corresponding protobuf type."""
        assert pb_repo.repository_type == proxima_se_pb2.CollectionConfig.RepositoryConfig.RepositoryType.RT_DATABASE
        db = pb_repo.database
        return DatabaseRepository(pb_repo.repository_name, db.connection_uri,
                                  db.table_name, db.user, db.password, pb_repo.sharding_count)


class KafkaRepository(_Printable):
    """
    Kafka Repository.

    Attributes:
        repository_name (str): repository name
        sharding_count(int): sharding_count of kafka 
        connection_uri (str): database connection uri
        topic_name (str): topic name
        kafka_type (str): type of kafka repository
        group_id (str): group_id of kafka repository
        security_protocol (str): security_protocol of kafka 
        user (str): user of kafka 
        password(str): password of kafka 
        ssl_ca(str): ssl_ca of kafka 
    """

    # pylint: disable=too-many-arguments
    def __init__(self, repository_name, sharding_count, connection_uri,
                    topic_name, kafka_type="", group_id="", security_protocol="", 
                    user="", password="", ssl_ca=""):
        """
        Constructor.

        Args:
            repository_name (str): repository name
            connection_uri (str): database connection uri, e.g. mysql://localhost/database
            topic_name (str): topic name
        """
        self.repository_name = repository_name
        self.sharding_count = sharding_count
        self.connection_uri = connection_uri
        self.topic_name = topic_name 
        self.kafka_type = kafka_type 
        self.group_id = group_id 
        self.security_protocol = security_protocol 
        self.user = user 
        self.password = password 
        self.ssl_ca = ssl_ca 

    def to_pb(self):
        """Return corresponding protobuf message."""
        repo = proxima_se_pb2.CollectionConfig.RepositoryConfig()
        repo.repository_type = proxima_se_pb2.CollectionConfig.RepositoryConfig.RepositoryType.RT_KAFKA
        repo.repository_name = self.repository_name
        repo.sharding_count  = self.sharding_count
        kfk = repo.kafka_config
        kfk.connection_uri = self.connection_uri
        kfk.topic_name = self.topic_name
        kfk.kafka_type = self.kafka_type
        kfk.group_id = self.group_id
        kfk.security_protocol = self.security_protocol
        kfk.password = self.password
        kfk.ssl_ca = self.ssl_ca

        return repo

    @staticmethod
    def from_pb(pb_repo):
        """Parse from corresponding protobuf type."""
        assert pb_repo.repository_type == proxima_se_pb2.CollectionConfig.RepositoryConfig.RepositoryType.RT_KAFKA
        kfk = pb_repo.kafka_config
        return KafkaRepository(pb_repo.repository_name, pb_repo.sharding_count, 
                            kfk.connection_uri, kfk.topic_name, kfk.kafka_type, 
                            kfk.group_id, kfk.security_protocol, 
                            kfk.password, kfk.ssl_ca)

class FakeRepository(_Printable):
    """
    Fake Repository.

    Attributes:
        repository_name (str): repository name
        document_count(int): document count 
    """

    # pylint: disable=too-many-arguments
    def __init__(self, repository_name, document_count, sharding_count):
        """
        Constructor.

        Args:
            repository_name (str): repository name
            document_count(int): document count 
        """
        self.repository_name = repository_name
        self.document_count = document_count 
        self.sharding_count = sharding_count

    def to_pb(self):
        """Return corresponding protobuf message."""
        repo = proxima_se_pb2.CollectionConfig.RepositoryConfig()
        repo.repository_type = proxima_se_pb2.CollectionConfig.RepositoryConfig.RepositoryType.RT_FAKE
        repo.repository_name = self.repository_name
        repo.sharding_count  = self.sharding_count
        fake = repo.fake_config
        fake.document_count = self.document_count
        return repo

    @staticmethod
    def from_pb(pb_repo):
        """Parse from corresponding protobuf type."""
        assert pb_repo.repository_type == proxima_se_pb2.CollectionConfig.RepositoryConfig.RepositoryType.RT_FAKE
        fake = pb_repo.fake_config
        return FakeRepository(pb_repo.repository_name, fake.document_count, pb_repo.sharding_count)


class ConsistencyLevel(IntEnum):
    """Consistency level"""

    STRONG = 0
    """Only query the fasted replica(s) whose applied index is equal."""
    QUORUM = 1
    """Only query the replicas whose applied index is within `max_missing_index_of_quorum` steps behind the fasted replica."""
    WEAK = 2
    """Query any replica."""


class CollectionDeConfig(_Printable):
    """
    Collection De related config.

    Attributes:
        resource_group_name (str): resource group name
        consistency_level (ConsistencyLevel): ConsistencyLevel enum
        max_missing_index_of_quorum (Optional[int]): determines querying replicas' max step behind the fasted replica.
    """
    def __init__(self, resource_group_name, consistency_level=ConsistencyLevel.STRONG, max_missing_index_of_quorum=None):
        """
        Constructor

        Args:
            resource_group_name (str): resource group name
            consistency_level (int or str): ConsistencyLevel enum value or string
            max_missing_index_of_quorum (Optional[int]): Determines querying replicas' max step behind the fasted replica.
                                                         Required for ConsistencyLevel.QUORUM.
        """
        # resource group name
        self.resource_group_name = resource_group_name
        # ConsistencyLevel enum
        self.consistency_level = _parse_enum_value_or_string(ConsistencyLevel,
                                                             proxima_se_pb2.CollectionConfig.ConsistencyConfig.ConsistencyLevel,
                                                             consistency_level,
                                                             'CL_')
        # max missing index to be considered as quorum
        self.max_missing_index_of_quorum = max_missing_index_of_quorum
        self._valid_check()

    def _valid_check(self):
        if self.consistency_level == ConsistencyLevel.QUORUM:
            if not isinstance(self.max_missing_index_of_quorum, int) or self.max_missing_index_of_quorum < 0:
                raise ProximaSeException("QUORUM consistency need to config non negative max_missing_index_of_quorum")

    def to_pb(self):
        pb = proxima_se_pb2.CollectionConfig.DeConfig()
        pb.consistency_config.consistency_level = self.consistency_level.value
        if self.max_missing_index_of_quorum is not None:
            pb.consistency_config.max_missing_index_of_quorum = self.max_missing_index_of_quorum
        return pb

    @staticmethod
    def from_pb(resource_group_name, pb_de_config):
        return CollectionDeConfig(resource_group_name, pb_de_config.consistency_config.consistency_level, pb_de_config.consistency_config.max_missing_index_of_quorum)


class CollectionConfig(_Printable):
    """
    Collection configuration.

    Attributes:
        collection_name (str): collection name.
        index_column_params (List[IndexColumnParam]): index column params.
        forward_column_params (List[ForwardColumnParam]): forward column params.
        repository_config (Optional[DatabaseRepository]): repository config.
        max_docs_per_segment (long): max document number per segment.
        max_docs_wal_flush (int): max docs to flush wal file.
        num_of_persist_segments_to_compact (int): number of persist segment to trigger compaction
        disable_wal (Optional[bool]): is disable write wal file.
        de_config(Optional[CollectionDeConfig]): Collection De related config. Optional for proxima-se.
                                                 Required for proxima-de.
    """

    # pylint: disable=too-many-arguments
    def __init__(self,
                 collection_name,
                 index_column_params,
                 forward_column_params,
                 repository_config=None,
                 max_docs_per_segment=0,
                 max_docs_wal_flush=0,
                 num_of_persist_segments_to_compact=0,
                 disable_wal=False,
                 de_config=None):
        """
        Constructor.

        Args:
            collection_name (str): collection name.
            index_column_params (List[IndexColumnParam]): index column params.
            forward_column_params (List[ForwardColumnParam]): forward column params.
            repository_config (Optional[DatabaseRepository]): repository config.
            max_docs_per_segment (Optional[long]): max document number per segment. 0 means infinity.
            max_docs_wal_flush (Optional[int]): max docs to flush wal file.
            num_of_persist_segments_to_compact (Optional[int]): number of persist segment to trigger compaction
            disable_wal (Optional[bool]): is disable write wal file.
            de_config(Optional[CollectionDeConfig]): Collection De related config. Optional for proxima-se.
                                                     Required for proxima-de.
        """
        # collection name.
        self.collection_name = collection_name
        # index column list.
        self.index_column_params = index_column_params
        # forward column list
        self.forward_column_params = forward_column_params
        # repository_config
        self.repository_config = repository_config
        # max document number per segment.
        self.max_docs_per_segment = max_docs_per_segment
        # max requests to flush wal file
        self.max_docs_wal_flush = max_docs_wal_flush
        # number of persist segment to trigger compaction
        self.num_of_persist_segments_to_compact = num_of_persist_segments_to_compact
        # is disable write wal file
        self.disable_wal = disable_wal
        # collection de config
        self.de_config = de_config

    def to_pb(self):
        """Return corresponding protobuf message."""
        collection = proxima_se_pb2.CollectionConfig()
        collection.collection_name = self.collection_name
        collection.index_column_params.extend(
            column.to_pb() for column in self.index_column_params)
        collection.forward_column_params.extend(
            column.to_pb() for column in self.forward_column_params)
        collection.max_docs_per_segment = self.max_docs_per_segment
        collection.max_docs_wal_flush = self.max_docs_wal_flush
        collection.num_of_persist_segments_to_compact = self.num_of_persist_segments_to_compact
        collection.disable_wal = self.disable_wal
        if self.repository_config is not None:
            collection.repository_config.CopyFrom(self.repository_config.to_pb())
        if self.de_config is not None:
            collection.resource_group_name = self.de_config.resource_group_name
            collection.de_config.CopyFrom(self.de_config.to_pb())
        return collection

    @staticmethod
    def from_pb(pb_collection_config):
        """Parse from corresponding protobuf type."""
        repository_config = _parse_repository_from_pb(pb_collection_config)
        index_column_params = [
            IndexColumnParam.from_pb(column)
            for column in pb_collection_config.index_column_params
        ]
        # pylint: disable=unnecessary-comprehension
        forward_column_params = [
            ForwardColumnParam.from_pb(column)
            for column in pb_collection_config.forward_column_params
        ]
        de_config = None
        if pb_collection_config.resource_group_name:
            de_config = CollectionDeConfig.from_pb(pb_collection_config.resource_group_name, pb_collection_config.de_config)
        return CollectionConfig(collection_name=pb_collection_config.collection_name,
                                index_column_params=index_column_params,
                                forward_column_params=forward_column_params,
                                repository_config=repository_config,
                                max_docs_per_segment=pb_collection_config.max_docs_per_segment,
                                max_docs_wal_flush=pb_collection_config.max_docs_wal_flush,
                                num_of_persist_segments_to_compact=pb_collection_config.num_of_persist_segments_to_compact,
                                disable_wal=pb_collection_config.disable_wal,
                                de_config=de_config)


class CollectionInfo(_Printable):
    """
    Collection information.

    Attributes:
        collection_config (CollectionConfig): collection config.
        status (CollectionInfo.Status): Status enum
        uuid (Optional[str]): collection uuid
        latest_lsn_context (Optional[LsnContext]): lsn context
        magic_number (Optional[long]): magic number
    """

    class Status(IntEnum):
        """Collection Status"""
        INITIALIZED = 0
        SERVING = 1
        DROPPED = 2

    # pylint: disable=too-many-arguments
    def __init__(self,
                 collection_config,
                 status,
                 uuid=None,
                 latest_lsn_context=None,
                 magic_number=None):
        """
        Constructor.

        Args:
            collection_config (CollectionConfig): collection config.
            status (Optional[CollectionInfo.Status, int, str]): Status enum int or str
            uuid (Optional[str]): collection uuid
            latest_lsn_context (Optional[LsnContext]): lsn context
            magic_number (Optional[long]): magic number
        """
        self.collection_config = collection_config
        self.status = _parse_enum_value_or_string(
            CollectionInfo.Status,
            proxima_se_pb2.CollectionInfo.CollectionStatus, status, 'CS_')
        self.uuid = uuid
        self.latest_lsn_context = latest_lsn_context
        self.magic_number = magic_number

    @staticmethod
    def from_pb(pb_collection_info):
        """Parse from corresponding protobuf type."""
        collection_config = CollectionConfig.from_pb(pb_collection_info.config)
        latest_lsn_context = LsnContext(
            pb_collection_info.latest_lsn_context.lsn,
            pb_collection_info.latest_lsn_context.context)
        return CollectionInfo(collection_config, pb_collection_info.status,
                              pb_collection_info.uuid, latest_lsn_context,
                              pb_collection_info.magic_number)


class WriteRequest(_Printable):
    class IndexColumnMeta(_Printable):
        """
        Index column meta.

        Attributes:
            name (str): column name
            data_type (DataType): DataType enum
            dimension (Optional[int]): vector dimension, None for invert search
        """

        def __init__(self, name, data_type, dimension=None):
            """
            Constructor.

            Args:
                name (str): column name
                data_type (Union[DataType, int, str]): DataType enum, enum value or str
                dimension (int): vector dimension
            """
            self.name = name
            self.data_type = _parse_enum_value_or_string(DataType, common_pb2.DataType, data_type, 'DT_')
            self.dimension = dimension

    class ForwardColumnMeta(_Printable):
        """
        Forward column meta.

        Attributes:
            column_name (str): column name
            data_type (DataType): DataType enum
        """

        def __init__(self, name, data_type):
            """
            Constructor.

            Args:
                column_name (str): column name
                data_type (Union[DataType, int, str]): DataType enum, enum value or str
            """
            self.name = name
            self.data_type = _parse_enum_value_or_string(DataType, common_pb2.DataType, data_type, 'DT_')

    class RowMeta(_Printable):
        """
        Row meta data.

        Attributes:
            forward_column_metas (List[ForwardColumnMeta]): list of forward column meta
            index_column_metas (Optional[List[IndexColumnMeta]]): list of index column meta
        """

        def __init__(self,
                     index_column_metas,
                     forward_column_metas=None):
            """
            Constructor.

            Args:
                index_column_metas (List[IndexColumnMeta]): index column metas
                forward_column_metas (Optional[List[ForwardColumnMeta]]): forward column metas
            """
            self.index_column_metas = index_column_metas
            self.forward_column_metas = _default_if_none(forward_column_metas, [])

        def to_pb(self):
            """Return corresponding protobuf message."""
            row_meta = proxima_se_pb2.WriteRequest.RowMeta()
            for m in self.index_column_metas:
                index_column_meta = row_meta.index_column_metas.add()
                index_column_meta.data_type = m.data_type.value
                index_column_meta.column_name = m.name
                if m.dimension is not None:
                    index_column_meta.dimension = m.dimension
            if self.forward_column_metas:
                for m in self.forward_column_metas:
                    forward_column_meta = row_meta.forward_column_metas.add()
                    forward_column_meta.column_name = m.name
                    forward_column_meta.data_type = m.data_type.value
            return row_meta

    class OperationType(IntEnum):
        INSERT = 0
        UPDATE = 1
        DELETE = 2

    class Row(_Printable):
        """
        Row

        Attributes:
            primary_key (long): primary key
            operation_type (OperationType): OperationType enum
            index_column_values (Optional[List[Union[str, bytes, List[Union[float, int, ...]]]]]): index column values.
                Should contain the same number as RowMeta.
            forward_column_values (Optional[List[Any]]): forward column values. Should contain the same number and type
                as RowMeta.
            lsn_context (Optional[LsnContext]): lsn context
        """

        # pylint: disable=too-many-arguments
        def __init__(self,
                     primary_key,
                     operation_type,
                     index_column_values=None,
                     forward_column_values=None,
                     lsn_context=None):
            """
            Constructor.

            Args:
                primary_key (long): primary key
                operation_type (Union[OperationType, int, str]): OperationType enum, enum value or str
                index_column_values (Optional[List[Union[str, bytes, List[Union[float, int, ...]]]]]): index column
                    values. Should contain the same number as RowMeta. Not required if operation_type is DELETE.
                forward_column_values (Optional[List[Any]]): forward column values. Should contain the same number and
                    type as RowMeta.
                lsn_context (Optional[LsnContext]): lsn context

            Examples:
                >>> # only primary_key is required for delete request
                >>> row = WriteRequest.Row(primary_key=1, operation_type=WriteRequest.OperationType.DELETE)

                >>> # index column value can take bytes, str(in the format of json array) or vector list
                >>> # 1. vector list
                >>> row = WriteRequest.Row(primary_key=1, operation_type=WriteRequest.OperationType.INSERT,
                ...     index_column_values=[[1.0, 2.0, 3.0]])
                >>> # 2. bytes in the format of binary representation in little endian
                >>> row = WriteRequest.Row(primary_key=1, operation_type=WriteRequest.OperationType.INSERT,
                ...     index_column_values=[struct.pack('<3f', 1.0, 2.0, 3.0)])
                >>> # 3. str in the format of json array
                >>> row = WriteRequest.Row(primary_key=1, operation_type=WriteRequest.OperationType.INSERT,
                ...     index_column_values=['[1.0, 2.0, 3.0]'])
            """
            self.primary_key = primary_key
            self.operation_type = _parse_enum_value_or_string(
                WriteRequest.OperationType, common_pb2.OperationType, operation_type, 'OP_')
            self.index_column_values = _default_if_none(index_column_values, [])
            self.forward_column_values = _default_if_none(forward_column_values, [])
            self.lsn_context = lsn_context
            self._valid_check()

        def _valid_check(self):
            if self.operation_type != WriteRequest.OperationType.DELETE and not self.index_column_values:
                raise ProximaSeException("Insert/Update request require index_column_values set")

    # pylint: disable=too-many-arguments
    def __init__(self,
                 collection_name,
                 rows,
                 row_meta=None,
                 request_id=None,
                 magic_number=None,
                 sharding_id=-1):
        """
        Constructor

        Args:
            collection_name (str): collection name
            rows (List[Rows]): rows
            row_meta (Optional[RowMeta]): row meta, Not required if all operation_type of rows is DELETE
            request_id (Optional[str]): request id
            magic_number (Optional[long]): magic number
            sharding_id(int): de sharding id. -1 means auto sharding, otherwise writes to the specific sharding.
        """
        self._collection_name = collection_name
        self._request_id = request_id
        self._magic_number = magic_number
        self._row_meta = row_meta
        self._rows = rows
        self._sharding_id = sharding_id
        self._valid_check()
        self._convert_vector_feature_to_bytes()

    def _valid_check(self):
        if not self._rows:
            raise ProximaSeException("Cannot write empty rows")
        for row in self._rows:
            row._valid_check()  # NOQA
        # only allow empty row meta on delete requests
        if self._row_meta is None:
            all_delete = all(row.operation_type == WriteRequest.OperationType.DELETE for row in self._rows)
            if not all_delete:
                raise ProximaSeException("Insert/Update request require row_meta set")
        else:
            forward_metas_len = len(self._row_meta.forward_column_metas)
            forward_values_len = len(self._rows[0].forward_column_values)
            if forward_metas_len != forward_values_len:
                raise ProximaSeException(
                    f"Mismatched forward meta with value, forward_metas_len={forward_metas_len}, "
                    f"forward_values_len={forward_values_len}"
                )

            index_metas_len = len(self._row_meta.index_column_metas)
            index_values_len = len(self._rows[0].index_column_values)
            if index_metas_len != index_values_len:
                raise ProximaSeException(
                    f"Mismatched index meta with value, index_metas_len={index_metas_len}, "
                    f"index_values_len={index_values_len}")

    def _convert_vector_feature_to_bytes(self):
        for row in self._rows:
            for i, features in enumerate(row.index_column_values):
                if isinstance(features, list):
                    index_meta = self._row_meta.index_column_metas[i]
                    row.index_column_values[i] = _pack_feature(features, index_meta.data_type, index_meta.dimension)

    def to_pb(self):
        """Return corresponding protobuf message."""
        pb = proxima_se_pb2.WriteRequest()
        pb.collection_name = self._collection_name
        if self._row_meta is not None:
            pb.row_meta.CopyFrom(self._row_meta.to_pb())
        if self._request_id is not None:
            pb.request_id = self._request_id
        if self._magic_number is not None:
            pb.magic_number = self._magic_number
        pb.sharding_id = self._sharding_id
        for row in self._rows:
            pb_row = pb.rows.add()
            pb_row.primary_key = row.primary_key
            pb_row.operation_type = row.operation_type.value
            if self._row_meta is not None:
                pb_row.forward_column_values.values.extend(
                    _generic_value(value, column_meta.data_type) for value, column_meta in zip(
                        row.forward_column_values, self._row_meta.forward_column_metas))
                pb_row.index_column_values.values.extend(
                    _index_value_to_generic_value(value, column_meta)
                    for value, column_meta in zip(row.index_column_values, self._row_meta.index_column_metas))
            if row.lsn_context is not None:
                pb_row.lsn_context.lsn = row.lsn_context.lsn
                pb_row.lsn_context.context = row.lsn_context.context
        return pb


class Document(_Printable):
    """
    Document

    Attributes:
        primary_key (long): primary key
        score (float): score, i.e. distance from query vector
        forward_column_values (dict): dict of forward column name and value
    """

    def __init__(self, pb_doc=None, json_doc=None):
        """
        Constructor.

        Args:
            pb_doc (proximase_pb2.Document): protobuf message
            json_doc (json): json message
        """
        if pb_doc is not None:
            self.primary_key = pb_doc.primary_key
            self.score = pb_doc.score
            self.forward_column_values = {
                value.key: _parse_generic_value_from_pb(value.value)
                for value in pb_doc.forward_column_values
            }
            return
        self.primary_key = int(json_doc['primary_key'])
        self.score = json_doc['score']
        self.forward_column_values = {}
        for forward in json_doc['forward_column_values']:
            key = forward['key']
            pb_value = forward['value']
            value = None
            if len(pb_value) == 1:
                type_key, value = next(iter(pb_value.items()))
                if type_key in ['int64_value', 'uint64_value']:
                    value = int(value)
                elif type_key == 'bytes_value':
                    value = base64.b64decode(value)
            self.forward_column_values[key] = value

    @staticmethod
    def from_pb(pb_doc):
        """Parse from corresponding protobuf type."""
        return Document(pb_doc)

    @staticmethod
    def from_json(json_doc):
        """Parse from json."""
        return Document(json_doc=json_doc)


class QueryResponse(_Printable):
    """
    QueryResponse

    Attributes:
        results (List[List[Document]]): query results.
        debug_info (str): debug information.
        latency_us (long): query latency.
    """

    def __init__(self, pb_rsp=None, json_rsp=None):
        if pb_rsp is not None:
            self.results = [[Document(d) for d in r.documents] for r in pb_rsp.results]
            self.debug_info = pb_rsp.debug_info
            self.latency_us = pb_rsp.latency_us
            return
        self.debug_info = json_rsp['debug_info']
        self.latency_us = int(json_rsp['latency_us'])
        self.results = [[Document.from_json(d) for d in r['documents']] for r in json_rsp['results']]

    @staticmethod
    def from_pb(pb_rsp):
        """Parse from corresponding protobuf type."""
        return QueryResponse(pb_rsp)

    @staticmethod
    def from_json(json_rsp):
        """Parse from json."""
        return QueryResponse(json_rsp=json_rsp)


class CollectionStats(_Printable):
    """
    Collection statistics.

    Attributes:
        collection_name(str) : collection name
        collection_path(str) : collection path
        total_doc_count(long) : total document count
        total_segment_count(long) : total segment count
        total_index_file_count(long) : total index file count
        total_index_file_size(long) : total index file size
        segment_stats(List[SegmentStats]) : segments statistics
    """

    class SegmentState(IntEnum):
        CREATED = 0
        WRITING = 1
        DUMPING = 2
        COMPACTING = 3
        PERSIST = 4

    class SegmentStats(_Printable):
        """
        Segment statistics.

        Attributes:
            segment_id(int) : segment id
            state(SegmentState) : segment state
            doc_count(long) : document count
            index_file_count(long) : index file count
            index_file_size(long) : index file size
            min_doc_id(long) : minimum document id in current segment
            max_doc_id(long) : maximum document id in current segment
            min_primary_key(long) : minimum primary key in current segment
            max_primary_key(long) : maximum primary key in current segment
            min_timestamp(long) : minimum document timestamp in current segment
            max_timestamp(long) : maximum document timestamp in current segment
            min_lsn(long) : minimum log sequence number(lsn) in current segment
            max_lsn(long) : maximum log sequence number(lsn) in current segment
            segment_path(str) : segment path

        """

        def __init__(self, pb):
            self.segment_id = pb.segment_id
            self.state = _parse_enum_value_or_string(
                CollectionStats.SegmentState,
                proxima_se_pb2.CollectionStats.SegmentStats.SegmentState, pb.state, 'SS_')
            self.doc_count = pb.doc_count
            self.index_file_count = pb.index_file_count
            self.index_file_size = pb.index_file_size
            self.min_doc_id = pb.min_doc_id
            self.max_doc_id = pb.max_doc_id
            self.min_primary_key = pb.min_primary_key
            self.max_primary_key = pb.max_primary_key
            self.min_timestamp = pb.min_timestamp
            self.max_timestamp = pb.max_timestamp
            self.min_lsn = pb.min_lsn
            self.max_lsn = pb.max_lsn
            self.segment_path = pb.segment_path

        @staticmethod
        def from_pb(pb):
            """Parse from corresponding protobuf type."""
            return CollectionStats.SegmentStats(pb)

    def __init__(self, pb):
        self.collection_name = pb.collection_name
        self.collection_path = pb.collection_path
        self.total_doc_count = pb.total_doc_count
        self.total_segment_count = pb.total_segment_count
        self.total_index_file_count = pb.total_index_file_count
        self.total_index_file_size = pb.total_index_file_size
        self.segment_stats = [
            CollectionStats.SegmentStats.from_pb(s) for s in pb.segment_stats
        ]

    @staticmethod
    def from_pb(pb):
        """Parse from corresponding protobuf type."""
        return CollectionStats(pb)

class DeCollectionStats(_Printable):
    """
    DeCollection statistics.

    Attributes:
        sharding_stats(List[ShardingStats]) : sharding statistics
    """

    class ReplicaStats(_Printable):
        """
        replica statistics.

        Attributes:
            stats(CollectionStats) : collection stats 
            host(str) : host info of replica
        """

        def __init__(self, pb):
            self.stats = CollectionStats(pb.stats)
            self.host = pb.host

        @staticmethod
        def from_pb(pb):
            """Parse from corresponding protobuf type."""
            return DeCollectionStats.ReplicaStats(pb)

    class ShardingStats(_Printable):
        """
        sharding statistics.

        Attributes:
            sharding_id(int) : sharding id 
            replica_stats(List[ReplicaStats]) : replica list statistics
        """

        def __init__(self, sharding_id, replica_stats):
            self.sharding_id = sharding_id
            self.replica_stats = replica_stats

        @staticmethod
        def from_pb(pb):
            """Parse from corresponding protobuf type."""
            replica_stats = [
                DeCollectionStats.ReplicaStats.from_pb(replica)
                for replica in pb.replica_stats
            ]
            return DeCollectionStats.ShardingStats(pb.sharding_id, replica_stats)

    def __init__(self, sharding_stats):
        self.sharding_stats = sharding_stats

    @staticmethod
    def from_pb(pb):
        """Parse from corresponding protobuf type."""
        sharding_stats = [
            DeCollectionStats.ShardingStats.from_pb(sharding)
            for sharding in pb.sharding_stats
        ]
        return DeCollectionStats(sharding_stats)


class LsnContext(_Printable):
    """
    Log sequence number context.

    Usually optional.
    Currently used by database repository.

    Attributes:
        lsn (long): log sequence number
        context (str): context str.
    """

    def __init__(self, lsn, context):
        """
        Constructor

        Args:
            lsn (long): log sequence number
            context (str): context str.
        """
        self.lsn = lsn
        self.context = context


class QueryRequest(_Printable):

    class QueryRelType(IntEnum):
        EQ = 0
        NE = 1
        GT = 2
        LT = 3
        GE = 4
        LE = 5
        LIKE = 6

    class QueryLogicType(IntEnum):
        AND = 0
        OR = 1

    class KnnQueryParam(_Printable):
        """
        KNN query param

        Attributes:
            column_name (str): knn vector index column name
            features (Union[bytes, str, List[List[Union[float, int, ...]]]]): vector features in the following formats:
               * bytes of little endian order.
               * json string in the following format
                   * flatten json array, e.g. '[1.0,2.0,3.0,4.0]' with 2 batch of 2 dimensional vectors
                   * json array of json array, e.g. '[[1.0,2.0],[3.0,4.0]]' with above case
               * list of vectors, e.g. [[1.0,2.0,3.0], [4.0, 5.0, 6.0]]
            data_type (DataType): DataType enum
               * optional for bytes features.
               * required for list of vectors features.
            dimension (Optional[int]): vector dimension.
               * required for bytes features.
               * auto computed for list of vectors features.
            batch_count (Optional[int]): query batch.
               * required for bytes features.
               * auto computed for list of vectors features.
            is_linear (bool): whether to linear search.
            radius (Optional[float]): return only documents within `radius` distance from query.
            extra_params (Optional[dict]): extra parameters.
        """

        def __init__(self,
                     column_name,
                     features,
                     data_type,
                     dimension=None,
                     batch_count=None,
                     is_linear=False,
                     radius=None,
                     extra_params=None):
            """
            Constructor

            Attributes:
                column_name (str): knn vector index column name
                features (Union[bytes, str, List[List[Union[float, int, ...]]]]): vector features of following formats:
                   * bytes of little endian order.
                   * json string in the following format
                       * flatten json array, e.g. '[1.0,2.0,3.0,4.0]' with 2 batch of 2 dimensional vectors
                       * json array of json array, e.g. '[[1.0,2.0],[3.0,4.0]]' with above case
                   * list of vectors, e.g. [[1.0,2.0,3.0], [4.0, 5.0, 6.0]]
                data_type (int or str): DataType enum value or str
                dimension (Optional[int]): vector dimension.
                   * required for bytes features.
                   * required for json string features.
                   * optional for list of vectors features, auto computed.
                batch_count (Optional[int]): query batch.
                   * required for bytes features.
                   * required for json string features.
                   * optional for list of vectors features, auto computed.
                is_linear (bool): whether to linear search.
                radius (Optional[float]): return only documents within `radius` distance from query.
                extra_params (Optional[dict]): extra parameters.
            """
            self.column_name = column_name
            self.features = features
            self.data_type = _parse_enum_value_or_string(DataType, common_pb2.DataType, data_type, 'DT_')
            self.dimension = dimension
            self.batch_count = batch_count
            self.is_linear = is_linear
            self.radius = radius
            self.extra_params = _default_if_none(extra_params, {})
            self._valid_check()

        def _valid_check(self):
            if not self.features:
                raise ProximaSeException(f'Empty features:{self.features}')

            # check feature
            if (not (isinstance(self.features, str) or isinstance(self.features, bytes) or
                     isinstance(self.features, list))):
                raise ProximaSeException(
                    f'Unsupported feature type[{type(self.features)}], we only support bytes/str/list features')
            if isinstance(self.features, list):
                if not isinstance(self.features[0], list):
                    # make single list to list(list(...))
                    self.features = [self.features]
            else:
                if self.dimension is None or self.batch_count is None:
                    raise ProximaSeException(f'str or bytes feature has empty dimension[{self.dimension}] \
                    or batch_count[{self.batch_count}]')
                if isinstance(self.features, str):
                    self.matrix = self.features

            # check dimension and batch_count
            if not self.data_type.name.startswith('VECTOR'):
                raise ProximaSeException(
                    f'Invalid data_type[{self.data_type}], expect vector type')
            self._infer_dimension_and_batch_count()

        def _infer_dimension_and_batch_count(self):
            inferred_dim = None
            inferred_batch = None
            if self.dimension is None or self.batch_count is None:
                if isinstance(self.features, list):
                    inferred_dim = len(self.features[0]) * _data_type_to_dimension.get(self.data_type, 1)
                    inferred_batch = len(self.features)
                else:
                    raise ProximaSeException(f'str or bytes feature has empty dimension[{self.dimension}] '
                                             f'or batch_count[{self.batch_count}]')
            if self.dimension is None:
                self.dimension = inferred_dim
            if self.batch_count is None:
                self.batch_count = inferred_batch
            if not self.dimension or not self.batch_count:
                raise ProximaSeException(
                    f"Empty dimension[{self.dimension}] or batch_count[{self.batch_count}]")

        def to_pb(self):
            """Return corresponding protobuf message"""
            knn = proxima_se_pb2.QueryRequest.KnnQueryParam()
            knn.column_name = self.column_name
            knn.batch_count = self.batch_count
            knn.dimension = self.dimension
            knn.data_type = self.data_type.value
            if isinstance(self.features, str):
                knn.matrix = self.matrix
            else:
                knn.features = self._build_features()
            if self.radius is not None:
                knn.radius = self.radius
            knn.is_linear = self.is_linear
            knn.extra_params.extend(_key_value_pair(key, value) for key, value in self.extra_params.items())
            return knn

        def _build_features(self):
            if isinstance(self.features, bytes):
                return self.features
            elif isinstance(self.features, list):
                bs = []
                for feature in self.features:
                    bs.append(_pack_feature(feature, self.data_type.value, self.dimension))
                return b''.join(bs)
            else:
                raise ProximaSeException(
                    f"unsupported features type[{type(self.features)}]")

    class QueryFilterExpression(_Printable):
        """
        Query Filter Expression

        Attributes:
            column_name (str): column name to add filter
            rel_type (QueryRequest.QueryRelType): QueryRelType enum
            value (Any): column value corresponding to column name
            value_type (DataType): DataType enum
        """

        def __init__(self, column_name, rel_type, value, value_type):
            """
            Constructor

            Attributes:
                column_name (str): column name to add filter
                rel_type (int or str): QueryRelType enum value or string.
                value (Any): column value corresponding to column name
                value_type (int or str): DataType enum value or string
            """
            self.column_name = column_name
            self.rel_type = _parse_enum_value_or_string(
                QueryRequest.QueryRelType, proxima_se_pb2.QueryRequest.QueryRelType, rel_type)
            self.value = value
            self.value_type = _parse_enum_value_or_string(DataType, common_pb2.DataType, value_type, 'DT_')

        def to_pb(self):
            """Return corresponding protobuf message"""
            pb = proxima_se_pb2.QueryRequest.QueryFilterExpression()
            pb.column_name = self.column_name
            pb.rel_type = self.rel_type.value
            pb.value.CopyFrom(_generic_value(self.value, self.value_type))
            return pb

    class QueryFilterNode(_Printable):
        """
        Query Filter Node

        Attributes:
            logic_type (QueryRequest.QueryLogicType): QueryLogicType enum
            expressions (List[QueryFilterExpression]): QueryFilterExpression between logic_type
            filter_nodes (Optional[list[QueryFilterNode]]): like semantic tree, QueryFilterNode is organized as a nested
                QueryFilterNode tree
        """

        def __init__(self,
                     logic_type,
                     expressions,
                     filter_nodes=None):
            """
            Constructor

            Attributes:
                logic_type (int or str): QueryLogicType enum value or str
                expressions (List[QueryFilterExpression]): QueryFilterExpression between logic_type
                filter_nodes (Optional[list[QueryFilterNode]]): like semantic tree, QueryFilterNode is organized as a nested
                    QueryFilterNode tree
            """
            self.logic_type = _parse_enum_value_or_string(
                QueryRequest.QueryLogicType, proxima_se_pb2.QueryRequest.QueryLogicType, logic_type)
            self.expressions = expressions
            self.filter_nodes = _default_if_none(filter_nodes, [])

        def to_pb(self):
            """Return corresponding protobuf message"""
            pb = proxima_se_pb2.QueryRequest.QueryFilterNode()
            pb.logic_type = self.logic_type.value
            for expression in self.expressions:
                expr_pb = pb.expressions.add()
                expr_pb.CopyFrom(expression.to_pb())
            for node in self.filter_nodes:
                node_pb = pb.filter_nodes.add()
                node_pb.CopyFrom(node.to_pb())
            return pb

    class QueryFilter(_Printable):
        """
        Query Filter

        Attributes:
            filter_nodes (QueryFilterNode): root node of query filter node tree
        """

        def __init__(self, filter_node):
            """
            Constructor

            Attributes:
                filter_nodes (QueryFilterNode): root node of query filter node tree
            """
            self.filter_node = filter_node

        def to_pb(self):
            """Return corresponding protobuf message"""
            pb = proxima_se_pb2.QueryRequest.QueryFilter()
            pb.filter_node.CopyFrom(self.filter_node.to_pb())
            return pb

    def __init__(self,
                 collection_name,
                 topk=100,
                 debug_mode=False,
                 knn_param=None,
                 invert_param=None,
                 query_filter=None,
                 query_fields=None,
                 **kwargs):
        """
        Constructor

        Attributes:
            collection_name (str): collection name to query
            topk (int): topk, default 100
            debug_mode (boolean): whether using debug mode, default False
            knn_param (Optional[KnnQueryParam]): param for knn vector search
            query_filter (Optional[QueryFilter]): filters of forward columns
            query_fields (Optional[list[str]]): summary column names of searching, default all columns
        """
        self.collection_name = collection_name
        self.topk = topk
        self.debug_mode = debug_mode or kwargs.get("debug", False)
        self.knn_pram = knn_param
        self.query_filter = query_filter
        self.query_fields = _default_if_none(query_fields, [])
        # self._valid_check()

    def _valid_check(self):
        if self.query_filter is not None or self.query_fields:
            # when using query_filter or query_fields, knn_param only support SINGLE STR feature
            if self.knn_pram is not None and (
                    self.knn_pram.batch_count != 1 or not isinstance(self.knn_pram.features, str)):
                raise ProximaSeException(
                    f"query_request with query_filter or query_fields only support single json string knn feature, now "
                    f"got feature type[{type(self.knn_pram.features)}], batch_count[{self.knn_pram.batch_count}]")

    def to_pb(self):
        """Return corresponding protobuf message"""
        pb = proxima_se_pb2.QueryRequest()
        pb.collection_name = self.collection_name
        pb.topk = self.topk
        pb.debug_mode = self.debug_mode
        if self.knn_pram is not None:
            pb.knn_param.CopyFrom(self.knn_pram.to_pb())
        if self.query_filter is not None:
            pb.query_filter.CopyFrom(self.query_filter.to_pb())
        if self.query_fields:
            pb.query_fields.extend(self.query_fields)
        return pb


class SqlQueryRequest(_Printable):
    """
    SQL Query Request

    Attributes:
        sql (str): request sql
        debug_mode (Boolean): debug mode, default False
    """

    def __init__(self, sql, debug_mode=False, **kwargs):
        """
        Constructor

        Attributes:
            sql (str): request sql
            debug_mode (Optional[Boolean]): debug mode, default False
        """
        self.sql = sql
        self.debug_mode = debug_mode or kwargs.get("debug", False)

    def to_pb(self):
        """Return corresponding protobuf message"""
        pb = proxima_se_pb2.SqlQueryRequest()
        pb.sql = self.sql
        pb.debug_mode = self.debug_mode
        return pb


def _parse_enum_value_or_string(enum_type, pb_enum_type, value, pb_enum_prefix=''):
    """
    Convert `value` to corresponding enum value.

    Args:
        enum_type: enum type.
        pb_enum_type: Protobuf enum type.
        value (int, str or enum_type): enum value

    Returns:
        enum type instance.

    Raises:
        ProximaSeException on invalid enum.
    """
    try:
        if isinstance(value, str):
            assert pb_enum_type.Value(pb_enum_prefix + value) == enum_type[value].value
            return enum_type[value]
        if isinstance(value, enum_type):
            assert pb_enum_type.Name(value.value) == pb_enum_prefix + value.name
            return value
        assert pb_enum_type.Name(value) == pb_enum_prefix + enum_type(value).name
        return enum_type(value)
    except ValueError as e:
        raise ProximaSeException(str(e))
    except AssertionError as e:
        raise ProximaSeException(f"Enum definition mismatch:{str(e)}")


def _key_value_pair(key, value):
    """Return KeyValuePair"""
    pair = common_pb2.KeyValuePair()
    pair.key = key
    pair.value = value
    return pair


def _build_get_document_request(collection_name, primary_key):
    req = proxima_se_pb2.GetDocumentRequest()
    req.collection_name = collection_name
    req.primary_key = primary_key
    return req


_data_type_to_dimension = {
    DataType.VECTOR_BINARY32: 32,
    DataType.VECTOR_BINARY64: 64,
}

_data_type_to_format = {
    DataType.VECTOR_FP16: 'e',
    DataType.VECTOR_FP32: 'f',
    DataType.VECTOR_FP64: 'd',
    DataType.VECTOR_INT16: 'h',
    DataType.VECTOR_INT8: 'c',
    DataType.VECTOR_BINARY32: 'I',
    DataType.VECTOR_BINARY64: 'Q',
}


def _pack_feature(feature, data_type, dimension):
    format_dimension = dimension // _data_type_to_dimension.get(data_type, 1)
    if data_type not in _data_type_to_format:
        raise ProximaSeException(
            f'not support auto pack feature type[{data_type}]')
    return struct.pack(f'<{format_dimension}{_data_type_to_format[data_type]}', *feature)


def _build_collection_name(collection_name):
    pb = proxima_se_pb2.CollectionName()
    pb.collection_name = collection_name
    return pb


def _build_list_condition(repository_name):
    pb = proxima_se_pb2.ListCondition()
    if repository_name is not None:
        pb.repository_name = repository_name
    return pb


def _generic_value(value, data_type):
    generic_value = common_pb2.GenericValue()
    type_to_attr = {
        DataType.BINARY: 'bytes_value',
        DataType.BOOL: 'bool_value',
        DataType.INT32: 'int32_value',
        DataType.INT64: 'int64_value',
        DataType.UINT32: 'uint32_value',
        DataType.UINT64: 'uint64_value',
        DataType.FLOAT: 'float_value',
        DataType.DOUBLE: 'double_value',
        DataType.STRING: 'string_value',
    }
    if data_type not in type_to_attr:
        raise ProximaSeException(
            f"Unsupported type[{type}], supported={type_to_attr.keys()}")
    setattr(generic_value, type_to_attr[data_type], value)
    return generic_value

def _index_value_to_generic_value(value, column_meta):
    if isinstance(value, bytes):
        return _generic_value(value, DataType.BINARY)
    if isinstance(value, str):
        return _generic_value(value, DataType.STRING)
        
    if column_meta.data_type == DataType.INT32:
        return _generic_value(value, DataType.INT32)
    if column_meta.data_type == DataType.UINT32:
        return _generic_value(value, DataType.UINT32)
    if column_meta.data_type == DataType.INT64:
        return _generic_value(value, DataType.INT64)
    if column_meta.data_type == DataType.UINT64:
        return _generic_value(value, DataType.UINT64)
    raise ProximaSeException(
        f'Index value only support str, int or bytes, got {type(value)}')


def _parse_repository_from_pb(pb_collection):
    if not pb_collection.HasField('repository_config'):
        return None
    pb_repo = pb_collection.repository_config
    if pb_repo.repository_type == proxima_se_pb2.CollectionConfig.RepositoryConfig.RepositoryType.RT_DATABASE:
        return DatabaseRepository.from_pb(pb_repo)
    if pb_repo.repository_type == proxima_se_pb2.CollectionConfig.RepositoryConfig.RepositoryType.RT_KAFKA:
        return KafkaRepository.from_pb(pb_repo)
    if pb_repo.repository_type == proxima_se_pb2.CollectionConfig.RepositoryConfig.RepositoryType.RT_FAKE:
        return FakeRepository.from_pb(pb_repo)
    raise ProximaSeException(
        f'Unexpected repository type, repo=[{str(pb_repo)}]')


def _parse_generic_value_from_pb(pb_generic_value):
    if not pb_generic_value.HasField('value_oneof'):
        return None
    field_name = pb_generic_value.WhichOneof('value_oneof')
    return getattr(pb_generic_value, field_name)


def _default_if_none(value, default_value):
    return value if value is not None else default_value


def _stringify(self):
    return f'{type(self).__name__}{vars(self)}'


def _check_version(status, version):
    if not status.ok():
        raise ProximaSeException(f'Get server version failed, status={status}')
    client_version = __version__.split('.', maxsplit=2)[:2]
    server_version = version.split('.', maxsplit=2)[:2]
    if client_version != server_version:
        raise ProximaSeException(f'Version mismatch, client_version={__version__}, server_version={version}')


class _TimerStage(Enum):
    serialization = 1
    rpc = 2
    deserialization = 3
    build_pb_obj = 4
    build_py_obj = 5
    total = 6


class _Timer(object):
    def __init__(self):
        self._start_time = time.perf_counter()
        self._starts_map = {}
        self.timer_report = {}

    def begin_stage(self, *names):
        now = time.perf_counter()
        for n in names:
            self._starts_map[n] = now

    def end_stage(self, *names, start_stage_name=None):
        now = time.perf_counter()
        for n in names:
            self.timer_report[n] = now - self._starts_map.get(n, self._start_time)
        if start_stage_name:
            self._starts_map[start_stage_name] = now

    @staticmethod
    def begin_stage_helper(timer, *names):
        if timer is not None:
            timer.begin_stage(*names)

    @staticmethod
    def end_stage_helper(timer, *names, start_stage_name=None):
        if timer is not None:
            timer.end_stage(*names, start_stage_name=start_stage_name)
