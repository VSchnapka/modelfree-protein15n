import numpy as np
import random as rd
from lmfit import Minimizer, Parameters, report_fit
import gc
import re
import matplotlib.pyplot as plt
from rich.progress import track
from modfree.constants_functions import *


def C(t, amps, taus):
    if len(amps) == len(taus)-1:
        amps.append(1-sum(amps))
    elif len(amps) != len(taus):
        print("amps and taus length mismatch")
        return 1
    return sum([amps[i]*np.exp(-t/taus[i]) for i in range(len(taus))])


def j(omega, amps, taus):
    if len(amps) == len(taus)-1:
        amps.append(1-sum(amps))
    elif len(amps) != len(taus):
        print("amps and taus length mismatch")
        return 1
    return sum([amps[i]*taus[i]/(1 + ((omega**2)*(taus[i]**2))) for i in range(len(taus))])


def R1(x, amps, taus):
    def J(omega): return j(omega, amps, taus)
    field = x * 1e6 / (gamma1H/(2*np.pi))
    omegaN = gamma15N * field
    omegaH = gamma1H * field
    omega_sum = omegaH + omegaN
    omega_diff = omegaH - omegaN
    c = tCSA * omegaN
    return ((d**2)/10)*(6*J(omega_sum) + J(omega_diff) + 3*J(omegaN)) + (2/15)*(c**2)*J(omegaN)


def R2(x, amps, taus):
    def J(omega): return j(omega, amps, taus)
    field = x * 1e6 / (gamma1H/(2*np.pi))
    omegaN = gamma15N * field
    omegaH = gamma1H * field
    omega_sum = omegaH + omegaN
    omega_diff = omegaH - omegaN
    c = tCSA * omegaN
    return ((d**2)/20)*(6.0*J(omega_sum) + J(omega_diff) + 3*J(omegaN) + 6*J(omegaH) + 4*J(0)) + ((c**2)/45)*(3*J(omegaN) + 4*J(0))


def NOE(x, amps, taus):
    def J(omega): return j(omega, amps, taus)
    field = x * 1e6 / (gamma1H/(2*np.pi))
    omegaN = gamma15N * field
    omegaH = gamma1H * field
    omega_sum = omegaH + omegaN
    omega_diff = omegaH - omegaN
    return 1.0 + (d**2)/(10*R1(x, amps, taus)) * (gamma1H/gamma15N)*(6*J(omega_sum)-J(omega_diff))


def etaXY(x, amps, taus):
    def J(omega): return j(omega, amps, taus)
    field = x * 1e6 / (gamma1H/(2*np.pi))
    omegaN = gamma15N * field
    omegaH = gamma1H * field
    omega_sum = omegaH + omegaN
    omega_diff = omegaH - omegaN
    c = tCSA * omegaN
    return -(1/15)*d*c*P2(np.cos(theta))*(3*J(omegaN) + 4*J(0))


def etaZ(x, amps, taus):
    def J(omega): return j(omega, amps, taus)
    field = x * 1e6 / (gamma1H/(2*np.pi))
    omegaN = gamma15N * field
    omegaH = gamma1H * field
    omega_sum = omegaH + omegaN
    omega_diff = omegaH - omegaN
    c = tCSA * omegaN
    return -(1/15)*d*c*P2(np.cos(theta))*6*J(omegaN)


def get_params(params):
    """ returns amps and taus from param list """
    return params['amps'], params['taus'], params['Rex']


def give_params(amps, taus, Rex=0):
    return {'amps': amps, 'taus': taus, 'Rex': Rex}


def isRex(rate, Rex):
        if rate == 'R2':
            return Rex
        return 0


def minus_amps(length_amps):
    output = ''
    for i in range(length_amps):
        output = output + ' - '
        output = output + 'amp'+str(i+1)
    return output


