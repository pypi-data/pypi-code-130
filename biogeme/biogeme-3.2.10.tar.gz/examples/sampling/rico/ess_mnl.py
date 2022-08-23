#!/usr/bin/env python
# coding: utf-8

# # Illustration of endogenous stratified sampling (ESS) sampling of observations in MNL
# Illustrated methods:
# * Conditional maximum likelihood (CML)
# * Weighted exogenous sample maximum likelihood (WESML)

# In[1]:


import numpy as np
import pandas as pd

import biogeme.database as db
import biogeme.biogeme as bio
import biogeme.models as models
from biogeme.expressions import Beta

np.random.seed(123)


# ## Load data

# In[2]:


df = pd.read_table('swissmetro.dat')

remove = ((df['PURPOSE'] != 1) & (df['PURPOSE'] != 3)) | (df['CHOICE'] == 0)
df = df[remove == False]

df['SM_COST'] = df['SM_CO'] * (df['GA'] == 0)
df['TRAIN_COST'] = df['TRAIN_CO'] * (df['GA'] == 0)

df['CAR_AV_SP'] = df['CAR_AV'] * (df['SP'] != 0)
df['TRAIN_AV_SP'] = df['TRAIN_AV'] * (df['SP'] != 0)

atts = ['TRAIN_TT', 'TRAIN_COST',
        'SM_TT', 'SM_COST',
        'CAR_TT', 'CAR_CO'
        ]
df = df.apply(lambda x: x / 100 if x.name in atts else x)


print(df['CHOICE'].value_counts(normalize=True))


# ## Estimate MNL on original data

# In[3]:


# Read the data
database = db.Database('swissmetro', df)

# The following statement allows you to use the names of the variable
# as Python variable.
globals().update(database.variables)

# Parameters to be estimated
ASC_TRAIN = Beta('ASC_TRAIN', 0, None, None, 0)
ASC_SM = Beta('ASC_SM', 0, None, None, 1)
ASC_CAR = Beta('ASC_CAR', 0, None, None, 0)
B_TIME = Beta('B_TIME', 0, None, None, 0)
B_COST = Beta('B_COST', 0, None, None, 0)

# Definition of the utility functions
V_TRAIN = ASC_TRAIN + B_TIME * TRAIN_TT + B_COST * TRAIN_COST
V_SM = ASC_SM + B_TIME * SM_TT + B_COST * SM_COST
V_CAR = ASC_CAR + B_TIME * CAR_TT + B_COST * CAR_CO

# Associate utility functions with the numbering of alternatives
V = {1: V_TRAIN,
     2: V_SM,
     3: V_CAR}

# Associate the availability conditions with the alternatives
av = {1: TRAIN_AV_SP,
      2: SM_AV,
      3: CAR_AV_SP}

# Definition of the model. This is the contribution of each
# observation to the log likelihood function.
# The choice model is a nested logit, with availability conditions
logprob = models.loglogit(V, av, CHOICE)

# Create the Biogeme object
biogeme = bio.BIOGEME(database, logprob)
biogeme.modelName = 'mnl'

# Estimate the parameters
results = biogeme.estimate()

# Get the results in a pandas table
pandasResults = results.getEstimatedParameters()
print(pandasResults)

alpha_names = ['ASC_TRAIN', 'ASC_CAR']
beta_names = ['B_TIME', 'B_COST']
param_names = alpha_names.copy()
param_names.extend(beta_names)

alpha = pandasResults['Value'][alpha_names].values
beta = pandasResults['Value'][beta_names].values
theta_true = np.concatenate((alpha, beta))


# ## Synthesise population

# In[4]:

df_pop = pd.concat([df for i in range(100)])

n_pop = df_pop.shape[0]
n_alt = 3

avail = df_pop[['TRAIN_AV_SP', 'SM_AV', 'CAR_AV_SP']].values

perturb = lambda x: x + 0.1 * x.std() * np.random.randn(x.shape[0])
df_pop = df_pop.apply(lambda x: perturb(x) if x.name in atts else x)

