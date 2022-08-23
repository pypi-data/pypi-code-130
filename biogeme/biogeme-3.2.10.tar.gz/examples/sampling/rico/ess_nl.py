#!/usr/bin/env python
# coding: utf-8

# # Illustration of endogenous stratified sampling (ESS) sampling of observations in nested logit (NL)
# Illustrated methods:
# * Exogenous sample maximum likelihood
# * Conditional maximum likelihood (CML)
# * Weighted exogenous sample maximum likelihood (WESML)

# In[1]:


import numpy as np
import pandas as pd
from scipy.special import logsumexp

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


# ## Estimate NL on original data

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

MU = Beta('MU', 1, 1, 10, 0)

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

#Definition of nests:
# 1: nests parameter
# 2: list of alternatives
existing = MU, [1, 3]
future = 1.0, [2]
nests = existing, future

# Definition of the model. This is the contribution of each
# observation to the log likelihood function.
# The choice model is a nested logit, with availability conditions
logprob = models.lognested(V, av, nests, CHOICE)

# Create the Biogeme object
biogeme = bio.BIOGEME(database, logprob)
biogeme.modelName = 'nl'

# Estimate the parameters
results = biogeme.estimate()

# Get the results in a pandas table
pandasResults = results.getEstimatedParameters()
print(pandasResults)

alpha_names = ['ASC_TRAIN', 'ASC_CAR']
beta_names = ['B_TIME', 'B_COST']
mu_names = ['MU']
param_names = alpha_names.copy()
param_names.extend(beta_names)
param_names.extend(mu_names)

alpha = pandasResults['Value'][alpha_names].values
beta = pandasResults['Value'][beta_names].values
mu = pandasResults['Value'][mu_names].values
theta_true = np.concatenate((alpha, beta, mu))
mu = np.append(mu, 1.0)

# ## Synthesise population

# In[4]:
    
np.random.seed(123)

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

nests = [[0, 2], [1]]
alt_nest = [0, 1, 0]
log_g = np.zeros((n_pop, n_alt))
for j, k in enumerate(alt_nest):
    log_g[:,j] += (mu[k] - 1) * v[:,j]
    log_g[:,j] += (1/mu[k] - 1) * logsumexp(mu[k] \
                   * v[:,nests[k]].reshape(n_pop, len(nests[k])), axis=1, 
                   b=avail[:,nests[k]])

eps = -np.log(-np.log(np.random.rand(n_pop, n_alt)))
u = v + log_g + eps
u[avail==0] = np.nan
df_pop['CHOICE'] = np.nanargmax(u, axis=1) + 1


###
#Check log-lik
###

# v = np.zeros((n_pop, n_alt))
# v[:,0] = alpha[0] + df_pop[['TRAIN_TT', 'TRAIN_COST']].values @ beta
# v[:,1] = 0 + df_pop[['SM_TT', 'SM_COST']].values @ beta
# v[:,2] = alpha[1] + df_pop[['CAR_TT', 'CAR_CO']].values @ beta

# log_g = np.zeros((n_pop, n_alt))
# for j, k in enumerate(alt_nest):
#     log_g[:,j] += (mu[k] - 1) * v[:,j]
#     log_g[:,j] += (1/mu[k] - 1) * logsumexp(mu[k] \
#                   * v[:,nests[k]].reshape(n_pop, len(nests[k])), axis=1, 
#                   b=avail[:,nests[k]])

# y = v + log_g
# choice = df['CHOICE'].values
# lp_numer = np.zeros(n_pop,)
# for i in np.arange(n_pop):
#     lp_numer[i] = y[i,choice[i]-1]
# lp_denom = logsumexp(y, axis=1, b=avail)
# lp = lp_numer - lp_denom
# ll = np.sum(lp)
# print('Own log-lik:', ll)
# print('Biogeme log-lik:', results.data.logLike)


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
correction = strats['log_r_g'].values
strats


# ## Experiment

# In[6]:


n_rep = 200

methods = ['ml', 'wcml', 'wesml']

