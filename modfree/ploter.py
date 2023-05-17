import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import re
from modfree.inputs import read_relaxation_data_file


plt.rcParams['font.family'] = 'FreeSans'
plt.rcParams['legend.numpoints'] = 1
plt.rc('text', usetex=False)
plt.rcParams['mathtext.default'] = 'regular'
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
import seaborn as sns
sns.set()
sns.set_style("ticks", {"xtick.direction": "in", "ytick.direction": "in", "xtick.major.size": 8, "ytick.major.size": 8, 'font.family': ['FreeSans']})
sns.set_context("poster")
sns.set_palette('dark')
colors = ['blue', 'orange', 'red', 'darkred', 'black', 'darkblue', 'darkorange', 'maroon', 'purple', 'pink']


def check_output_dir(output_dir):
    if not os.path.isdir(output_dir+"/Plots"):
        os.mkdir(output_dir+"/Plots")


def plot_param(filename, color="darkblue", ax=None, log=False):
    with open(filename, "r") as f:
        dat = [el.rstrip("\n").split() for el in f.readlines()]
    x = [int(el[0]) for el in dat]
    if ax == None:
        fig, ax = plt.subplots(1, 1, figsize=(8, 5))
    if len(dat[0]) == 1:
        ax.plot(x, color=color)
    elif len(dat[0]) == 2:
        y = [float(el[1]) for el in dat]
        ax.plot(x, y, color=color)
    else:
        y = [float(el[1]) for el in dat]
        dy = [float(el[2]) for el in dat]
        ax.errorbar(x, y, yerr=dy, color=color)
    if log:
        ax.set_yscale("log")
    ax.set_xlabel("Sequence")
    ax.set_ylabel(filename.split("/")[-1].replace(".out", ""))
    ax.set_ylim(0.8*np.min(y), 1.2*np.max(y))


def plot_params_std(output_dir, file_format="pdf", dpi=600):
    check_output_dir(output_dir)
    param_files = glob.glob(output_dir+"/*.out")
    for el in param_files:
        log = True if re.search("tau", el) else False
        fig, ax = plt.subplots(1, 1, figsize=(8, 5))
        plot_param(el, ax=ax, log=log, color="darkblue")
        plt.savefig(output_dir+"/Plots/"+el.split("/")[-1].replace(".out", "."+file_format), format=file_format, dpi=dpi)
        plt.close()
    

def plot_statistics_std(output_dir, plotname, file_format="pdf", dpi=600):
    check_output_dir(output_dir)
    fig, ax = plt.subplots(3, 1, figsize=(8, 10))
    plot_param(output_dir+"/redchi2.out", color="darkblue", ax=ax[0], log=True)
    plot_param(output_dir+"/aic.out", color="darkblue", ax=ax[1])
    plot_param(output_dir+"/bic.out", color="darkblue", ax=ax[2])
    plt.savefig(output_dir+"/Plots/"+plotname, format=file_format, dpi=dpi)
    plt.close()
    
    
def plot_rates_corr_std(output_dir, plotname, file_format="pdf", dpi=600):
    check_output_dir(output_dir)
    rates_fit_dirs = sorted(glob.glob(output_dir+"/Relaxation_Rates/*.fit"))
    rates_exp_dirs = sorted(glob.glob(output_dir+"/Relaxation_Rates/*.exp"))
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    for i, rdir in enumerate(rates_exp_dirs):
        x, y1, dy1 = read_relaxation_data_file(rates_exp_dirs[i])
        x, y2, dy2 = read_relaxation_data_file(rates_fit_dirs[i])
        ax.plot([np.min(y1), np.max(y1)], [np.min(y1), np.max(y1)], lw=0.1, color="black")
        ax.errorbar(y1, y2, xerr=dy1, yerr=dy2, color="darkblue", ls="", marker="o")
    ax.set_ylabel("Calculated relaxation rates")
    ax.set_xlabel("Experimental relaxation rates")
    plt.savefig(output_dir+"/Plots/"+plotname, format=file_format, dpi=dpi)
    plt.close()


def plot_rates_std(output_dir, file_format="pdf", dpi=600):
    check_output_dir(output_dir)
    rates_fit_dirs = sorted(glob.glob(output_dir+"/Relaxation_Rates/*.fit"))
    rates_exp_dirs = sorted(glob.glob(output_dir+"/Relaxation_Rates/*.exp"))
    for i, rdir in enumerate(rates_exp_dirs):
        fig, ax = plt.subplots(1, 1, figsize=(10, 10))
        x1, y1, dy1 = read_relaxation_data_file(rates_exp_dirs[i])
        x2, y2, dy2 = read_relaxation_data_file(rates_fit_dirs[i])
        ax.plot(x1, y1, color="darkblue", label="Experiment")
        ax.fill_between(x1, np.array(y1)-np.array(dy1), np.array(y1)+np.array(dy1), color="darkblue", alpha=0.5)
        ax.plot(x2, y2, color="darkorange", label="Fit")
        ax.fill_between(x2, np.array(y2)-np.array(dy2), np.array(y2)+np.array(dy2), color="darkorange", alpha=0.5)
        ax.set_xlabel("Sequence")
        ax.set_ylabel(rdir.split("/")[-1].replace(".exp", ""))
        ax.legend(frameon=False)
        plt.savefig(output_dir+"/Plots/"+rdir.split("/")[-1].replace("exp", str(file_format)), format=file_format, dpi=dpi)
        plt.close()
