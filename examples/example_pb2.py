# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: example.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='example.proto',
  package='',
  syntax='proto2',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\rexample.proto\"^\n\x12\x45xampleIntentProto\x12\x17\n\x0brandom_seed\x18\x01 \x01(\x05:\x02\x34\x32\x12\x15\n\nnum_models\x18\x02 \x01(\x05:\x01\x32\x12\x18\n\rnum_variables\x18\x03 \x01(\x05:\x01\x33'
)




_EXAMPLEINTENTPROTO = _descriptor.Descriptor(
  name='ExampleIntentProto',
  full_name='ExampleIntentProto',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='random_seed', full_name='ExampleIntentProto.random_seed', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=True, default_value=42,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='num_models', full_name='ExampleIntentProto.num_models', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=True, default_value=2,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='num_variables', full_name='ExampleIntentProto.num_variables', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=True, default_value=3,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=17,
  serialized_end=111,
)

DESCRIPTOR.message_types_by_name['ExampleIntentProto'] = _EXAMPLEINTENTPROTO
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

ExampleIntentProto = _reflection.GeneratedProtocolMessageType('ExampleIntentProto', (_message.Message,), {
  'DESCRIPTOR' : _EXAMPLEINTENTPROTO,
  '__module__' : 'example_pb2'
  # @@protoc_insertion_point(class_scope:ExampleIntentProto)
  })
_sym_db.RegisterMessage(ExampleIntentProto)


# @@protoc_insertion_point(module_scope)
