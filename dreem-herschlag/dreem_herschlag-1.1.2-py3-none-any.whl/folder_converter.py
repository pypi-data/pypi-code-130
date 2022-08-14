
import pickle
import os 
path = '/Users/ymdt/src/dreem_herschlag/data/'
my_list = os.listdir(path)
for s in my_list:
    try:        
        p = pickle.load(open(path+s+'/mutation_histos.p', 'rb'))
        pickle.dump(p, open(path+s+'.p', 'wb'))
    except:
        print(s)
        pass