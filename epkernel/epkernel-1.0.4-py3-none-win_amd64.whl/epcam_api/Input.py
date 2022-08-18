import os, sys, json
from epcam_api import BASE

#打开料号
def open_job(job, path):
    try:
       ret= json.loads(BASE.open_job(path, job))['paras']['status']
       return ret   
    except Exception as e:
        print(e)
        return False


def open_eps(job, path):
    try:
        path = path +'\\'+str(job)+'.eps'
        BASE.open_eps(job, path)
    except Exception as e:
        print(e)
