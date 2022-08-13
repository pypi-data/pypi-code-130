# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: cosmos/gov/v1beta1/gov.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from cosmos.base.v1beta1 import coin_pb2 as cosmos_dot_base_dot_v1beta1_dot_coin__pb2
from gogoproto import gogo_pb2 as gogoproto_dot_gogo__pb2
from cosmos_proto import cosmos_pb2 as cosmos__proto_dot_cosmos__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from google.protobuf import any_pb2 as google_dot_protobuf_dot_any__pb2
from google.protobuf import duration_pb2 as google_dot_protobuf_dot_duration__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1c\x63osmos/gov/v1beta1/gov.proto\x12\x12\x63osmos.gov.v1beta1\x1a\x1e\x63osmos/base/v1beta1/coin.proto\x1a\x14gogoproto/gogo.proto\x1a\x19\x63osmos_proto/cosmos.proto\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x19google/protobuf/any.proto\x1a\x1egoogle/protobuf/duration.proto\"\x95\x01\n\x12WeightedVoteOption\x12.\n\x06option\x18\x01 \x01(\x0e\x32\x1e.cosmos.gov.v1beta1.VoteOption\x12O\n\x06weight\x18\x02 \x01(\tB?\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Dec\xc8\xde\x1f\x00\xf2\xde\x1f\ryaml:\"weight\"\"C\n\x0cTextProposal\x12\r\n\x05title\x18\x01 \x01(\t\x12\x13\n\x0b\x64\x65scription\x18\x02 \x01(\t:\x0f\xd2\xb4-\x07\x43ontent\xe8\xa0\x1f\x01\"\xb0\x01\n\x07\x44\x65posit\x12+\n\x0bproposal_id\x18\x01 \x01(\x04\x42\x16\xf2\xde\x1f\x12yaml:\"proposal_id\"\x12\x11\n\tdepositor\x18\x02 \x01(\t\x12[\n\x06\x61mount\x18\x03 \x03(\x0b\x32\x19.cosmos.base.v1beta1.CoinB0\xc8\xde\x1f\x00\xaa\xdf\x1f(github.com/cosmos/cosmos-sdk/types.Coins:\x08\x88\xa0\x1f\x00\xe8\xa0\x1f\x00\"\xfc\x05\n\x08Proposal\x12(\n\x0bproposal_id\x18\x01 \x01(\x04\x42\x13\xea\xde\x1f\x02id\xf2\xde\x1f\tyaml:\"id\"\x12\x32\n\x07\x63ontent\x18\x02 \x01(\x0b\x32\x14.google.protobuf.AnyB\x0b\xca\xb4-\x07\x43ontent\x12N\n\x06status\x18\x03 \x01(\x0e\x32\".cosmos.gov.v1beta1.ProposalStatusB\x1a\xf2\xde\x1f\x16yaml:\"proposal_status\"\x12^\n\x12\x66inal_tally_result\x18\x04 \x01(\x0b\x32\x1f.cosmos.gov.v1beta1.TallyResultB!\xc8\xde\x1f\x00\xf2\xde\x1f\x19yaml:\"final_tally_result\"\x12O\n\x0bsubmit_time\x18\x05 \x01(\x0b\x32\x1a.google.protobuf.TimestampB\x1e\x90\xdf\x1f\x01\xc8\xde\x1f\x00\xf2\xde\x1f\x12yaml:\"submit_time\"\x12Y\n\x10\x64\x65posit_end_time\x18\x06 \x01(\x0b\x32\x1a.google.protobuf.TimestampB#\x90\xdf\x1f\x01\xc8\xde\x1f\x00\xf2\xde\x1f\x17yaml:\"deposit_end_time\"\x12z\n\rtotal_deposit\x18\x07 \x03(\x0b\x32\x19.cosmos.base.v1beta1.CoinBH\xc8\xde\x1f\x00\xaa\xdf\x1f(github.com/cosmos/cosmos-sdk/types.Coins\xf2\xde\x1f\x14yaml:\"total_deposit\"\x12[\n\x11voting_start_time\x18\x08 \x01(\x0b\x32\x1a.google.protobuf.TimestampB$\x90\xdf\x1f\x01\xc8\xde\x1f\x00\xf2\xde\x1f\x18yaml:\"voting_start_time\"\x12W\n\x0fvoting_end_time\x18\t \x01(\x0b\x32\x1a.google.protobuf.TimestampB\"\x90\xdf\x1f\x01\xc8\xde\x1f\x00\xf2\xde\x1f\x16yaml:\"voting_end_time\":\x04\xe8\xa0\x1f\x01\"\xaa\x02\n\x0bTallyResult\x12;\n\x03yes\x18\x01 \x01(\tB.\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xc8\xde\x1f\x00\x12?\n\x07\x61\x62stain\x18\x02 \x01(\tB.\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xc8\xde\x1f\x00\x12:\n\x02no\x18\x03 \x01(\tB.\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xc8\xde\x1f\x00\x12[\n\x0cno_with_veto\x18\x04 \x01(\tBE\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Int\xc8\xde\x1f\x00\xf2\xde\x1f\x13yaml:\"no_with_veto\":\x04\xe8\xa0\x1f\x01\"\xbf\x01\n\x04Vote\x12+\n\x0bproposal_id\x18\x01 \x01(\x04\x42\x16\xf2\xde\x1f\x12yaml:\"proposal_id\"\x12\r\n\x05voter\x18\x02 \x01(\t\x12\x32\n\x06option\x18\x03 \x01(\x0e\x32\x1e.cosmos.gov.v1beta1.VoteOptionB\x02\x18\x01\x12=\n\x07options\x18\x04 \x03(\x0b\x32&.cosmos.gov.v1beta1.WeightedVoteOptionB\x04\xc8\xde\x1f\x00:\x08\x98\xa0\x1f\x00\xe8\xa0\x1f\x00\"\x9f\x02\n\rDepositParams\x12\x8f\x01\n\x0bmin_deposit\x18\x01 \x03(\x0b\x32\x19.cosmos.base.v1beta1.CoinB_\xc8\xde\x1f\x00\xaa\xdf\x1f(github.com/cosmos/cosmos-sdk/types.Coins\xf2\xde\x1f\x12yaml:\"min_deposit\"\xea\xde\x1f\x15min_deposit,omitempty\x12|\n\x12max_deposit_period\x18\x02 \x01(\x0b\x32\x19.google.protobuf.DurationBE\xc8\xde\x1f\x00\x98\xdf\x1f\x01\xea\xde\x1f\x1cmax_deposit_period,omitempty\xf2\xde\x1f\x19yaml:\"max_deposit_period\"\"}\n\x0cVotingParams\x12m\n\rvoting_period\x18\x01 \x01(\x0b\x32\x19.google.protobuf.DurationB;\xc8\xde\x1f\x00\x98\xdf\x1f\x01\xea\xde\x1f\x17voting_period,omitempty\xf2\xde\x1f\x14yaml:\"voting_period\"\"\xb8\x02\n\x0bTallyParams\x12R\n\x06quorum\x18\x01 \x01(\x0c\x42\x42\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Dec\xc8\xde\x1f\x00\xea\xde\x1f\x10quorum,omitempty\x12X\n\tthreshold\x18\x02 \x01(\x0c\x42\x45\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Dec\xc8\xde\x1f\x00\xea\xde\x1f\x13threshold,omitempty\x12{\n\x0eveto_threshold\x18\x03 \x01(\x0c\x42\x63\xda\xde\x1f&github.com/cosmos/cosmos-sdk/types.Dec\xc8\xde\x1f\x00\xea\xde\x1f\x18veto_threshold,omitempty\xf2\xde\x1f\x15yaml:\"veto_threshold\"*\xe6\x01\n\nVoteOption\x12,\n\x17VOTE_OPTION_UNSPECIFIED\x10\x00\x1a\x0f\x8a\x9d \x0bOptionEmpty\x12\"\n\x0fVOTE_OPTION_YES\x10\x01\x1a\r\x8a\x9d \tOptionYes\x12*\n\x13VOTE_OPTION_ABSTAIN\x10\x02\x1a\x11\x8a\x9d \rOptionAbstain\x12 \n\x0eVOTE_OPTION_NO\x10\x03\x1a\x0c\x8a\x9d \x08OptionNo\x12\x32\n\x18VOTE_OPTION_NO_WITH_VETO\x10\x04\x1a\x14\x8a\x9d \x10OptionNoWithVeto\x1a\x04\x88\xa3\x1e\x00*\xcc\x02\n\x0eProposalStatus\x12.\n\x1bPROPOSAL_STATUS_UNSPECIFIED\x10\x00\x1a\r\x8a\x9d \tStatusNil\x12;\n\x1ePROPOSAL_STATUS_DEPOSIT_PERIOD\x10\x01\x1a\x17\x8a\x9d \x13StatusDepositPeriod\x12\x39\n\x1dPROPOSAL_STATUS_VOTING_PERIOD\x10\x02\x1a\x16\x8a\x9d \x12StatusVotingPeriod\x12,\n\x16PROPOSAL_STATUS_PASSED\x10\x03\x1a\x10\x8a\x9d \x0cStatusPassed\x12\x30\n\x18PROPOSAL_STATUS_REJECTED\x10\x04\x1a\x12\x8a\x9d \x0eStatusRejected\x12,\n\x16PROPOSAL_STATUS_FAILED\x10\x05\x1a\x10\x8a\x9d \x0cStatusFailed\x1a\x04\x88\xa3\x1e\x00\x42\x36Z(github.com/cosmos/cosmos-sdk/x/gov/types\xd8\xe1\x1e\x00\x80\xe2\x1e\x00\xc8\xe1\x1e\x00\x62\x06proto3')

