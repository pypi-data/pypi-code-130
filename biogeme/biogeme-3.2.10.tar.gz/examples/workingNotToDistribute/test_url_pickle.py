import pickle
import urllib.request as urlr
import urllib.error as urle
#from urllib.request import urlopen
import biogeme.results as res


pickle_file = 'https://courses.edx.org/asset-v1:EPFLx+ChoiceModels2x+3T2021+type@asset+block@02asv.pickle'

#pickle_file = 'https://courses.edx.org/asset-v1:EPFLx+ChoiceModels2x+3T2021+type@asset+block@0asv.pickle'


try:
    with urlr.urlopen(pickle_file) as p:
        data = pickle.load(p)
except urle.HTTPError:
    pass
try:
    with open(pickle_file, 'rb') as p:
        data = pickle.load(p)
except FileNotFoundError:
    print('FILE NOT FOUND')
    
results = res.bioResults(data)
print(results.printGeneralStatistics())
        