def params(modes=2, parameters=None, vary_amps=True, vary_taus=True, exchange=False, **fix):
    """ generate parameters, inputs the nb of lorentzians wanted and outputs the params """
    params = Parameters()
    
    if parameters is not None:
        amps, taus, Rex = get_params(parameters)
        if 'Rex' in fix.keys():
            params.add('Rex', value=fix['Rex'], min=0, max=50, vary=False)
        else:
            params.add('Rex', value=Rex, min=0, max=50, vary=exchange)
        if len(amps) == len(taus):
            amps.pop()
        for i in range(modes):
            if i != modes-1:
                params.add('amp'+str(i+1), value=amps[i], min=0, max=1, vary=vary_amps)
            else:
                #params.add('amp'+str(i+1), expr='1'+minus_amps(len(amps)), min=0, max=1, vary=vary_amps) # makes a mess
                pass
            if 'tau'+str(i+1) in fix.keys():
                params.add('tau'+str(i+1), value=fix['tau'+str(i+1)], min=1e-12, max=5e-7, vary=False)
            else:
                params.add('tau'+str(i+1), value=taus[i], min=1e-12, max=5e-7, vary=vary_taus)
        return params

    amps = []
    if 'Rex' in fix.keys():
        params.add('Rex', value=fix['Rex'], min=0, max=50, vary=False)
    else:
        params.add('Rex', value=0, min=0, max=50, vary=exchange)
    for i in range(modes):
        term = sum(amps) if amps else 0
        if i == modes-1:
            #params.add('amp'+str(i+1), expr='1'+minus_amps(len(amps)), min=0, max=1, vary=vary_amps) # makes a mess
            pass
        else:
            amps.append((1-term)*rd.uniform(0, 0.6))
            params.add('amp'+str(i+1), value=amps[i], min=0, max=1, vary=vary_amps)
        if 'tau'+str(i+1) in fix.keys():
            params.add('tau'+str(i+1), value=fix['tau'+str(i+1)], min=1e-12, max=5e-7, vary=False)
        else:
            params.add('tau'+str(i+1), value=(10**i)*rd.uniform(1, 9)*1e-11, min=1e-12, max=5e-7, vary=vary_taus)
    return params


def x_y(data_dict, dev_data_dict=None):
    """ convert data dict to list of conditions and values for the minimize function (used in the fit function) """
    # data format: {rate: {field: value}}
    x = np.concatenate([[(rate, field) for field in data_dict[rate].keys()] for rate in data_dict.keys()])
    y = np.array(np.concatenate([[data_dict[rate][field] for field in data_dict[rate].keys()] for rate in data_dict.keys()]))
    if dev_data_dict:
        dy = np.array(np.concatenate([[dev_data_dict[rate][field] for field in dev_data_dict[rate].keys()] for rate in dev_data_dict.keys()]))
        return x, y, dy
    return x, y, None


def minfnc(params, conditions, rates, dev_rates=None):
    """ residues to minimize """
    methods = {'R1': R1, 'R2': R2, 'nOe': NOE, 'etaXY': etaXY, 'etaZ': etaZ, 'NOE': NOE}
    # data format: {rate: {field: value}}
    amps = [el.value for el in list(params.values()) if el.name[0] == 'a']
    taus = [el.value for el in list(params.values()) if el.name[0] == 't']
    Rex = params['Rex']
    data = rates
    # ex: [ r1,600 ; r1,700 ; r2,600 ; r2,700 ... ]
    model = np.array([methods[rate](int(field), amps, taus)+isRex(rate, Rex) for (rate, field) in conditions])
    #model = np.array(np.concatenate([[methods[rate](field, amps, taus) for field in data_dict[rate].keys()] for rate in data_dict.keys()]))
    if dev_rates is not None:
        return (data - model)/dev_rates
    return data - model


def fit(data_dict, modes=2, func2min=minfnc, parameters=None, method='leastsq', vary_amps=True, vary_taus=True, dev_data_dict=None, exchange=False, **fix):
    """ fitting function inputs data dictionnary {rate: {field: value}} and outputs lmfit result class """
    conditions, rates, dev_rates = x_y(data_dict, dev_data_dict=dev_data_dict)
    if parameters:
        minner = Minimizer(func2min, params(modes, parameters, vary_amps=vary_amps, vary_taus=vary_taus, exchange=exchange, **fix), fcn_args=(conditions, rates, dev_rates))
    else:
        minner = Minimizer(func2min, params(modes, vary_amps=vary_amps, vary_taus=vary_taus, exchange=exchange, **fix), fcn_args=(conditions, rates, dev_rates))#, fcn_args=(data_dict))
    result = minner.minimize(method=method)
    #report_fit(result)
    return result


