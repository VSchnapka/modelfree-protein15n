from argparse import ArgumentParser
from argparse import Namespace
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import modfree.data_format as df
import modfree.inputs as inputs
import modfree.outputs as outputs
import modfree.run_fit as run_fit
import modfree.ploter as ploter
import modfree.generator as generator


__version__ = "0.0.1"


console = Console()


header = "\n".join(
[
    r"  _______ __           ___    ___       _______   ",
    r" |  ____// /____  __  |   \  /   |     |  ____/   ",
    r" | |__  / / _ \ \/ /  | |\ \/ /| |     | |__      ",
    r" |  _/ / /  __/ _ /\  | | \__/ | |     |  _/   15 ",
    r" |_|  /_/\___/_/  \_\ |_|      |_|odel |_|ree    N",
    "",
    "",
])


def introduction_print():
    logo = Text(header, style="red")
    description1= Text("Flexible Model Free analysis\n", style="cyan")
    description2= Text("of protein backbone amide nitrogen\n", style="cyan")
    description3= Text("NMR spin relaxation data\n", style="cyan")
    description4= Text("15N-1H Dipolar and 15N CSA conributions to relaxation\n", style="blue")
    description5= Text("Monte Carlo error estimation\n", style="blue")
    merged_text = Text.assemble(logo, description1, description2, description3, description4, description5)
    panel = Panel.fit(merged_text)
    console.print(panel)


def plot(args: Namespace):
    data_file = args.o
    what_to_plot = args.p
    if what_to_plot == "relaxation" or what_to_plot == "all":
        ploter.plot_rates_std(output_dir=data_file, file_format=args.format, dpi=args.dpi)
    if what_to_plot == "parameters" or what_to_plot == "all":
        ploter.plot_params_std(output_dir=data_file, plotname="parameters."+str(args.format), file_format=args.format, dpi=args.dpi)
    if what_to_plot == "statistics" or what_to_plot == "all":
        ploter.plot_statistics_std(output_dir=data_file, plotname="statistics."+str(args.format), file_format=args.format, dpi=args.dpi)
    if what_to_plot == "correlation" or what_to_plot == "all":
        ploter.plot_rates_corr_std(output_dir=data_file, plotname="correlation."+str(args.format), file_format=args.format, dpi=args.dpi)


def fit(args: Namespace):
    data_files = inputs.read_directory_file(args.d, args.m)
    input_parameters = inputs.read_parameter_file(args.p, args.m)
    result = run_fit.launch_fits(input_parameters, args.r, data_files, model=args.m)
    outputs.save_params(result, directory=args.o)
    df.Save(result, args.o+"/rawoutput.txt")
    if args.plot:
        ploter.plot_params_std(output_dir=data_file, plotname="parameters."+str(args.format), file_format=args.format, dpi=args.dpi)
        ploter.plot_statistics_std(output_dir=data_file, plotname="statistics."+str(args.format), file_format=args.format, dpi=args.dpi)
        ploter.plot_rates_corr_std(output_dir=data_file, plotname="correlation."+str(args.format), file_format=args.format, dpi=args.dpi)
        ploter.plot_rates_std(output_dir=data_file, file_format=args.format, dpi=args.dpi)


def generate(args: Namespace):
    generator.generate(args.n, args.o, fields=args.fields, rates=args.rates, modes=args.modes, noise_proportion=args.noise)


def build_parser():
    parser = ArgumentParser(description="model free analysis framework for backbone amid 15N spin relaxation analysis")

    subparsers = parser.add_subparsers(dest="commands")

    fit_parser = subparsers.add_parser("fit", help="Fit the data")
    fit_parser.set_defaults(func=fit)
    fit_parser.add_argument('-o', type=str, help="output directory", default="Outputs")
    fit_parser.add_argument('-d', type=str, help="directory file. toml file. contains the directories and the corresponding conditions", default="directories.toml")
    fit_parser.add_argument('-p', type=str, help="parameter file. toml file", default="params.toml")
    fit_parser.add_argument('-r', type=str, help="residue to analyse. can be 'all' or a number corresponding to the residue number.", default="None")
    fit_parser.add_argument('-m', type=str, help="fitting model: standard (std), arrhenius (arrh), viscosity (visc), arrhenius-viscosity (arvi).", default="std")
    fit_parser.add_argument('-plot', type=bool, help="plot the output", default=False)
    
    plot_parser = subparsers.add_parser("plot", help="Plot the data")
    plot_parser.set_defaults(func=plot)
    plot_parser.add_argument('-o', type=str, help="output directory", default="Outputs")
    plot_parser.add_argument('-p', type=str, help="what to plot: all, relaxation, parameters, statistics, correlation", default="all")
    plot_parser.add_argument('-format', type=str, help="file format: pdf, jpg, png, svg", default="pdf")
    plot_parser.add_argument('-dpi', type=int, help="output resolution", default=600)
    
    gen_parser = subparsers.add_parser("generate", help="generate some fake random relaxation data")
    gen_parser.set_defaults(func=generate)
    gen_parser.add_argument('-o', type=str, help="output directory", default="Generated")
    gen_parser.add_argument('-modes', type=int, help="number of dynamic modes for the generation (1,2,3)", default=2)
    gen_parser.add_argument('-n', type=int, help="number of residues in the fake data", default=100)
    gen_parser.add_argument('-noise', type=float, help="proportion of noise in the data. default is 3% (0.03)", default=0.03)
    gen_parser.add_argument('-fields', type=float, nargs="+", help="magnetic fields for the generated relaxation rates in MHz", default=(400,600,800,1000,1200))
    gen_parser.add_argument('-rates', type=float, nargs="+", help="relaxation rates to generate", default=("R1", "R2", "NOE", "etaXY"))
    
    return parser


def main():
    introduction_print()
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
