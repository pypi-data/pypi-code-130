# -*- coding: utf-8 -*-
from poinc.job2poinc import send_job, read_result, get_result_from_hash

def func(x):
    # takes only one argument
    return x * x


for arg in [10]:
    code_hash, arg_hash = send_job(func, arg)

# watch ftp server and get the result
ret = read_result(func, arg)
# ret = get_result_from_hash(code_hash, arg_hash)