_VOTEOPTION = DESCRIPTOR.enum_types_by_name['VoteOption']
VoteOption = enum_type_wrapper.EnumTypeWrapper(_VOTEOPTION)
_PROPOSALSTATUS = DESCRIPTOR.enum_types_by_name['ProposalStatus']
ProposalStatus = enum_type_wrapper.EnumTypeWrapper(_PROPOSALSTATUS)
VOTE_OPTION_UNSPECIFIED = 0
VOTE_OPTION_YES = 1
VOTE_OPTION_ABSTAIN = 2
VOTE_OPTION_NO = 3
VOTE_OPTION_NO_WITH_VETO = 4
PROPOSAL_STATUS_UNSPECIFIED = 0
PROPOSAL_STATUS_DEPOSIT_PERIOD = 1
PROPOSAL_STATUS_VOTING_PERIOD = 2
PROPOSAL_STATUS_PASSED = 3
PROPOSAL_STATUS_REJECTED = 4
PROPOSAL_STATUS_FAILED = 5


_WEIGHTEDVOTEOPTION = DESCRIPTOR.message_types_by_name['WeightedVoteOption']
_TEXTPROPOSAL = DESCRIPTOR.message_types_by_name['TextProposal']
_DEPOSIT = DESCRIPTOR.message_types_by_name['Deposit']
_PROPOSAL = DESCRIPTOR.message_types_by_name['Proposal']
_TALLYRESULT = DESCRIPTOR.message_types_by_name['TallyResult']
_VOTE = DESCRIPTOR.message_types_by_name['Vote']
_DEPOSITPARAMS = DESCRIPTOR.message_types_by_name['DepositParams']
_VOTINGPARAMS = DESCRIPTOR.message_types_by_name['VotingParams']
_TALLYPARAMS = DESCRIPTOR.message_types_by_name['TallyParams']
WeightedVoteOption = _reflection.GeneratedProtocolMessageType('WeightedVoteOption', (_message.Message,), {
  'DESCRIPTOR' : _WEIGHTEDVOTEOPTION,
  '__module__' : 'cosmos.gov.v1beta1.gov_pb2'
  # @@protoc_insertion_point(class_scope:cosmos.gov.v1beta1.WeightedVoteOption)
  })