def sort_params(result):
    """ get the amps and taus of the result class and sort them """
    values = result.params.valuesdict()
    #print("values: \n", values)
    amps, taus = [], []
    Rex = 0
    for k in values.keys():
        if re.match("amp*", k):
            amps.append((int(re.search("\d+", k).group()), values[k]))
        elif re.match("tau*", k):
            taus.append((int(re.search("\d+", k).group()), values[k]))
        elif re.match("Rex", k):
            Rex = values[k]
    amps = [el[1] for el in sorted(amps)]
    taus = [el[1] for el in sorted(taus)]
    if len(amps) == len(taus)-1:
        amps.append(1-sum(amps))
    modes = sorted(list(zip(taus, amps)))
    amps, taus = [el[1] for el in modes], [el[0] for el in modes]
    return {'amps': amps, 'taus': taus, 'Rex': Rex}


def fitting(data_to_fit, dev_data_to_fit=None, modes=2, use_weights=True, nb_iterations=20, fitting_method='leastsq', exchange=False, **fix):
    if use_weights:
        result = fit(data_to_fit, modes=modes, dev_data_dict=dev_data_to_fit, exchange=exchange, **fix)
    else:
        result = fit(data_to_fit, modes=modes, exchange=exchange, **fix)
    chi2, red_chi2, aic, bic = result.chisqr, result.redchi, result.aic, result.bic
    #print("chi2", chi2, "red_chi2", red_chi2, "aic", aic, "bic", bic)
    fit_params = sort_params(result)
    fit_amps, fit_taus, fit_Rex = get_params(fit_params)
    #methods = ['least_squares', 'trust-constr', 'nelder', 'lbfgsb', 'powell', 'cg', 'cobyla', 'bfgs', 'tnc', 'slsqp', 'shgo', 'leastsq']
    #         fast & eq< chi2    eq chi2+      fast   fast & eq chi2 fast  eq chi2   fast    eq chi2 slow eq chi2,eqchi2,fast,
    # jacobian needed for Newton methods and dogleg
    for i in range(nb_iterations): #fast but no better chi2
        #print("fit in process")
        if use_weights:
            #result = fit(data_to_fit, modes=modes, parameters=fit_params, method=fitting_method, dev_data_dict=dev_data_to_fit, exchange=exchange, **fix)
            result = fit(data_to_fit, modes=modes, method=fitting_method, dev_data_dict=dev_data_to_fit, exchange=exchange, **fix)
        else:
            #result = fit(data_to_fit, modes=modes, parameters=fit_params, method=fitting_method, exchange=exchange, **fix)
            result = fit(data_to_fit, modes=modes, method=fitting_method, exchange=exchange, **fix)
        if result.redchi < red_chi2:
            #print(fitting_method+" nice")
            chi2, red_chi2, aic, bic = result.chisqr, result.redchi, result.aic, result.bic
            #print("chi2", chi2, "red_chi2", red_chi2, "aic", aic, "bic", bic)
            fit_params = sort_params(result)
            fit_amps, fit_taus, fit_Rex = get_params(fit_params)
        #print(fit_params, chi2, red_chi2, aic, bic)
        #print(sum(fit_amps))
        return fit_params, chi2, red_chi2, aic, bic


def calc_rates(params, rates=('R1', 'R2', 'nOe', 'etaXY'), fields=(200, 400, 600, 700, 850, 950, 1200), noise_proportion=0):
    methods = {'R1': R1, 'R2': R2, 'nOe': NOE, 'etaXY': etaXY, 'etaZ': etaZ, 'NOE': NOE}
    amps, taus, Rex = get_params(params)
    output, errors = dict(), dict()
    for r in rates:
        if r in methods.keys():
            output[r] = {f: rd.gauss(methods[r](f, amps, taus), abs(methods[r](f, amps, taus)*noise_proportion))+isRex(r, Rex) for f in fields}
            if noise_proportion != 0:
                errors[r] = {f: abs(methods[r](f, amps, taus)*noise_proportion) for f in fields}
        else:
            print(f"{r} not in methods")
    if noise_proportion != 0:
        return output, errors
    return output


