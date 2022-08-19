import numpy as np
import pandas as pd
import os
import pickle

import biogeme.database as db
import biogeme.biogeme as bio
import biogeme.models as models
from biogeme.expressions import Beta

###
#Data generation
###

def gen_data(n_obs, n_alt, beta, scale):
    
    #Generate alternatives
    X_alts = pd.DataFrame()
    
    X_alts['rating'] = np.random.choice(np.arange(1,6), size=n_alt, 
                                        replace=True, 
                                        p=np.array([0.1, 0.1, 0.2, 0.4, 0.2]))
    X_alts['price'] = np.random.choice(np.arange(1,5), size=n_alt, 
                                        replace=True, 
                                        p=np.array([0.3, 0.4, 0.2, 0.1]))
    
    cat_labels = ['American', 'Chinese', 'Japanese', 'Korean', 'Indian',
                  'French', 'Mexican', 'Lebanese', 'Ethiopian']
    cat_probs = np.array([0.3, 0.1, 0.075, 0.1, 0.075, 
                          0.05, 0.15, 0.075, 0.075])
    cat = np.random.choice(cat_labels, size=n_alt, replace=True, p=cat_probs)
    for c in cat_labels[1:]:
        X_alts['category_{}'.format(c)] = 1 * (cat == c)
        
    X_alts['rest_lat'] = np.random.rand(n_alt) * 100
    X_alts['rest_lon']  = np.random.rand(n_alt) * 100
    
    #Generate users
    X_user = pd.DataFrame()
    
    X_user['user_lat'] = np.random.rand(n_obs) * 100
    X_user['user_lon']  = np.random.rand(n_obs) * 100
    
    #Design matrix
    X = pd.DataFrame(data=np.repeat(np.array(X_user), n_alt, axis=0), 
                     columns=X_user.columns)
    X_alts_obs = pd.DataFrame(data=np.tile(np.array(X_alts), (n_obs,1)), 
                              columns=X_alts.columns)
    X = pd.concat((X, X_alts_obs), axis=1)
    
    X['log_dist'] = np.log(np.sqrt((X['user_lat'] - X['rest_lat'])**2                                    
                                   + (X['user_lon'] - X['rest_lon'])**2))
    
    X.drop(columns=['rest_lat', 'rest_lon', 'user_lat', 'user_lon'], 
           inplace=True)
    
    #Synthesise choices
    v = np.array(np.array(X) @ beta).reshape(n_obs, n_alt)
    
    eps = -np.log(-np.log(np.random.rand(n_obs, n_alt)))
    u = scale * v + eps
    choice = u.argmax(axis=1)
    
    error = 0
    for i in range(n_obs):
        choice_det = np.where(v[i,:] == v[i,:].max())
        error += choice[i] not in choice_det
    error /= n_obs
    print("Error rate:", error)
    
    X *= scale
    sample = {'X': X, 'choice': choice, 'n_obs': n_obs, 'n_alt': n_alt}
    return sample

def sample_alts(sample, l):
    #Sample alternatives
    if l == sample['n_alt']:
        X_mat = np.array(sample['X']).reshape(n_obs, -1)
        choice_new = np.array(sample['choice'])
    else:
        avail_bool_list = []
        choice_new = np.zeros((sample['n_obs'],), dtype='int64')
        for i in range(sample['n_obs']):
            avail_bool_i = np.zeros((sample['n_alt'],), dtype='bool')
            avail_bool_i[sample['choice'][i]] = True
            alt_ex_choice = np.array([j for j in range(n_alt) if j != 
                                      sample['choice'][i]])
            avail_alts = np.random.choice(alt_ex_choice, size=l-1, 
                                          replace=False)
            avail_bool_i[avail_alts] = True
            avail_bool_list.append(avail_bool_i)
            
            alts_selected = np.sort(np.append(avail_alts, sample['choice'][i]))
            choice_new[i] = np.nonzero(alts_selected==sample['choice'][i])[0]
            
        avail_bool = np.concatenate(avail_bool_list)
        X_mat = np.array(sample['X'][avail_bool]).reshape(n_obs, -1)
        
    #Make dataframe
    att_labels = sample['X'].columns.copy()
    X_labels = ['{}_j{}'.format(k,j+1) for j in range(l) for k in att_labels]
    df = pd.DataFrame(data=X_mat, columns=X_labels)
    df['choice'] = choice_new + 1
    
    return df, att_labels


###
#Experiment
###

t = 1 #int(os.getenv('TASK'))

np.random.seed(123+t)

n_rep = 1

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

L = [2, 5] #, 10, 20, 50, 100, 200]

est = [np.zeros((n_rep, 4, n_att)) for l in L]
time = np.zeros((n_rep, len(L)))

for r in range(n_rep):
    
    print("Sample {} of {}".format(r+1, n_rep))

    ###
    #Synthesise data
    ###
    
    sample = gen_data(n_obs, n_alt, beta, scale)
    
    for l_i, l in enumerate(L):

        ###
        #Estimate MNL with l alternatives
        ###
        
        #Sample alternatives
        df, att_labels = sample_alts(sample, l)
        
        #Availability
        avail_labels = ['av_j{}'.format(j+1) for j in range(l)]
        avail_bool = np.ones((n_obs, l))
        df_avail = pd.DataFrame(data=avail_bool, columns=avail_labels)
        df_sample = pd.concat((df, df_avail), axis=1)
        
        # Read the data
        database = db.Database('synthetic', df_sample)
        
        # The following statement allows you to use the names of the variable
        # as Python variable.
        globals().update(database.variables)
        
        # Parameters to be estimated
        B_labels = ['B_{}'.format(k) for k in att_labels]
        B = [Beta(b, 0, None, None, 0) for b in B_labels]
        
        # Definition of the utility functions
        def calc_V_j(X_j, B):
            V_j = 0
            for X_jk, B_k in zip(X_j, B):
                V_j += X_jk * B_k
            return V_j
                
        V = {j: calc_V_j([eval('{}_j{}'.format(k,j)) for k in att_labels], B) 
             for j in range(1,l+1)}
        
        # Associate the availability conditions with the alternatives
        av = {j: eval('av_j{}'.format(j)) for j in range(1,l+1)}
        
        # Definition of the model. This is the contribution of each
        # observation to the log likelihood function.
        logprob = models.loglogit(V, av, choice)
        
        # Create the Biogeme object
        biogeme = bio.BIOGEME(database, logprob)
        biogeme.modelName = 'mnl_l{}_t{}'.format(l,t)
        
        # Estimate the parameters
        results = biogeme.estimate()
        
        # Get the results in a pandas table
        pandasResults = results.getEstimatedParameters()
        #print(pandasResults)
        time[r,l_i] = biogeme.optimizationMessages['Optimization time']\
            .total_seconds()
    
        est[l_i][r,0,:] = np.array(pandasResults['Value'][B_labels])
        est[l_i][r,1,:] = np.array(pandasResults['Std err'][B_labels])
        est[l_i][r,2,:] = est[l_i][r,0,:] - 1.96 * est[l_i][r,1,:]
        est[l_i][r,3,:] = est[l_i][r,0,:] + 1.96 * est[l_i][r,1,:]

###
#Store results
###

results = {'est': est, 'time': time, 'B_labels': B_labels}

filename = 'results_soa_{}'.format(t)
outfile = open(filename, 'wb')
pickle.dump(results, outfile)
outfile.close()