_sym_db.RegisterMessage(WeightedVoteOption)

TextProposal = _reflection.GeneratedProtocolMessageType('TextProposal', (_message.Message,), {
  'DESCRIPTOR' : _TEXTPROPOSAL,
  '__module__' : 'cosmos.gov.v1beta1.gov_pb2'
  # @@protoc_insertion_point(class_scope:cosmos.gov.v1beta1.TextProposal)
  })
_sym_db.RegisterMessage(TextProposal)

Deposit = _reflection.GeneratedProtocolMessageType('Deposit', (_message.Message,), {
  'DESCRIPTOR' : _DEPOSIT,
  '__module__' : 'cosmos.gov.v1beta1.gov_pb2'
  # @@protoc_insertion_point(class_scope:cosmos.gov.v1beta1.Deposit)
  })
_sym_db.RegisterMessage(Deposit)

Proposal = _reflection.GeneratedProtocolMessageType('Proposal', (_message.Message,), {
  'DESCRIPTOR' : _PROPOSAL,
  '__module__' : 'cosmos.gov.v1beta1.gov_pb2'
  # @@protoc_insertion_point(class_scope:cosmos.gov.v1beta1.Proposal)
  })
_sym_db.RegisterMessage(Proposal)

TallyResult = _reflection.GeneratedProtocolMessageType('TallyResult', (_message.Message,), {
  'DESCRIPTOR' : _TALLYRESULT,
  '__module__' : 'cosmos.gov.v1beta1.gov_pb2'
  # @@protoc_insertion_point(class_scope:cosmos.gov.v1beta1.TallyResult)
  })
