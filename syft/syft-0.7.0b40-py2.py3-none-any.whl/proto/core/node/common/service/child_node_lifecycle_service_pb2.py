# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: proto/core/node/common/service/child_node_lifecycle_service.proto
"""Generated protocol buffer code."""
# third party
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


# syft absolute
from syft.proto.core.common import (
    common_object_pb2 as proto_dot_core_dot_common_dot_common__object__pb2,
)
from syft.proto.core.io import address_pb2 as proto_dot_core_dot_io_dot_address__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\nAproto/core/node/common/service/child_node_lifecycle_service.proto\x12\x1dsyft.core.node.common.service\x1a%proto/core/common/common_object.proto\x1a\x1bproto/core/io/address.proto"\xcd\x01\n\x18RegisterChildNodeMessage\x12%\n\x06msg_id\x18\x01 \x01(\x0b\x32\x15.syft.core.common.UID\x12(\n\tlookup_id\x18\x02 \x01(\x0b\x32\x15.syft.core.common.UID\x12&\n\x07\x61\x64\x64ress\x18\x03 \x01(\x0b\x32\x15.syft.core.io.Address\x12\x38\n\x19\x63hild_node_client_address\x18\x04 \x01(\x0b\x32\x15.syft.core.io.Addressb\x06proto3'
)

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(
    DESCRIPTOR,
    "proto.core.node.common.service.child_node_lifecycle_service_pb2",
    globals(),
)
if _descriptor._USE_C_DESCRIPTORS == False:

    DESCRIPTOR._options = None
    _REGISTERCHILDNODEMESSAGE._serialized_start = 169
    _REGISTERCHILDNODEMESSAGE._serialized_end = 374
# @@protoc_insertion_point(module_scope)
