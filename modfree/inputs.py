import re
import glob
import tomli
import numpy as np


def read_relaxation_data_file(filedir):
    with open(filedir, "r") as f:
        dat = [el.rstrip("\n").split() for el in f.readlines()]
    x = [int(el[0]) for el in dat]
    y = [float(el[1]) for el in dat]
    dy = [float(el[2]) for el in dat]
    return x, y, dy


def read_directory_file(filename="directories.toml", model="std"):
    rates = "R1", "R2", "NOE", "etaXY", "etaZ"
    if model != "std":
        print("in read directory file function: models other than std not yet implemented")
        return None
    if model == "std":
        with open(filename, "rb") as f:
            toml_dict = tomli.load(f)
        dirs = dict()
        for k in toml_dict.keys():
            files = glob.glob(toml_dict[k]['directory']+"/*")
            for f in files:
                rate = re.findall('r1|r2|noe|etaxy|etaz', f, re.IGNORECASE)
                rate = '' if rate == [] else rate[0]
                for e in rates:
                    match = re.search(rate, e, re.IGNORECASE)
                    if match and match.group(0) != '':
                        if toml_dict[k]['magnetic_field_MHz'] not in dirs.keys():
                            dirs[toml_dict[k]['magnetic_field_MHz']] = dict()
                        dirs[toml_dict[k]['magnetic_field_MHz']][e] = f
    return dirs


def read_parameter_file(param_file, model="std"):
    if model != "std":
        print("in read directory file function: models other than std not yet implemented")
        return None
    if model == "std":
        with open(param_file, "rb") as f:
            toml_dict = tomli.load(f)
        parameters = {"modes": toml_dict["modes"], "mf_minimization_iterations": toml_dict["mf_minimization_iterations"], "monte_carlo_iterations": toml_dict["monte_carlo_iterations"],
                      "monte_carlo_minimization_iterations": toml_dict["monte_carlo_minimization_iterations"],
                      "magnetic_fields_MHz": toml_dict["magnetic_fields_MHz"], "residues": toml_dict["residues"]}
        fix_regex_pattern = "tau\d+|amp\d+"
        parameters["fix"] = {k: val for k, val in toml_dict.items() if k not in parameters.keys() and re.match(fix_regex_pattern, k)}
    return parameters


if __name__ == "__main__":
    print(read_parameter_file("parameters.txt"))