_sym_db.RegisterMessage(TallyResult)

Vote = _reflection.GeneratedProtocolMessageType('Vote', (_message.Message,), {
  'DESCRIPTOR' : _VOTE,
  '__module__' : 'cosmos.gov.v1beta1.gov_pb2'
  # @@protoc_insertion_point(class_scope:cosmos.gov.v1beta1.Vote)
  })
_sym_db.RegisterMessage(Vote)

DepositParams = _reflection.GeneratedProtocolMessageType('DepositParams', (_message.Message,), {
  'DESCRIPTOR' : _DEPOSITPARAMS,
  '__module__' : 'cosmos.gov.v1beta1.gov_pb2'
  # @@protoc_insertion_point(class_scope:cosmos.gov.v1beta1.DepositParams)
  })
_sym_db.RegisterMessage(DepositParams)

VotingParams = _reflection.GeneratedProtocolMessageType('VotingParams', (_message.Message,), {
  'DESCRIPTOR' : _VOTINGPARAMS,
  '__module__' : 'cosmos.gov.v1beta1.gov_pb2'
  # @@protoc_insertion_point(class_scope:cosmos.gov.v1beta1.VotingParams)
  })
_sym_db.RegisterMessage(VotingParams)

TallyParams = _reflection.GeneratedProtocolMessageType('TallyParams', (_message.Message,), {
  'DESCRIPTOR' : _TALLYPARAMS,
  '__module__' : 'cosmos.gov.v1beta1.gov_pb2'
  # @@protoc_insertion_point(class_scope:cosmos.gov.v1beta1.TallyParams)
  })
_sym_db.RegisterMessage(TallyParams)