#Synthesise choices
v = np.zeros((n_pop, n_alt))
v[:,0] = alpha[0] + df_pop[['TRAIN_TT', 'TRAIN_COST']].values @ beta
v[:,1] = 0 + df_pop[['SM_TT', 'SM_COST']].values @ beta
v[:,2] = alpha[1] + df_pop[['CAR_TT', 'CAR_CO']].values @ beta

eps = -np.log(-np.log(np.random.rand(n_pop, n_alt)))
u = v + eps
u[avail==0] = np.nan
df_pop['CHOICE'] = np.nanargmax(u, axis=1) + 1


# ## Endogenous sampling of observations

# In[5]:


n_obs = 10000

strats = pd.DataFrame()
strats['w_g_n_p'] = df_pop['CHOICE'].value_counts().sort_index()
strats['w_g'] = strats['w_g_n_p'] / n_pop
strats['h_g'] = np.array([0.7, 0.1, 0.2])
strats['h_g_n_s'] = strats['h_g'] * n_obs
strats['r_g'] = strats['h_g_n_s'] / strats['w_g_n_p']
strats['log_r_g'] = np.log(strats['r_g'])
strats


# ## Experiment

# In[6]:

n_rep = 200

est_esml = np.zeros((n_rep, 4, len(param_names)))
est_cml = np.zeros((n_rep, 4, len(param_names)))
est_wesml = np.zeros((n_rep, 4, len(param_names)))

for r in range(n_rep):
    
    print("Sample {} of {}".format(r+1, n_rep))
    
    #Sample by endogenous stratification
    df_sample_list = []
    for idx, row in strats.iterrows(): 
        s = df_pop[df_pop['CHOICE']==idx].sample(n=int(row['h_g_n_s']), 
                                                 replace=False)
        s['weight'] = row['w_g'] / row['h_g']
        df_sample_list.append(s)
    df_sample = pd.concat(df_sample_list)                    
    
    ###
    #Estimate MNL via CML
    ###
    
    # Read the data
    database = db.Database('swissmetro', df_sample)
    
    # The following statement allows you to use the names of the variable
    # as Python variable.
    globals().update(database.variables)
    
    # Parameters to be estimated
    ASC_TRAIN = Beta('ASC_TRAIN', 0, None, None, 0)
    ASC_SM = Beta('ASC_SM', 0, None, None, 1)
    ASC_CAR = Beta('ASC_CAR', 0, None, None, 0)
    B_TIME = Beta('B_TIME', 0, None, None, 0)
    B_COST = Beta('B_COST', 0, None, None, 0)
    
    # Definition of the utility functions
    V_TRAIN = ASC_TRAIN + B_TIME * TRAIN_TT + B_COST * TRAIN_COST
    V_SM = ASC_SM + B_TIME * SM_TT + B_COST * SM_COST
    V_CAR = ASC_CAR + B_TIME * CAR_TT + B_COST * CAR_CO
    
    # Associate utility functions with the numbering of alternatives
    V = {1: V_TRAIN,
         2: V_SM,
         3: V_CAR}
    
    # Associate the availability conditions with the alternatives
    av = {1: TRAIN_AV_SP,
          2: SM_AV,
          3: CAR_AV_SP}
    
    # Definition of the model. This is the contribution of each
    # observation to the log likelihood function.
    # The choice model is a nested logit, with availability conditions
    logprob = models.loglogit(V, av, CHOICE)
    
    # Create the Biogeme object
    biogeme = bio.BIOGEME(database, logprob)
    biogeme.modelName = 'mnl_cml'
    
    # Estimate the parameters
    results = biogeme.estimate()
    
    # Get the results in a pandas table
    pandasResults = results.getEstimatedParameters()
    #print(pandasResults)
    
    est_esml[r,0,:] = np.array(pandasResults['Value'][param_names])
    est_esml[r,1,:] = np.array(pandasResults['Rob. Std err'][param_names])
    est_esml[r,2,:] = est_esml[r,0,:] - 1.96 * est_esml[r,1,:]
    est_esml[r,3,:] = est_esml[r,0,:] + 1.96 * est_esml[r,1,:]
    
    beta_cml_r = np.array(pandasResults['Value'][param_names])
    beta_cml_r[:2] += strats['log_r_g'].iloc[1] - strats['log_r_g'].iloc[[0,2]]
    
    est_cml[r,0,:] = beta_cml_r
    est_cml[r,1,:] = np.array(pandasResults['Rob. Std err'][param_names])
    est_cml[r,2,:] = est_cml[r,0,:] - 1.96 * est_cml[r,1,:]
    est_cml[r,3,:] = est_cml[r,0,:] + 1.96 * est_cml[r,1,:]
    
    ###
    #Estimate MNL via WESML
    ###
    
    # Read the data
    database = db.Database('swissmetro', df_sample)
    
    # The following statement allows you to use the names of the variable
    # as Python variable.
    globals().update(database.variables)
    
    # Parameters to be estimated
    ASC_TRAIN = Beta('ASC_TRAIN', 0, None, None, 0)
    ASC_SM = Beta('ASC_SM', 0, None, None, 1)
    ASC_CAR = Beta('ASC_CAR', 0, None, None, 0)
    B_TIME = Beta('B_TIME', 0, None, None, 0)
    B_COST = Beta('B_COST', 0, None, None, 0)
    
    # Definition of the utility functions
    V_TRAIN = ASC_TRAIN + B_TIME * TRAIN_TT + B_COST * TRAIN_COST
    V_SM = ASC_SM + B_TIME * SM_TT + B_COST * SM_COST
    V_CAR = ASC_CAR + B_TIME * CAR_TT + B_COST * CAR_CO
    
    # Associate utility functions with the numbering of alternatives
    V = {1: V_TRAIN,
         2: V_SM,
         3: V_CAR}
    
    # Associate the availability conditions with the alternatives
    av = {1: TRAIN_AV_SP,
          2: SM_AV,
          3: CAR_AV_SP}
    
    # Definition of the model. This is the contribution of each
    # observation to the log likelihood function.
    # The choice model is a nested logit, with availability conditions
    logprob = models.loglogit(V, av, CHOICE)
    
    # Create the Biogeme object
    formulas = {'loglike': logprob, 'weight': weight}
    biogeme = bio.BIOGEME(database, formulas)
    biogeme.modelName = 'mnl_wesml'
    
    # Estimate the parameters
    results = biogeme.estimate()
    
    # Get the results in a pandas table
    pandasResults = results.getEstimatedParameters()
    #print(pandasResults)
    
    beta_wesml_r = np.array(pandasResults['Value'][param_names])
    
    est_wesml[r,0,:] = beta_wesml_r
    est_wesml[r,1,:] = np.array(pandasResults['Rob. Std err'][param_names])
    est_wesml[r,2,:] = est_wesml[r,0,:] - 1.96 * est_wesml[r,1,:]
    est_wesml[r,3,:] = est_wesml[r,0,:] + 1.96 * est_wesml[r,1,:]
    


