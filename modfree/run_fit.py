#!/usr/bin/env python
import modfree.data_format as df
import modfree.inputs as inputs
import modfree.mf as mf


def format_data(input_parameters_dic, directories):
    # format the data for the mf programm
    # outputs the data to fit and error to fit dictionnaries, in a metadictionnnary with all the residues.
    data = {f: {e: {x: y for (x,y,dy) in list(zip(*inputs.read_relaxation_data_file(directories[f][e])))} for e in directories[f].keys()} for f in directories.keys()}
    error = {f: {e: {x: dy for (x,y,dy) in list(zip(*inputs.read_relaxation_data_file(directories[f][e])))} for e in directories[f].keys()} for f in directories.keys()}
    data = df.swap(data, 1, 3)
    error = df.swap(error, 1, 3)
    return data, error


def run_fit(data, error, input_params):
    return mf.model_free(data, error, modes=input_params["modes"], mf_iterations=input_params["mf_minimization_iterations"], 
                               mc_iterations=input_params["monte_carlo_iterations"], mcmf_iterations=input_params["monte_carlo_minimization_iterations"],
                               **input_params["fix"])


def launch_fits(input_parameters_dic, residue, directories):
    data_dic, error_dic = format_data(input_parameters_dic, directories)
    if residue == 0:
        residue = input_parameters_dic["residues"]
    if residue == "all":
        results = dict()
        for res in sorted(list(data_dic.keys())):
            print("\nresidue", res)
            try:
                results[res] = run_fit(data_dic[res], error_dic[res], input_parameters_dic)
            except TypeError:
                print("TypeError exception, there is probably not enough data for this residue.")
    elif type(residue) == list or type(residue) == tuple:
        results = dict()
        for res in sorted(residue):
            if res not in data_dic.keys():
                print("\nresidue", res, "not in data")
                continue
            print("\nresidue", res)
            try:
                results[res] = run_fit(data_dic[res], error_dic[res], input_parameters_dic)
            except TypeError:
                print("TypeError exception, there is probably not enough data for this residue.")
    else:
        residue = int(residue)
        print("\nresidue", residue)
        try:
            results = {int(residue): run_fit(data_dic[int(residue)], error_dic[int(residue)], input_parameters_dic)}
        except ValueError:
            print("something is wrong with the residues settings in the parameter file")
            return None
        except KeyError:
            print("\nresidue", residue, "is not in the data")
            return None
        except TypeError:
            print("TypeError exception, there is probably not enough data for this residue.")
            return None
    return results


if __name__ == "__main__":
    print(format_data(inputs.read_parameter_file("parameters.txt"), "../../relaxation-data/dilute/"))