if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'Z(github.com/cosmos/cosmos-sdk/x/gov/types\330\341\036\000\200\342\036\000\310\341\036\000'
  _VOTEOPTION._options = None
  _VOTEOPTION._serialized_options = b'\210\243\036\000'
  _VOTEOPTION.values_by_name["VOTE_OPTION_UNSPECIFIED"]._options = None
  _VOTEOPTION.values_by_name["VOTE_OPTION_UNSPECIFIED"]._serialized_options = b'\212\235 \013OptionEmpty'
  _VOTEOPTION.values_by_name["VOTE_OPTION_YES"]._options = None
  _VOTEOPTION.values_by_name["VOTE_OPTION_YES"]._serialized_options = b'\212\235 \tOptionYes'
  _VOTEOPTION.values_by_name["VOTE_OPTION_ABSTAIN"]._options = None
  _VOTEOPTION.values_by_name["VOTE_OPTION_ABSTAIN"]._serialized_options = b'\212\235 \rOptionAbstain'
  _VOTEOPTION.values_by_name["VOTE_OPTION_NO"]._options = None
  _VOTEOPTION.values_by_name["VOTE_OPTION_NO"]._serialized_options = b'\212\235 \010OptionNo'
  _VOTEOPTION.values_by_name["VOTE_OPTION_NO_WITH_VETO"]._options = None
  _VOTEOPTION.values_by_name["VOTE_OPTION_NO_WITH_VETO"]._serialized_options = b'\212\235 \020OptionNoWithVeto'
  _PROPOSALSTATUS._options = None
  _PROPOSALSTATUS._serialized_options = b'\210\243\036\000'
  _PROPOSALSTATUS.values_by_name["PROPOSAL_STATUS_UNSPECIFIED"]._options = None
  _PROPOSALSTATUS.values_by_name["PROPOSAL_STATUS_UNSPECIFIED"]._serialized_options = b'\212\235 \tStatusNil'
  _PROPOSALSTATUS.values_by_name["PROPOSAL_STATUS_DEPOSIT_PERIOD"]._options = None
  _PROPOSALSTATUS.values_by_name["PROPOSAL_STATUS_DEPOSIT_PERIOD"]._serialized_options = b'\212\235 \023StatusDepositPeriod'
  _PROPOSALSTATUS.values_by_name["PROPOSAL_STATUS_VOTING_PERIOD"]._options = None
  _PROPOSALSTATUS.values_by_name["PROPOSAL_STATUS_VOTING_PERIOD"]._serialized_options = b'\212\235 \022StatusVotingPeriod'
  _PROPOSALSTATUS.values_by_name["PROPOSAL_STATUS_PASSED"]._options = None
  _PROPOSALSTATUS.values_by_name["PROPOSAL_STATUS_PASSED"]._serialized_options = b'\212\235 \014StatusPassed'
  _PROPOSALSTATUS.values_by_name["PROPOSAL_STATUS_REJECTED"]._options = None
  _PROPOSALSTATUS.values_by_name["PROPOSAL_STATUS_REJECTED"]._serialized_options = b'\212\235 \016StatusRejected'
  _PROPOSALSTATUS.values_by_name["PROPOSAL_STATUS_FAILED"]._options = None
  _PROPOSALSTATUS.values_by_name["PROPOSAL_STATUS_FAILED"]._serialized_options = b'\212\235 \014StatusFailed'
  _WEIGHTEDVOTEOPTION.fields_by_name['weight']._options = None
  _WEIGHTEDVOTEOPTION.fields_by_name['weight']._serialized_options = b'\332\336\037&github.com/cosmos/cosmos-sdk/types.Dec\310\336\037\000\362\336\037\ryaml:\"weight\"'
  _TEXTPROPOSAL._options = None
  _TEXTPROPOSAL._serialized_options = b'\322\264-\007Content\350\240\037\001'
  _DEPOSIT.fields_by_name['proposal_id']._options = None
  _DEPOSIT.fields_by_name['proposal_id']._serialized_options = b'\362\336\037\022yaml:\"proposal_id\"'
  _DEPOSIT.fields_by_name['amount']._options = None
  _DEPOSIT.fields_by_name['amount']._serialized_options = b'\310\336\037\000\252\337\037(github.com/cosmos/cosmos-sdk/types.Coins'
  _DEPOSIT._options = None
  _DEPOSIT._serialized_options = b'\210\240\037\000\350\240\037\000'
  _PROPOSAL.fields_by_name['proposal_id']._options = None
  _PROPOSAL.fields_by_name['proposal_id']._serialized_options = b'\352\336\037\002id\362\336\037\tyaml:\"id\"'
  _PROPOSAL.fields_by_name['content']._options = None
  _PROPOSAL.fields_by_name['content']._serialized_options = b'\312\264-\007Content'
  _PROPOSAL.fields_by_name['status']._options = None
  _PROPOSAL.fields_by_name['status']._serialized_options = b'\362\336\037\026yaml:\"proposal_status\"'
  _PROPOSAL.fields_by_name['final_tally_result']._options = None
  _PROPOSAL.fields_by_name['final_tally_result']._serialized_options = b'\310\336\037\000\362\336\037\031yaml:\"final_tally_result\"'
  _PROPOSAL.fields_by_name['submit_time']._options = None
  _PROPOSAL.fields_by_name['submit_time']._serialized_options = b'\220\337\037\001\310\336\037\000\362\336\037\022yaml:\"submit_time\"'
  _PROPOSAL.fields_by_name['deposit_end_time']._options = None
  _PROPOSAL.fields_by_name['deposit_end_time']._serialized_options = b'\220\337\037\001\310\336\037\000\362\336\037\027yaml:\"deposit_end_time\"'
  _PROPOSAL.fields_by_name['total_deposit']._options = None
  _PROPOSAL.fields_by_name['total_deposit']._serialized_options = b'\310\336\037\000\252\337\037(github.com/cosmos/cosmos-sdk/types.Coins\362\336\037\024yaml:\"total_deposit\"'
  _PROPOSAL.fields_by_name['voting_start_time']._options = None
  _PROPOSAL.fields_by_name['voting_start_time']._serialized_options = b'\220\337\037\001\310\336\037\000\362\336\037\030yaml:\"voting_start_time\"'
  _PROPOSAL.fields_by_name['voting_end_time']._options = None
  _PROPOSAL.fields_by_name['voting_end_time']._serialized_options = b'\220\337\037\001\310\336\037\000\362\336\037\026yaml:\"voting_end_time\"'
  _PROPOSAL._options = None
  _PROPOSAL._serialized_options = b'\350\240\037\001'
  _TALLYRESULT.fields_by_name['yes']._options = None
  _TALLYRESULT.fields_by_name['yes']._serialized_options = b'\332\336\037&github.com/cosmos/cosmos-sdk/types.Int\310\336\037\000'
  _TALLYRESULT.fields_by_name['abstain']._options = None
  _TALLYRESULT.fields_by_name['abstain']._serialized_options = b'\332\336\037&github.com/cosmos/cosmos-sdk/types.Int\310\336\037\000'
  _TALLYRESULT.fields_by_name['no']._options = None
  _TALLYRESULT.fields_by_name['no']._serialized_options = b'\332\336\037&github.com/cosmos/cosmos-sdk/types.Int\310\336\037\000'
  _TALLYRESULT.fields_by_name['no_with_veto']._options = None
  _TALLYRESULT.fields_by_name['no_with_veto']._serialized_options = b'\332\336\037&github.com/cosmos/cosmos-sdk/types.Int\310\336\037\000\362\336\037\023yaml:\"no_with_veto\"'
  _TALLYRESULT._options = None
  _TALLYRESULT._serialized_options = b'\350\240\037\001'
  _VOTE.fields_by_name['proposal_id']._options = None
  _VOTE.fields_by_name['proposal_id']._serialized_options = b'\362\336\037\022yaml:\"proposal_id\"'
  _VOTE.fields_by_name['option']._options = None
  _VOTE.fields_by_name['option']._serialized_options = b'\030\001'
  _VOTE.fields_by_name['options']._options = None
  _VOTE.fields_by_name['options']._serialized_options = b'\310\336\037\000'
  _VOTE._options = None
  _VOTE._serialized_options = b'\230\240\037\000\350\240\037\000'
  _DEPOSITPARAMS.fields_by_name['min_deposit']._options = None
  _DEPOSITPARAMS.fields_by_name['min_deposit']._serialized_options = b'\310\336\037\000\252\337\037(github.com/cosmos/cosmos-sdk/types.Coins\362\336\037\022yaml:\"min_deposit\"\352\336\037\025min_deposit,omitempty'
  _DEPOSITPARAMS.fields_by_name['max_deposit_period']._options = None
  _DEPOSITPARAMS.fields_by_name['max_deposit_period']._serialized_options = b'\310\336\037\000\230\337\037\001\352\336\037\034max_deposit_period,omitempty\362\336\037\031yaml:\"max_deposit_period\"'
  _VOTINGPARAMS.fields_by_name['voting_period']._options = None
  _VOTINGPARAMS.fields_by_name['voting_period']._serialized_options = b'\310\336\037\000\230\337\037\001\352\336\037\027voting_period,omitempty\362\336\037\024yaml:\"voting_period\"'
  _TALLYPARAMS.fields_by_name['quorum']._options = None
  _TALLYPARAMS.fields_by_name['quorum']._serialized_options = b'\332\336\037&github.com/cosmos/cosmos-sdk/types.Dec\310\336\037\000\352\336\037\020quorum,omitempty'
  _TALLYPARAMS.fields_by_name['threshold']._options = None
  _TALLYPARAMS.fields_by_name['threshold']._serialized_options = b'\332\336\037&github.com/cosmos/cosmos-sdk/types.Dec\310\336\037\000\352\336\037\023threshold,omitempty'
  _TALLYPARAMS.fields_by_name['veto_threshold']._options = None
  _TALLYPARAMS.fields_by_name['veto_threshold']._serialized_options = b'\332\336\037&github.com/cosmos/cosmos-sdk/types.Dec\310\336\037\000\352\336\037\030veto_threshold,omitempty\362\336\037\025yaml:\"veto_threshold\"'
  _VOTEOPTION._serialized_start=2620
  _VOTEOPTION._serialized_end=2850
  _PROPOSALSTATUS._serialized_start=2853
  _PROPOSALSTATUS._serialized_end=3185
  _WEIGHTEDVOTEOPTION._serialized_start=226
  _WEIGHTEDVOTEOPTION._serialized_end=375
  _TEXTPROPOSAL._serialized_start=377
  _TEXTPROPOSAL._serialized_end=444
  _DEPOSIT._serialized_start=447
  _DEPOSIT._serialized_end=623
  _PROPOSAL._serialized_start=626
  _PROPOSAL._serialized_end=1390
  _TALLYRESULT._serialized_start=1393
  _TALLYRESULT._serialized_end=1691
  _VOTE._serialized_start=1694
  _VOTE._serialized_end=1885
  _DEPOSITPARAMS._serialized_start=1888
  _DEPOSITPARAMS._serialized_end=2175
  _VOTINGPARAMS._serialized_start=2177
  _VOTINGPARAMS._serialized_end=2302
  _TALLYPARAMS._serialized_start=2305
  _TALLYPARAMS._serialized_end=2617
# @@protoc_insertion_point(module_scope)
