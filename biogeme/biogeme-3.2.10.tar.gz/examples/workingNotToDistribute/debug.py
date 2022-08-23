import biogeme.biogeme as bio
import biogeme.database as db
import pandas as pd
import numpy as np
from biogeme.expressions import Beta, Variable, exp
import biogeme.messaging as msg
logger = msg.bioMessage()
logger.setDetailed()

df = pd.DataFrame({'Person':[1,1,1,2,2],
                   'Exclude':[0,0,1,0,1],
                   'Variable1':[1,2,3,4,5],
                   'Variable2':[10,20,30,40,50],
                   'Choice':[1,2,3,1,2],
                   'Av1':[0,1,1,1,1],
                   'Av2':[1,1,1,1,1],
                   'Av3':[0,1,1,1,1]})
myData = db.Database('test', df)


Variable1=Variable('Variable1')
Variable2=Variable('Variable2')
beta1 = Beta('beta1', -1.0, -3, 3, 0)
beta2 = Beta('beta2', 2.0, -3, 10, 0)
likelihood = -beta1**2 * Variable1 - exp(beta2 * beta1) \
    * Variable2 - beta2**4
simul = beta1 / Variable1 + beta2 / Variable2
dictOfExpressions = {'loglike': likelihood, 
                     'beta1': beta1,
                     'simul': simul}

myBiogeme = bio.BIOGEME(myData, dictOfExpressions)
myBiogeme.modelName = 'simpleExample'
results = myBiogeme.estimate(bootstrap=10)

print('******* HERE: SIMULATE *******')
simulationWithDefaultBetas = myBiogeme.simulate()
print(simulationWithDefaultBetas)

print('******* HERE: VALIDATE *******')

validationData = myData.split(slices=5)
validation_results = myBiogeme.validate(results, validationData)
