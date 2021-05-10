import logging
import random
import params_pb2

from absl import app
from absl import flags

from google.protobuf import text_format
from ortools.linear_solver import linear_solver_pb2
from ortools.linear_solver import pywraplp

FLAGS = flags.FLAGS

flags.DEFINE_string(
    'params',
    '',
    'Content of KnapsackParameters in text format. '
    'Takes precedence of FLAGS.params_file.')

flags.DEFINE_string(
    'params_file',
    '',
    'Filepath to KnapsackParameters in text format. '
    'Takes precedence over KnapsackParameters default values.')

flags.DEFINE_string(
    'out',
    '/tmp/knapsack',
    'Pattern where to store the generated MPS files.')

flags.DEFINE_integer('seed', 0, 'Random seed to use during generation.')

flags.DEFINE_integer('num', 1, 'How many models to generate.')


def BuildMipForKnapsack(
    knapsack: params_pb2.Knapsack) -> linear_solver_pb2.MPModelProto:
  model_proto = linear_solver_pb2.MPModelProto()

  num_items = len(knapsack.item)
  num_bins = len(knapsack.bin)
  num_resources = knapsack.r

  # place_vars[i][b] contains the index of a variable denoting how many copies
  # of item i to place in bin b.
  place_vars = [[None] * num_bins for _ in range(num_items)]
  for i in range(num_items):
    for b in range(num_bins):
      place_vars[i][b] = len(model_proto.variable)
      var_proto = model_proto.variable.add()
      var_proto.name = 'place_%d_%d' % (i, b)
      var_proto.is_integer = True
      var_proto.lower_bound = 0.0
      var_proto.upper_bound = knapsack.item[i].c

  # Place the appropriate number of copies for each item:
  # for i:
  #   sum_{b} place(i, b) = item(i).c
  for i in range(num_items):
    ct_proto = model_proto.constraint.add()
    ct_proto.name = 'copies_ct_%d' % i
    ct_proto.lower_bound = knapsack.item[i].c
    ct_proto.upper_bound = knapsack.item[i].c
    for b in range(num_bins):
      ct_proto.var_index.append(place_vars[i][b])
      ct_proto.coefficient.append(1.0)

  # Ensure all items fit in their bins:
  # for b, r:
  #   sum_{i} item(i).d(r) * place(i, b) <= knapsack.bin[b].s[r]
  for b in range(num_bins):
    for r in range(num_resources):
      ct_proto = model_proto.constraint.add()
      ct_proto.name = 'supply_ct_%d_%d' % (b, r)
      ct_proto.upper_bound = knapsack.bin[b].s[r]
      for i in range(num_items):
        ct_proto.var_index.append(place_vars[i][b])
        ct_proto.coefficient.append(knapsack.item[i].d[r])

  # deficit_vars[b][r] contains the index of a variable tracking the deficit
  # of the utilization of the resource r in bin b wrt the utilization expected
  # in a perfectly balanced placement.
  deficit_vars = [[None] * num_resources for _ in range(num_bins)]
  for b in range(num_bins):
    for r in range(num_resources):
      deficit_vars[b][r] = len(model_proto.variable)
      var_proto = model_proto.variable.add()
      var_proto.name = 'deficit_%d_%d' % (b, r)
      var_proto.is_integer = False
      var_proto.lower_bound = 0.0
      var_proto.upper_bound = 1.0
      var_proto.objective_coefficient = 1.0

  # for b, r:
  #   1 - num_bins / t(r) * sum_{i} item(i).d(r) * place(i, b) <= deficit(b, r)
  #
  #   where t(r) is the total demand for resource r.
  for r in range(num_resources):
    t = sum(item.d[r] for item in knapsack.item)
    for b in range(num_bins):
      ct_proto = model_proto.constraint.add()
      ct_proto.name = 'deficit_ct_%d_%d' % (b, r)
      ct_proto.lower_bound = 1.0
      ct_proto.var_index.append(deficit_vars[b][r])
      ct_proto.coefficient.append(1.0)
      for i in range(num_items):
        ct_proto.var_index.append(place_vars[i][b])
        ct_proto.coefficient.append(knapsack.item[i].d[r] * num_bins / t)

  max_deficit_vars = [None] * num_resources
  for r in range(num_resources):
    max_deficit_vars[r] = len(model_proto.variable)
    var_proto = model_proto.variable.add()
    var_proto.name = 'max_deficit_%d' % r
    var_proto.is_integer = False
    var_proto.lower_bound = 0.0
    var_proto.upper_bound = 1.0
    # We hard-code a separation between inf and L1 norms in the objective (the
    # former is always strictly more important than the latter).
    var_proto.objective_coefficient = 10.0 * num_bins * num_resources

  # for r, b:
  #   max_deficit(r) >= deficit(b, r)
  for b in range(num_bins):
    for r in range(num_resources):
      ct_proto = model_proto.constraint.add()
      ct_proto.name = 'max_deficit_ct_%d_%d' % (b, r)
      ct_proto.lower_bound = 0.0
      ct_proto.var_index.append(max_deficit_vars[r])
      ct_proto.coefficient.append(1.0)
      ct_proto.var_index.append(deficit_vars[b][r])
      ct_proto.coefficient.append(-1.0)

  return model_proto


def GenerateKnapsack(params: params_pb2.KnapsackParameters,
                     random_seed: int) -> params_pb2.Knapsack:
  random.seed(random_seed)
  knapsack = params_pb2.Knapsack()
  assert len(params.f_min) == len(params.f_max)
  knapsack.r = len(params.f_min)

  for item_param in params.item_param:
    num_items = random.randint(item_param.i_min, item_param.i_max)
    for i in range(num_items):
      item = knapsack.item.add()
      item.c = random.randint(item_param.c_min, item_param.c_max)
      item.d.extend([random.uniform(item_param.d_min[r], item_param.d_max[r])
                     for r in range(knapsack.r)])

  b = random.randint(params.b_min, params.b_max)
  t = [sum(item.d[r] for item in knapsack.item) for r in range(knapsack.r)]
  f = [random.uniform(params.f_min[r], params.f_max[r])
       for r in range(knapsack.r)]

  for _ in range(b):
    knapsack.bin.add().s.extend([f[r] * t[r] / b for r in range(knapsack.r)])
  return knapsack


def MPModelProtoToMPS(model_proto: linear_solver_pb2.MPModelProto):
  model_mps = pywraplp.ExportModelAsMpsFormat(model_proto)
  return model_mps


def BuildRandomizedModels(output: str, random_seed: int, num_models: int,
                          knapsack_params:
                          params_pb2.KnapsackParameters):
  for i in range(num_models):
    filename = output + '_%d.mps' % i
    logging.info('Building model %s', filename)
    knapsack = GenerateKnapsack(knapsack_params, random_seed + i)
    model = BuildMipForKnapsack(knapsack)
    model.name = 'Knapsack_%d' % i
    with open(filename, 'w') as mps_file:
      mps_file.write(MPModelProtoToMPS(model))


def main(_):
  knapsack_params = params_pb2.KnapsackParameters()
  if FLAGS.params_file:
    with open(FLAGS.params_file, 'r') as params_file:
      params_str = params_file.read()
      text_format.Merge(params_str, knapsack_params)
  text_format.Merge(FLAGS.params, knapsack_params)
  BuildRandomizedModels(FLAGS.out, FLAGS.seed, FLAGS.num, knapsack_params)


if __name__ == '__main__':
    app.run(main)
