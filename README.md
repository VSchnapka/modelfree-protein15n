# modelfree-protein15n
Simple flexible model free analysis framework for protein backbone amide 15N NMR spin relaxation rates

The tool is flexible enough to allow spin relaxation data fitting with a chosen number of dynamic modes and the fixing of given variables.
Typically, one can perform 1, 2, and 3 dynamic mode MF analysis and see which model is most relevant for the data.
IMPACT analysis is also possible.

## Relevant litterature

Lipari & Szabo, Journal of the American Chemical Society (1982);
Halle, The Journal of chemical physics (2009);
Khan et al., Biophysical journal (2015)

# installation

    $ python setup.py install

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

    $ modfree fit -o Generated_fit -d Generated/directories.toml -p Generated/parameters.toml -r [10, 11, 12, 13, 14, 15, 16]
    
Or

    $ modfree fit -o Generated_fit -d Generated/directories.toml -p Generated/parameters.toml -r 15

## Data fitting

To plot the fitted data, just type:

    $ modfree plot -o Generated_fit -p all

The following flags are available:
-o (str): Output directory containing the data.
-p: What to plot (all, relaxation, parameters, statistics, correlation)
-format: Format of the plot files (pdf, png, jpg, svg...)
-dpi (600 by default)







    
