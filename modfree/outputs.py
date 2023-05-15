import os
import modfree.data_format as df
import modfree.analysis as analysis


def save_param(x, y=None, dy=None, outputname="test.txt"):
    with open(outputname, "w") as f:
        if y is None:
            for el in x:
                f.write(str(el)+"\n")
        elif dy is None:
            for i, res in enumerate(x):
                f.write(str(res)+"  "+str(y[i])+"\n")
        else:
            for i, res in enumerate(x):
                f.write(str(res)+"  "+str(y[i])+"  "+str(dy[i])+"\n")


def save_params(result_dic, directory, model="std"):
    #print(result_dic)
    if model != "std":
        print("other models not implemented so far in save_params")
        return None
    if not os.path.isdir(directory):
        os.mkdir(directory)
    if directory[-1] != "/":
        directory = directory + "/"
    values = df.swap(result_dic, 1, 2)['values']
    #values = df.swap(values, 2, 3) # values[res][amps/taus][0,1,2,...]
    errors = df.swap(result_dic, 1, 2)['error']
    #errors = df.swap(errors, 2, 3)
    X = [res for res in values.keys()]
    # residue specific monte carlo results
    if not os.path.isdir(directory+"Monte_Carlo"):
        os.mkdir(directory+"Monte_Carlo")
    for res in X:
        if not os.path.isdir(directory+"Monte_Carlo/"+str(res)):
            os.mkdir(directory+"Monte_Carlo/"+str(res))
        save_param(result_dic[res]['mc_red_chi2_distrib'], outputname=directory+"Monte_Carlo/"+str(res)+"/mc_redchi2.out")
        for i in range(len(result_dic[res]['mc_taus'])):
            save_param(result_dic[res]['mc_taus'][i], outputname=directory+"Monte_Carlo/"+str(res)+"/mc_tau"+str(i+1)+".out")
            save_param(result_dic[res]['mc_amps'][i], outputname=directory+"Monte_Carlo/"+str(res)+"/mc_amp"+str(i+1)+".out")
    # experimental and back calculated relaxation rates
    if not os.path.isdir(directory+"Relaxation_Rates/"):
        os.mkdir(directory+"Relaxation_Rates/")
    rates = {"fit": dict(), "exp": dict(), "err": dict(), "fiterr": dict()}
    for res in X:
        exp_rates, err_rates, fit_rates, fit_error = analysis.calc_rates_result(result_dic[res], model=model)
        rates["fit"][res] = fit_rates
        rates["fiterr"][res] = fit_error
        rates["exp"][res] = exp_rates
        rates["err"][res] = err_rates
        # rates[exp/fit][res][e][f]
    rates = df.swap(rates, 2, 4)
    for f in rates["exp"].keys():
        for e in rates["exp"][f].keys():
            x = list(rates["exp"][f][e].keys())
            y = [rates["exp"][f][e][r] for r in x]
            dy = [rates["err"][f][e][r] for r in x]
            save_param(x, y, dy, outputname=directory+"Relaxation_Rates/"+str(f)+"_"+str(e)+".exp")
            x = list(rates["fit"][f][e].keys())
            y = [rates["fit"][f][e][r] for r in x]
            dy = [rates["fiterr"][f][e][r] for r in x]
            save_param(x, y, dy, outputname=directory+"Relaxation_Rates/"+str(f)+"_"+str(e)+".fit")
    save_param(X, [result_dic[res]['red_chi2'] for res in X], outputname=directory+"redchi2.out")
    save_param(X, [result_dic[res]['aic'] for res in X], outputname=directory+"aic.out")
    save_param(X, [result_dic[res]['bic'] for res in X], outputname=directory+"bic.out")
    for i in range(len(values[list(values.keys())[0]]["taus"])):
        save_param(X, [values[res]['amps'][i] for res in X], dy=[errors[res]['amps'][i] for res in X], outputname=directory+"amp"+str(i+1)+".out")
        save_param(X, [values[res]['taus'][i] for res in X], dy=[errors[res]['taus'][i] for res in X], outputname=directory+"tau"+str(i+1)+".out")


if __name__ == "__main__":
    pass
    #print(read_parameter_file("parameters.txt"))
