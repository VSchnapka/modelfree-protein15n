import os
import glob
import re
import random as rd
import numpy as np
import modfree.data_format as df
import modfree.outputs as outputs
from modfree.mf_standard import give_params, calc_rates


def random_amp1(length):
    output = [rd.uniform(0, 1)]
    for i in range(1, length):
        idx, dat = 0, 1000
        while (dat > 0.4 or dat < 0) and idx < 10000:
            dat = rd.gauss(output[i-1], 0.1)
        output.append(dat)
    return np.array(output)


def random_amp2(length, amp1):
    output = [rd.uniform(0, 1)]
    for i in range(1, length):
        idx, dat = 0, 1000
        while (dat > 1-amp1[i] or dat < 0) and idx < 10000:
            dat = rd.gauss(output[i-1], 0.1)
        output.append(dat)
    return np.array(output)


def random_tau_50ps(length):
    output = [rd.gauss(50e-12, 5e-12)]
    for i in range(1, length):
        idx, dat = 0, 1000
        while (dat > 100e-12 or dat < 10e-12) and idx < 10000:
            dat = rd.gauss(50e-12, 5e-12)
        output.append(dat)
    return output


def random_tau_100ps(length):
    output = [rd.uniform(0.1e-9, 1e-9)]
    for i in range(1, length):
        idx, dat = 0, 1000
        while (dat > 1e-9 or dat < 0.1e-9) and idx < 10000:
            dat = rd.gauss(output[i-1], 0.1e-9)
        output.append(dat)
    return output


def random_tau_ns(length):
    output = [rd.uniform(2e-9, 20e-9)]
    for i in range(1, length):
        idx, dat = 0, 1000
        while (dat > 20e-9 or dat < 2e-9) and idx < 10000:
            dat = rd.gauss(output[i-1], 1e-9)
        output.append(dat)
    return output


def random_tumb_ns(length):
    output = [rd.uniform(2e-9, 20e-9)]
    for i in range(1, length):
        idx, dat = 0, 1000
        while (dat > 20e-9 or dat < 2e-9) and idx < 10000:
            dat = rd.gauss(output[0], 0.4e-9)
        output.append(dat)
    return output


def generate_directories_file_std(directory_with_the_directories):
    current_path = os.path.abspath(".")
    dirs = glob.glob(directory_with_the_directories+"/*/")
    with open(directory_with_the_directories+"/directories.toml", "w") as f:
        for d in dirs:
            field = re.findall("\d+", re.findall("\d+MHz", d, re.IGNORECASE)[0])[0]
            f.write(f"[generated-{field}]\n")
            f.write(f"directory = \"{current_path}/{d}\"\n")
            f.write(f"magnetic_field_MHz = {field}\n")
            f.write("\n")
            
            
def generate_parameter_file_std(directory_with_the_directories, fields, modes=2):
    with open(directory_with_the_directories+"/parameters.toml", "w") as f:
        f.write("# model free analysis parameter file. model choice: standard only so far\n")
        f.write(f"modes = {modes}\n")
        f.write(f"residues = \"all\"\n\n")
        f.write(f"# model dependent input parameters\n")
        f.write(f"magnetic_fields_MHz = {fields}\n\n")
        f.write(f"# parameters to fix: (taux, ampx, (x an integer that has to be compatible with the number of dynamic modes. Starts from 1.))\n")
        f.write(f"#tau1 = 50e-12\n\n")
        f.write(f"# minimization parameters\n")
        f.write(f"mf_minimization_iterations = 3\n")
        f.write(f"monte_carlo_iterations = 50\n")
        f.write(f"monte_carlo_minimization_iterations = 3\n")
    return None


def generate(N, output_dir, fields=(400, 600, 800, 1000, 1200), rates=('R1', 'R2', 'nOe', 'etaXY'), modes=2, noise_proportion=0.01):
    RES = np.arange(1, N+1)
    print("Parameter generation...")
    if modes == 1:
        amps = [1]
        taus = [random_tau_100ps(N)]
    elif modes == 2:
        a1 = random_amp1(N)
        amps = [a1, 1-a1]
        taus = [random_tau_100ps(N), random_tumb_ns(N)]
    elif modes == 3:
        a1 = random_amp1(N)
        a2 = random_amp2(N, a1)
        amps = [a1, a2, 1-a1-a2]
        taus = [random_tau_50ps(N), random_tau_100ps(N), random_tau_ns(N)]
    else:
        print("so far, only random data from 1, 2 or 3 dynamic modes can be generated")
        return None
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    RATES, ERROR = dict(), dict()
    print("Data calculation...")
    for i, r in enumerate(RES):
        params = give_params([el[i] for el in amps], [el[i] for el in taus])
        if noise_proportion == 0:
            rates, error = calc_rates(params, rates=rates, fields=fields, noise_proportion=noise_proportion), None
        else:
            rates, error = calc_rates(params, rates=rates, fields=fields, noise_proportion=noise_proportion)
        RATES[r] = rates
        ERROR[r] = error
        #[r][e][f]
    RATES = df.swap(RATES, 1, 3)
    ERROR = df.swap(ERROR, 1, 3)
    #[f][e][r]
    print("Data formating and saving...")
    for f in RATES.keys():
        if not os.path.isdir(output_dir+"/"+str(f)+"MHz"):
            os.mkdir(output_dir+"/"+str(f)+"MHz")
        for e in RATES[f].keys():
            x = RES
            y = [RATES[f][e][r] for r in x]
            dy = [ERROR[f][e][r] for r in x]
            outputs.save_param(x, y, dy=dy, outputname=output_dir+"/"+str(f)+"MHz/generated_"+str(e)+".txt")
    print("Data directory input generation...")
    generate_directories_file_std(output_dir)
    generate_parameter_file_std(output_dir, list(RATES.keys()), modes=modes)


if __name__ == "__main__":
    print("data generator module")
