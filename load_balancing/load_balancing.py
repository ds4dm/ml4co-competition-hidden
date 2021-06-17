import logging
import random
import params_pb2
import gzip

from absl import app
from absl import flags

from google.protobuf import text_format
from ortools.linear_solver import linear_solver_pb2
from ortools.linear_solver import pywraplp

FLAGS = flags.FLAGS

flags.DEFINE_string(
    'params', '', 'Content of LoadBalancingParameters in text format. '
    'Takes precedence over FLAGS.params_file.')

flags.DEFINE_string(
    'params_file', '', 'Filepath to LoadBalancingParameters in text format. '
    'Takes precedence over LoadBalancingParameters default values.')

flags.DEFINE_string('out', '/tmp/load_balancing',
                    'Pattern where to store the generated MPS files.')

flags.DEFINE_integer('seed', 0, 'Random seed to use during generation.')

flags.DEFINE_integer('num', 1, 'How many models to generate.')


def BuildMipForLoadBalancing(
    problem: params_pb2.LoadBalancingProblem) -> linear_solver_pb2.MPModelProto:
  model_proto = linear_solver_pb2.MPModelProto()

  num_workloads = len(problem.workload)
  num_workers = len(problem.worker)

  # reserved_capacity_vars[s][t] contains the index of a continuous variable
  # denoting the capacity reserved on worker t for handling workload s.
  reserved_capacity_vars = [[None] * num_workers for _ in range(num_workloads)]
  for s in range(num_workloads):
    for t in range(num_workers):
      reserved_capacity_vars[s][t] = len(model_proto.variable)
      var_proto = model_proto.variable.add()
      var_proto.name = f'reserved_capacity_{s}_{t}'
      var_proto.lower_bound = 0.0
      var_proto.upper_bound = 0.0
    # capacity can be reserved only on allowed workers.
    for t in problem.workload[s].allowed_workers:
      model_proto.variable[reserved_capacity_vars[s]
                           [t]].upper_bound = problem.worker[t].capacity

  # worker_used_vars[t] contains the index of a binary variable denoting whether
  # worker t is used in the solution.
  worker_used_vars = [None] * num_workers
  for t in range(num_workers):
    worker_used_vars[t] = len(model_proto.variable)
    var_proto = model_proto.variable.add()
    var_proto.name = f'worker_used_{t}'
    var_proto.is_integer = True
    var_proto.lower_bound = 0.0
    var_proto.upper_bound = 1.0
    var_proto.objective_coefficient = problem.worker[t].cost

  # Capacity can be reserved only if a node is used.
  # For s, t: reserved_capacity_vars[s][t] <= M * worker_used_vars[t]
  # where M = max(worker[t].capacity, workload[s].load)
  for s in range(num_workloads):
    for t in range(num_workers):
      ct_proto = model_proto.constraint.add()
      ct_proto.name = f'worker_used_ct_{s}_{t}'
      ct_proto.lower_bound = 0
      ct_proto.var_index.append(reserved_capacity_vars[s][t])
      ct_proto.coefficient.append(-1)
      ct_proto.var_index.append(worker_used_vars[t])
      M = max(problem.worker[t].capacity, problem.workload[s].load)
      ct_proto.coefficient.append(M)

  # Cannot reserve more capacity than available.
  # For t: sum_s reserved_capacity_vars[s][t] <= worker[t].capacity
  for t in range(num_workers):
    ct_proto = model_proto.constraint.add()
    ct_proto.name = f'worker_capacity_ct_{t}'
    ct_proto.upper_bound = problem.worker[t].capacity
    for s in range(num_workloads):
      ct_proto.var_index.append(reserved_capacity_vars[s][t])
      ct_proto.coefficient.append(1)

  # There must be sufficient capacity for each workload in the scenario where
  # any one of the allowed workers is unavailable.
  # For s, t: sum_{t' != t} reserved_capacity_vars[s][t'] >= workload[s].load
  for s in range(num_workloads):
    allowed_workers = sorted(set(problem.workload[s].allowed_workers))
    assert len(allowed_workers) > 1
    for unavailable_t in allowed_workers:
      ct_proto = model_proto.constraint.add()
      ct_proto.name = f'workload_ct_{s}_failure_{unavailable_t}'
      ct_proto.lower_bound = problem.workload[s].load
      for t in allowed_workers:
        if t == unavailable_t:
          continue
        ct_proto.var_index.append(reserved_capacity_vars[s][t])
        ct_proto.coefficient.append(1)

  return model_proto


def GenerateLoadBalancingProblem(
    params: params_pb2.LoadBalancingParameters,
    random_seed: int) -> params_pb2.LoadBalancingProblem:
  random.seed(random_seed)
  problem = params_pb2.LoadBalancingProblem()

  # The index of the WorkerParameters that generated this worker.
  worker_group = []

  for (group, worker_param) in enumerate(params.worker_parameter):
    num_workers = random.randint(worker_param.i_min, worker_param.i_max)
    for _ in range(num_workers):
      worker_group.append(group)
      worker = problem.worker.add()
      worker.capacity = random.uniform(worker_param.capacity_min,
                                       worker_param.capacity_max)
      worker.cost = worker_param.cost

  for workload_param in params.workload_parameter:
    num_workloads = random.randint(workload_param.i_min, workload_param.i_max)
    assert len(workload_param.allowed_worker_probability) == len(
        params.worker_parameter)
    for _ in range(num_workloads):
      workload = problem.workload.add()
      workload.load = random.uniform(workload_param.load_min,
                                     workload_param.load_max)
      for worker_index in range(len(problem.worker)):
        if random.random() < workload_param.allowed_worker_probability[
            worker_group[worker_index]]:
          workload.allowed_workers.append(worker_index)

  return problem


def MPModelProtoToMPS(model_proto: linear_solver_pb2.MPModelProto):
  model_mps = pywraplp.ExportModelAsMpsFormat(model_proto)
  return model_mps


def BuildRandomizedModels(output: str, random_seed: int, num_models: int,
                          params: params_pb2.LoadBalancingParameters):
  for i in range(num_models):
    filename = output + '_%d.mps.gz' % i
    logging.info('Building model %s', filename)
    problem = GenerateLoadBalancingProblem(params, random_seed + i)
    model = BuildMipForLoadBalancing(problem)
    model.name = 'LoadBalancing_%d' % i
    with gzip.open(filename, 'wt') as mps_file:
      mps_file.write(MPModelProtoToMPS(model))


def main(_):
  params = params_pb2.LoadBalancingParameters()
  if FLAGS.params_file:
    with open(FLAGS.params_file, 'r') as params_file:
      params_str = params_file.read()
      text_format.Merge(params_str, params)
  text_format.Merge(FLAGS.params, params)
  BuildRandomizedModels(FLAGS.out, FLAGS.seed, FLAGS.num, params)


if __name__ == '__main__':
  app.run(main)
