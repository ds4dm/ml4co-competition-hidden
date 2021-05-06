'''Exemplary binary to generate MIP models.

To generate 3 models with 10 variables each, using the default random seed use:

  > python example.py --intent="num_models: 3 num_variables: 10"

Alternatively:
  > echo "num_models: 3 num_variables: 10" > /tmp/intent.pb2
  > python example.py --intent_file="/tmp/intent.pb2"

See example.proto for definitions of all "knobs" available to control the MIPs
being generated.
'''

import logging
import random
import example_pb2

from absl import app
from absl import flags
from google.protobuf import text_format
from ortools.linear_solver import linear_solver_pb2
from ortools.linear_solver import pywraplp

FLAGS = flags.FLAGS

flags.DEFINE_string(
    'intent',
    '',
    'Content of ExampleIntentProto in text format. '
    'Takes precedence of FLAGS.intent_file.')

flags.DEFINE_string(
    'intent_file',
    '',
    'Filepath to ExapleIntentProto in text format. '
    'Takes precedence over ExampleIntentProto default values.')

flags.DEFINE_string(
    'output',
    '/tmp/mymps',
    'Pattern where to store the generated MPS files.')


def BuildSingleMPModelProto(num_vars: int) -> linear_solver_pb2.MPModelProto:
  model_proto = linear_solver_pb2.MPModelProto()
  for i in range(num_vars):
    var_proto = model_proto.variable.add()
    var_proto.name = 'pick_%d' % i
    var_proto.is_integer = True
    var_proto.lower_bound = 0.0
    var_proto.upper_bound = 1.0
    var_proto.objective_coefficient = random.uniform(0.0, 1.0)

  ct_proto = model_proto.constraint.add()
  ct_proto.name = 'PickOneConstraint'
  ct_proto.lower_bound = 1.0
  ct_proto.upper_bound = 1.0
  ct_proto.var_index.extend(range(num_vars))
  ct_proto.coefficient.extend([1.0] * num_vars)
  return model_proto


def MPModelProtoToMPS(model_proto: linear_solver_pb2.MPModelProto):
  model_mps = pywraplp.ExportModelAsMpsFormat(model_proto)
  return model_mps


def BuildRandomizedModels(output: str, intent: example_pb2.ExampleIntentProto):
  for i in range(intent.num_models):
    logging.info('Building model %d', i)
    model = BuildSingleMPModelProto(intent.num_variables)
    model.name = 'RandomizedPickMax_%d' % i
    with open((output + '_%d.mps' % i), 'w') as mps_file:
      mps_file.write(MPModelProtoToMPS(model))


def main(_):
  # Instantiate an intent proto with default values.
  intent_proto = example_pb2.ExampleIntentProto()

  # First, overwrite the intent from the intent file for all fields which are
  # set in the intent file.
  if FLAGS.intent_file:
    with open(FLAGS.intent_file, 'r') as intent_file:
      intent_str = intent_file.read()
      text_format.Merge(intent_str, intent_proto)

  # Second, overwrite the intent from intent string passed directly in the
  # command line (for all fields set in the intent string).
  text_format.Merge(FLAGS.intent, intent_proto)

  random.seed(intent_proto.random_seed)
  BuildRandomizedModels(FLAGS.output, intent_proto)


if __name__ == '__main__':
    app.run(main)