def calc_rates_from_tuples(params, r_f_tuples):
    methods = {'R1': R1, 'R2': R2, 'nOe': NOE, 'etaXY': etaXY, 'etaZ': etaZ, 'NOE': NOE}
    amps, taus, Rex = get_params(params)
    output = dict()
    rates = list(set([el[0] for el in r_f_tuples]))
    fields = list(set([el[1] for el in r_f_tuples]))
    for r in rates:
        output[r] = {f: methods[r](f, amps, taus)+isRex(r, Rex) for f in fields if (r, f) in r_f_tuples}
    return output


def generate_mc(data, error):
    output = dict()
    for r in data.keys():
        output[r] = {f: rd.gauss(data[r][f], error[r][f]) for f in data[r].keys()}
    return output


def monte_carlo(fitted_params, error_dict, modes=3, nb_iterations=50, mcmf_iterations=1, exchange=False, save_everything=False, verbose=True, **fix):
    tuples = []
    for r in error_dict.keys():
        for f in error_dict[r].keys():
            tuples.append((r, f))
    fitted_data_dict = calc_rates_from_tuples(fitted_params, tuples)
    
    mc_amps, mc_taus, mc_Rex, mc_chi2, mc_red_chi2 = [], [], [], [], []
    for i in track(range(nb_iterations), description='[green]Monte Carlo'):
        #if verbose:
            #print("monte iteration", i+1)
        mc_data, mc_error = generate_mc(fitted_data_dict, error_dict), {r: {k: error_dict[r][k] for k in error_dict[r].keys()} for r in error_dict.keys()}
        fit_mc_params, fit_mc_chi2, fit_mc_red_chi2, fit_mc_aic, fit_mc_bic = fitting(mc_data, dev_data_to_fit=mc_error, modes=modes, use_weights=True, nb_iterations=mcmf_iterations, fitting_method='leastsq', exchange=exchange, **fix)
        fit_mc_amps, fit_mc_taus, fit_mc_Rex = get_params(fit_mc_params)
        mc_amps.append(fit_mc_amps)
        mc_taus.append(fit_mc_taus)
        mc_Rex.append(fit_mc_Rex)
        mc_chi2.append(fit_mc_chi2)
        mc_red_chi2.append(fit_mc_red_chi2)
        #if verbose:
        #    print("chi2 = ", mc_chi2[i])
    mc_amps = [[el[i] for el in mc_amps] for i in range(len(mc_amps[0]))]
    mc_taus = [[el[i] for el in mc_taus] for i in range(len(mc_taus[0]))]

    dev_amps = [np.std(el) for el in mc_amps]
    dev_taus = [np.std(el) for el in mc_taus]
    dev_Rex = np.std(mc_Rex)
    #del mc_amps, mc_taus, mc_Rex, mc_chi2
    gc.collect()
    if save_everything:
        return give_params(dev_amps, dev_taus, dev_Rex), mc_red_chi2, mc_amps, mc_taus, mc_Rex
    return give_params(dev_amps, dev_taus, dev_Rex), mc_red_chi2


def model_free(data_dict, error_dict=None, modes=2, exchange=False, fitting_method='leastsq', use_weights=True, mc_iterations=20, mf_iterations=20, mcmf_iterations=1, save=0, output_format="model_free", **fix):
    #print("\n### Model Free Analysis ###\n")
    fit_params, chi2, red_chi2, aic, bic = fitting(data_dict, error_dict, modes=modes, use_weights=use_weights, nb_iterations=mf_iterations, fitting_method=fitting_method, exchange=exchange, **fix)
    print(f"Chi2 = {chi2:.2f}, reduced Chi2 = {red_chi2:.2f}")
    #print("Monte Carlo:")
    dev_params, red_chi2_distribution, all_amps, all_taus, all_Rex = monte_carlo(fit_params, error_dict, modes=modes, nb_iterations=mc_iterations, mcmf_iterations=mcmf_iterations, exchange=exchange, save_everything=True, **fix)
    return {"values": fit_params, "error": dev_params, "chi2": chi2, "red_chi2": red_chi2, "aic": aic, "bic": bic, "mc_red_chi2_distrib": red_chi2_distribution, "rates": data_dict, "rates_error": error_dict, "mc_amps": all_amps, "mc_taus": all_taus, "mc_Rex": all_Rex}
