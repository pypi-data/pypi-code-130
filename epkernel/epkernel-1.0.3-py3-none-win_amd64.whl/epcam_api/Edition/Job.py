import os, sys, json
from epcam_api import BASE

def delete_job(job):
    try:
        BASE.job_delete(job)
    except Exception as e:
        print(e)