est = {m: np.zeros((n_rep, 4, len(param_names))) for m in methods}

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
    #Estimate MNL via ML
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
    
    MU = Beta('MU', 1, 1, 10, 0)
    
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
    
    #Definition of nests:
    # 1: nests parameter
    # 2: list of alternatives
    existing = MU, [1, 3]
    future = 1.0, [2]
    nests = existing, future
    
    # Definition of the model. This is the contribution of each
    # observation to the log likelihood function.
    # The choice model is a nested logit, with availability conditions
    logprob = models.lognested(V, av, nests, CHOICE)
    
    # Create the Biogeme object
    biogeme = bio.BIOGEME(database, logprob)
    biogeme.modelName = 'nl_ml'
    
    # Estimate the parameters
    results = biogeme.estimate()
    
    # Get the results in a pandas table
    pandasResults = results.getEstimatedParameters()
    #print(pandasResults)
    
    beta_ml_r = np.array(pandasResults['Value'][param_names])
    
    est['ml'][r,0,:] = beta_ml_r
    est['ml'][r,1,:] = np.array(pandasResults['Rob. Std err'][param_names])
    est['ml'][r,2,:] = est['ml'][r,0,:] - 1.96 * est['ml'][r,1,:]
    est['ml'][r,3,:] = est['ml'][r,0,:] + 1.96 * est['ml'][r,1,:]               

    ###
    #Estimate NL via WCML
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
    
    MU = Beta('MU', 1, 1, 10, 0)
    
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
    
    #Definition of nests:
    # 1: nests parameter
    # 2: list of alternatives
    existing = MU, [1, 3]
    future = 1.0, [2]
    nests = existing, future
    
    #Sampling correction
    G = models.getMevForNested(V, av, nests)
    H = {i: v + G[i] + correction[i-1] for i, v in V.items()}
    
    # Definition of the model. This is the contribution of each
    # observation to the log likelihood function.
    # The choice model is a nested logit, with availability conditions
    #logprob = models.lognested(V, av, nests, CHOICE)
    logprob = models.loglogit(H, av, CHOICE)
    
    # Create the Biogeme object
    biogeme = bio.BIOGEME(database, logprob)
    biogeme.modelName = 'nl_wcml'
    
    # Estimate the parameters
    results = biogeme.estimate()
    
    # Get the results in a pandas table
    pandasResults = results.getEstimatedParameters()
    #print(pandasResults)
    
    beta_wcml_r = np.array(pandasResults['Value'][param_names])
    beta_wcml_r = np.array(pandasResults['Value'][param_names])
    
    est['wcml'][r,0,:] = beta_wcml_r
    est['wcml'][r,1,:] = np.array(pandasResults['Rob. Std err'][param_names])
    est['wcml'][r,2,:] = est['wcml'][r,0,:] - 1.96 * est['wcml'][r,1,:]
    est['wcml'][r,3,:] = est['wcml'][r,0,:] + 1.96 * est['wcml'][r,1,:]   
    
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
    
    MU = Beta('MU', 1, 1, 10, 0)
    
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
    
    #Definition of nests:
    # 1: nests parameter
    # 2: list of alternatives
    existing = MU, [1, 3]
    future = 1.0, [2]
    nests = existing, future
    
    # Definition of the model. This is the contribution of each
    # observation to the log likelihood function.
    # The choice model is a nested logit, with availability conditions
    logprob = models.lognested(V, av, nests, CHOICE)
    
    # Create the Biogeme object
    formulas = {'loglike': logprob, 'weight': weight}
    biogeme = bio.BIOGEME(database, formulas)
    biogeme.modelName = 'nl_wesml'
    
    # Estimate the parameters
    results = biogeme.estimate()
    
    # Get the results in a pandas table
    pandasResults = results.getEstimatedParameters()
    #print(pandasResults)
    
    beta_wesml_r = np.array(pandasResults['Value'][param_names])
    
    est['wesml'][r,0,:] = beta_wesml_r
    est['wesml'][r,1,:] = np.array(pandasResults['Rob. Std err'][param_names])
    est['wesml'][r,2,:] = est['wesml'][r,0,:] - 1.96 * est['wesml'][r,1,:]
    est['wesml'][r,3,:] = est['wesml'][r,0,:] + 1.96 * est['wesml'][r,1,:]
    


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

res = {m: describe(est[m], theta_true, param_names) for m in methods}


# ## Write to latex

# In[8]:


pd.options.display.max_colwidth = 1000

for m in methods:
    print(" ")
    print(m)
    print(res[m])
    latex = res[m].to_latex(escape=True, float_format="%.3f")
    text_file = open("table_res_nl_{}.tex".format(m), "w")
    text_file.write(latex)
    text_file.close()