# ## Evaluate results

# In[7]:


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
    return res

res_esml = describe(est_esml, theta_true, param_names)
res_cml = describe(est_cml, theta_true, param_names)
res_wesml = describe(est_wesml, theta_true, param_names)

#Correction
corr = pd.DataFrame(index=param_names[:2])
corr['True'] = theta_true[:2]
corr['MEV - ESML'] = res_esml['MEV'].iloc[:2]
corr[r'$\ln R_{\text{Swissmetro}}$'] = strats['log_r_g'].iloc[-1]
corr[r'$\ln R_{g}$'] = strats['log_r_g'].iloc[:2].values
corr['MEV - CML'] = res_cml['MEV'].iloc[:2]

pd.options.display.max_colwidth = 1000
latex = corr.to_latex(escape=False, float_format="%.3f")
text_file = open("table_res_mnl_cml_correction.tex", "w")
text_file.write(latex)
text_file.close()


# ## Write to latex

# In[8]:


pd.options.display.max_colwidth = 1000
print(" ")
print("CML")
print(res_cml)
latex = res_cml.to_latex(escape=True, float_format="%.3f")
text_file = open("table_res_mnl_cml.tex", "w")
text_file.write(latex)
text_file.close()

print(" ")
print("WESML")
print(res_wesml)
latex = res_wesml.to_latex(escape=True, float_format="%.3f")
text_file = open("table_res_mnl_wesml.tex", "w")
text_file.write(latex)
text_file.close()

