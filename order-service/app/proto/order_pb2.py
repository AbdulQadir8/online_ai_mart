# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: order.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0border.proto\x12\x05Order\"\x90\x01\n\x0cOrderMessage\x12\x0f\n\x07user_id\x18\x01 \x01(\x05\x12\x12\n\nuser_email\x18\x02 \x01(\t\x12\x0e\n\x06status\x18\x03 \x01(\t\x12\x14\n\x0ctotal_amount\x18\x04 \x01(\x01\x12\x12\n\ncreated_at\x18\x05 \x01(\t\x12\x12\n\nupdated_at\x18\x06 \x01(\t\x12\r\n\x05items\x18\x07 \x01(\t\"r\n\x13NotificationMessage\x12\x0f\n\x07user_id\x18\x01 \x01(\x05\x12\r\n\x05\x65mail\x18\x02 \x01(\t\x12\x0f\n\x07message\x18\x03 \x01(\t\x12\x0f\n\x07subject\x18\x04 \x01(\t\x12\x19\n\x11notification_type\x18\x05 \x01(\tb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'order_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _ORDERMESSAGE._serialized_start=23
  _ORDERMESSAGE._serialized_end=167
  _NOTIFICATIONMESSAGE._serialized_start=169
  _NOTIFICATIONMESSAGE._serialized_end=283
# @@protoc_insertion_point(module_scope)
