import numpy as np
import modfree.data_format as df
import modfree.mf as mf


def calc_relax_mc_error(result_dic, conditions):
    exp_rates = result_dic["rates"]
    mc_rates_error = dict()
    for i in range(len(result_dic["mc_amps"][0])):
        params = mf.give_params([result_dic["mc_amps"][j][i] for j in range(len(result_dic["mc_amps"]))], [result_dic["mc_taus"][j][i] for j in range(len(result_dic["mc_taus"]))])
        mc_rates_error[i] = mf.calc_rates_from_tuples(params, conditions)
    #[n][e][f]
    mc_rates_error = df.swap(df.swap(mc_rates_error, 1, 2), 2, 3)
    for e in mc_rates_error.keys():
        for f in mc_rates_error[e].keys():
            mc_rates_error[e][f] = np.std(list(mc_rates_error[e][f].values()))
    return mc_rates_error
            

def calc_rates_result(result_dic):
    exp_rates = result_dic["rates"]
    err_rates = result_dic["rates_error"]
    conditions = []
    for r in exp_rates.keys():
        for f in exp_rates[r].keys():
            conditions.append((r, int(f)))
    params = mf.give_params(result_dic["values"]["amps"], result_dic["values"]["taus"])
    fit_rates = mf.calc_rates_from_tuples(params, conditions)
    fit_error = calc_relax_mc_error(result_dic, conditions)
    return exp_rates, err_rates, fit_rates, fit_error


if __name__ == "__main__":
    pass
    #print(read_parameter_file("parameters.txt"))
