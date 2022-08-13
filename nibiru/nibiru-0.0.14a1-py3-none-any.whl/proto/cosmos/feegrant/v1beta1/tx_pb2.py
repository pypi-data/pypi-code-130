# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: cosmos/feegrant/v1beta1/tx.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from gogoproto import gogo_pb2 as gogoproto_dot_gogo__pb2
from google.protobuf import any_pb2 as google_dot_protobuf_dot_any__pb2
from cosmos_proto import cosmos_pb2 as cosmos__proto_dot_cosmos__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n cosmos/feegrant/v1beta1/tx.proto\x12\x17\x63osmos.feegrant.v1beta1\x1a\x14gogoproto/gogo.proto\x1a\x19google/protobuf/any.proto\x1a\x19\x63osmos_proto/cosmos.proto\"q\n\x11MsgGrantAllowance\x12\x0f\n\x07granter\x18\x01 \x01(\t\x12\x0f\n\x07grantee\x18\x02 \x01(\t\x12:\n\tallowance\x18\x03 \x01(\x0b\x32\x14.google.protobuf.AnyB\x11\xca\xb4-\rFeeAllowanceI\"\x1b\n\x19MsgGrantAllowanceResponse\"6\n\x12MsgRevokeAllowance\x12\x0f\n\x07granter\x18\x01 \x01(\t\x12\x0f\n\x07grantee\x18\x02 \x01(\t\"\x1c\n\x1aMsgRevokeAllowanceResponse2\xec\x01\n\x03Msg\x12p\n\x0eGrantAllowance\x12*.cosmos.feegrant.v1beta1.MsgGrantAllowance\x1a\x32.cosmos.feegrant.v1beta1.MsgGrantAllowanceResponse\x12s\n\x0fRevokeAllowance\x12+.cosmos.feegrant.v1beta1.MsgRevokeAllowance\x1a\x33.cosmos.feegrant.v1beta1.MsgRevokeAllowanceResponseB)Z\'github.com/cosmos/cosmos-sdk/x/feegrantb\x06proto3')



_MSGGRANTALLOWANCE = DESCRIPTOR.message_types_by_name['MsgGrantAllowance']
_MSGGRANTALLOWANCERESPONSE = DESCRIPTOR.message_types_by_name['MsgGrantAllowanceResponse']
_MSGREVOKEALLOWANCE = DESCRIPTOR.message_types_by_name['MsgRevokeAllowance']
_MSGREVOKEALLOWANCERESPONSE = DESCRIPTOR.message_types_by_name['MsgRevokeAllowanceResponse']
MsgGrantAllowance = _reflection.GeneratedProtocolMessageType('MsgGrantAllowance', (_message.Message,), {
  'DESCRIPTOR' : _MSGGRANTALLOWANCE,
  '__module__' : 'cosmos.feegrant.v1beta1.tx_pb2'
  # @@protoc_insertion_point(class_scope:cosmos.feegrant.v1beta1.MsgGrantAllowance)
  })
_sym_db.RegisterMessage(MsgGrantAllowance)

MsgGrantAllowanceResponse = _reflection.GeneratedProtocolMessageType('MsgGrantAllowanceResponse', (_message.Message,), {
  'DESCRIPTOR' : _MSGGRANTALLOWANCERESPONSE,
  '__module__' : 'cosmos.feegrant.v1beta1.tx_pb2'
  # @@protoc_insertion_point(class_scope:cosmos.feegrant.v1beta1.MsgGrantAllowanceResponse)
  })
_sym_db.RegisterMessage(MsgGrantAllowanceResponse)

MsgRevokeAllowance = _reflection.GeneratedProtocolMessageType('MsgRevokeAllowance', (_message.Message,), {
  'DESCRIPTOR' : _MSGREVOKEALLOWANCE,
  '__module__' : 'cosmos.feegrant.v1beta1.tx_pb2'
  # @@protoc_insertion_point(class_scope:cosmos.feegrant.v1beta1.MsgRevokeAllowance)
  })
_sym_db.RegisterMessage(MsgRevokeAllowance)

MsgRevokeAllowanceResponse = _reflection.GeneratedProtocolMessageType('MsgRevokeAllowanceResponse', (_message.Message,), {
  'DESCRIPTOR' : _MSGREVOKEALLOWANCERESPONSE,
  '__module__' : 'cosmos.feegrant.v1beta1.tx_pb2'
  # @@protoc_insertion_point(class_scope:cosmos.feegrant.v1beta1.MsgRevokeAllowanceResponse)
  })
_sym_db.RegisterMessage(MsgRevokeAllowanceResponse)

_MSG = DESCRIPTOR.services_by_name['Msg']
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'Z\'github.com/cosmos/cosmos-sdk/x/feegrant'
  _MSGGRANTALLOWANCE.fields_by_name['allowance']._options = None
  _MSGGRANTALLOWANCE.fields_by_name['allowance']._serialized_options = b'\312\264-\rFeeAllowanceI'
  _MSGGRANTALLOWANCE._serialized_start=137
  _MSGGRANTALLOWANCE._serialized_end=250
  _MSGGRANTALLOWANCERESPONSE._serialized_start=252
  _MSGGRANTALLOWANCERESPONSE._serialized_end=279
  _MSGREVOKEALLOWANCE._serialized_start=281
  _MSGREVOKEALLOWANCE._serialized_end=335
  _MSGREVOKEALLOWANCERESPONSE._serialized_start=337
  _MSGREVOKEALLOWANCERESPONSE._serialized_end=365
  _MSG._serialized_start=368
  _MSG._serialized_end=604
# @@protoc_insertion_point(module_scope)
