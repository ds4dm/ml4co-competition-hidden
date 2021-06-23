import csv
import pathlib
import random

import cplex


def anonymize_problem(in_file_path, out_file_path, name, file_format="mps"):
    cpx = cplex.Cplex(in_file_path)

    rename_problem(cpx, str(name))
    rename_vars(cpx)
    rename_cols(cpx)

    cpx.write(out_file_path, file_format)


def rename_problem(cpx: cplex.Cplex, new_name):
    cpx.set_problem_name(new_name)


def permutation(n: int):
    all_ints = list(range(n))
    random.shuffle(all_ints)
    return all_ints


def write_csv(d, f):
    with open(f, 'w') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in d.items():
            writer.writerow([key, value])


def rename_vars(cpx: cplex.Cplex, new_names=None):
    num_vars = cpx.variables.get_num()
    if not new_names:
        new_names = list(map(str, permutation(num_vars)))
    cpx.variables.set_names(zip(range(num_vars), new_names))


def rename_cols(cpx: cplex.Cplex, new_names=None):
    num_constraints = cpx.linear_constraints.get_num()
    if not new_names:
        new_names = list(map(str, permutation(num_constraints)))
    cpx.linear_constraints.set_names(zip(range(num_constraints), new_names))


def anonymize_all(in_dir, out_dir, file_ending="mps"):
    all_files = list(pathlib.Path(in_dir).glob(f"*.{file_ending}"))
    random.shuffle(all_files)
    file_name_mapping = {}
    for i, current_file in enumerate(all_files):
        print(f"Working on {current_file}.")
        new_file_path = pathlib.Path(out_dir).joinpath(f"{i}.{file_ending}")
        file_name_mapping[str(current_file.name)] = new_file_path.name
        anonymize_problem(str(current_file.absolute()),
                          str(new_file_path),
                          str(i),
                          file_ending.rstrip(".gz").rstrip(".bz"))
    return file_name_mapping


if __name__ == "__main__":
    file_name_mapping = anonymize_all("data/local/all_unanonimized",
                                      "data/all_anonymized",
                                      file_ending="mps.gz")
    write_csv(file_name_mapping, "mapping.csv")
