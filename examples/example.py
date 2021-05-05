import logging
import random

from absl import app
from absl import flags
from ortools.linear_solver import linear_solver_pb2
from ortools.linear_solver import pywraplp

FLAGS = flags.FLAGS

flags.DEFINE_integer('seed', 0, 'Random seed for the generator.')
flags.DEFINE_integer('num_models', 2, 'How  many models to generate.')
flags.DEFINE_integer('num_vars', 3, 'How many variables a model must have.')
flags.DEFINE_string('output',
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


def BuildRandomizedModels(output: str, num_models: int, num_vars: int):
  for i in range(num_models):
    logging.info('Building model %d', i)
    model = BuildSingleMPModelProto(num_vars)
    model.name = 'RandomizedPickMax_%d' % i
    with open((output + '_%d.mps' % i), 'w') as file:
      file.write(MPModelProtoToMPS(model))


def main(_):
  random.seed(FLAGS.seed)
  BuildRandomizedModels(FLAGS.output, FLAGS.num_models, FLAGS.num_vars)


if __name__ == '__main__':
    app.run(main)
