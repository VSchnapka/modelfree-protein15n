# modelfree-protein15n
Model-Free analysis framework for protein backbone amide 15N NMR spin relaxation rates.

This command line based tool fits NMR relaxation data to a multi-Lorentzian spectral density function.
One can choose the number of Lorentzians (dynamic modes) for the fit.
Typically, one can perform 1, 2, and 3 dynamic mode MF analysis and see which model is most relevant for the data.
IMPACT analysis is also possible by fixing the chosen correlation times and fitting the amplitudes.

## Relevant litterature

Lipari & Szabo, Journal of the American Chemical Society (1982);
Halle, The Journal of chemical physics (2009);
Khan et al., Biophysical journal (2015)

# installation

    $ pip install modelfree-protein15n

You can create another environment for this tool if you python version is not compatible. 
If you have Anaconda for instance, you can run the following:

    $ conda create -n modfree python=3.9

To activate the environment with your terminal, run:

    $ conda activate modfree

You can then install and use the tool with the pip command in this environment.
To deactivate the environment, simply run:

    $ conda deactivate

# usage

The program is able to generate random relaxation data with the command 'modfree generate'.
The program is able to fit relaxation data to a model with the command 'modfree fit'.
The program is able to plot the results with the command 'modfree plot'.

## Data generation

To generate relaxation data, type the following command:

    $ modfree generate
    
The following flags are available:
-o (str): Output directory containing the generated data.
-modes (int): number of dynamic modes used to generate the data
-n (int): number of residues in the data
-noise (float): between 0 and 1, indicates the proportion of noise to put in the data. (0.03 by default)
-fields (list, int or float): Magnetic fields used for the rate generation in MHz.
-rates: relaxation rates to generate. by default R1, R2, NOE, etaXY.

For example, you can type:

    $ modfree generate -o Generated -modes 2 -n 70 -noise 0.05 -fields 600 700 850 950 1200 -rates R1 R2 NOE etaXY etaZ
    
## Data fitting

To fit relaxation data, you will need your data in a specific format akin to the generated data. Generate some data to see how it's done. You will also need a directory file and a parameter file. type the following command to fit the data generated in the previous section:

    $ modfree fit -o Generated_fit -d Generated/directories.toml -p Generated/parameters.toml
    
You can also fit only part of the data with the flag -r:

    $ modfree fit -o Generated_fit -d Generated/directories.toml -p Generated/parameters.toml -r 10 11 12 13 14 15 16 17
    
Or

    $ modfree fit -o Generated_fit -d Generated/directories.toml -p Generated/parameters.toml -r 15

## Data plotting

To plot the fitted data, just type:

    $ modfree plot -o Generated_fit -p all

The following flags are available:
-o (str): Output directory containing the data.
-p: What to plot (all, relaxation, parameters, statistics, correlation)
-format: Format of the plot files (pdf, png, jpg, svg...)
-dpi (600 by default)
