import numpy as np
import pandas as pd
import pickle

###
#Experiment
###

n_rep = 200

n_obs = 10000
n_alt = 1000

scale = 4.0
beta = np.array([
    1.5, -0.8, 
    1.5, 2.5, 1.5, 2.0,
    1.5, 2.5, 1.5, 1.0, 
    -1.2
    ])
n_att = beta.shape[0]

L = [2, 5, 10, 20, 50, 100, 200]

est = [np.zeros((n_rep, 4, n_att)) for l in L]
time = np.zeros((n_rep, len(L)))

###
#Extract results
###

for r in np.arange(n_rep):
    #Load results
    infile = open('results_soa_{}'.format(r+1), 'rb')
    results = pickle.load(infile)
    infile.close()
    
    for l_i, l in enumerate(L):
        est[l_i][r,:,:] = results['est'][l_i][0,:,:]
        time[r,l_i] = results['time'][0,l_i]

B_labels = results['B_labels']   

###
#Evaluate results
###

def describe(est, true, names):
    res = pd.DataFrame(index=names)
    beta = est[:,0,:]
    se = est[:,1,:]
    
    res['True'] = true
    res['MEV'] = beta.mean(axis=0)
    res['APB'] = np.abs((res['MEV'] - true) / true) * 100
    res['ASE'] = se.mean(axis=0)
    res['FSSE'] = beta.std(axis=0)
    res['APBASE'] = np.abs((res['ASE'] - res['FSSE']) / res['FSSE']) * 100
    
    true_arr = np.array(true).reshape(1,len(names))
    covered = np.logical_and(est[:,2,:] <= true_arr, true_arr <= est[:,3,:])
    res['Coverage'] = covered.mean(axis=0)
    
    apb = res['APB'].mean()
    ase = res['ASE'].mean()
    fsse = res['FSSE'].mean()
    apbase = res['APBASE'].mean()
    return res, apb, ase, fsse, apbase

res, apb, ase, fsse, apbase \
    = map(list, zip(*[describe(e, beta, B_labels) for e in est]))

###
#Write to latex
###

pd.options.display.max_colwidth = 1000

for l, res_l in zip(L, res):
    print(" ")
    print("l = {}".format(l))
    print(res_l)
    latex = res_l.to_latex(escape=True, float_format="%.3f")
    text_file = open("table_res_soa_l{}.tex".format(l), "w")
    text_file.write(latex)
    text_file.close()


time_tab = pd.DataFrame(data={'Est. time [s]': time.mean(axis=0), 
                              'APB': apb, 
                              'FSSE': fsse}, 
                              #'APBASE': apbase},
                        index=L)
print(time_tab)
latex = time_tab.to_latex(escape=True, float_format="%.3f")
text_file = open("table_res_soa.tex", "w")
text_file.write(latex)
text_file.close()