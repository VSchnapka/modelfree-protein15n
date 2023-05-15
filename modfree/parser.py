from argparse import ArgumentParser
import modfree.modfree


def parse():
    parser = ArgumentParser(description="model free analysis framework for backbone amid 15N spin relaxation analysis")
    parser.add_argument('-d', type=str, help="directory file. toml file. contains the directories and the corresponding conditions", default="params.toml")
    parser.add_argument('-p', type=str, help="parameter file. toml file", default="params.toml")
    parser.add_argument('-r', type=str, help="residue to analyse. can be 'all' or a number corresponding to the residue number.", default="None")
    parser.add_argument('-m', type=str, help="fitting model: standard (std), arrhenius (arrh), viscosity (visc), arrhenius-viscosity (arvi).", default="std")
    parser.add_argument('-o', type=str, help="output directory", default="Outputs")
    return parser.parse_args()


def build_parser():
    parser = ArgumentParser(description="model free analysis framework for backbone amid 15N spin relaxation analysis")
    parser.add_argument('-o', type=str, help="output directory", default="Outputs")

    subparsers = parser.add_subparsers(dest="commands")

    fit_parser = subparsers.add_parser("fit", help="Fit the data")
    fit_parser.set_defaults(func=modfree.fit)
    parser.add_argument('-d', type=str, help="directory file. toml file. contains the directories and the corresponding conditions", default="params.toml")
    parser.add_argument('-p', type=str, help="parameter file. toml file", default="params.toml")
    parser.add_argument('-r', type=str, help="residue to analyse. can be 'all' or a number corresponding to the residue number.", default="None")
    parser.add_argument('-m', type=str, help="fitting model: standard (std), arrhenius (arrh), viscosity (visc), arrhenius-viscosity (arvi).", default="std")
    parser.add_argument('-plot', type=bool, help="plot the output", default=False)
    
    plot_parser = subparsers.add_parser("plot", help="Plot the data")
    fit_parser.set_defaults(func=modfree.plot)
    parser.add_argument('-p', type=str, help="what to plot: all, relaxation, parameters, statistics, correlation", default="all")
    parser.add_argument('-format', type=str, help="file format: pdf, jpg, png, svg", default="pdf")
    parser.add_argument('-dpi', type=int, help="output resolution", default=600)
    
    return parser


if __name__ == "__main__":
    args = build_parser().parse_args()
    print(args.i)
    print(args.t)
    print(args.o)
