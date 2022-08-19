import json
from redisgears import log

dimensions = ['W', 'S', 'P']
for dimension in dimensions:
    GB("StreamReader"). \
        foreach(lambda record: log(f'sandbox-{dimension}-{record}')). \
        register(
        prefix=f'ST:1MINUTE:{dimension}:::PG',
        convertToStr=True,
        collect=True,
        onFailedPolicy='abort',
        onFailedRetryInterval=1,
        batch=1,
        duration=0,
        trimStream=False)

# run('ST:1MINUTE::::PG', trimStream=False)

# desc_json_w = {"name": 'W'}
# GB("StreamReader", desc=json.dumps(desc_json_w)). \
#     filter(lambda record: record['value']['dimension'] == 'W'). \
#     foreach(lambda record: log(f'sandbox-w-{record}')). \
#     register(
#     prefix='ST:1MINUTE::::PG',
#     convertToStr=True,
#     collect=True,
#     onFailedPolicy='abort',
#     onFailedRetryInterval=1,
#     batch=1,
#     duration=0,
#     trimStream=False)
# log(f'Register W OK')

# desc_json_s = {"name": 'S'}
# GB("StreamReader", desc=json.dumps(desc_json_s)). \
#     filter(lambda record: record['value']['dimension'] == 'S'). \
#     foreach(lambda record: log(f'sandbox-s-{record}')). \
#     register(
#     prefix='ST:1MINUTE::::PG',
#     convertToStr=True,
#     collect=True,
#     onFailedPolicy='abort',
#     onFailedRetryInterval=1,
#     batch=1,
#     duration=0,
#     trimStream=False)
# log(f'Register S OK')

# desc_json_p = {"name": 'P'}
# GB("StreamReader", desc=json.dumps(desc_json_p)). \
#     filter(lambda record: record['value']['dimension'] == 'P'). \
#     foreach(lambda record: log(f'sandbox-p-{record}')). \
#     register(
#     prefix='ST:1MINUTE::::PG',
#     convertToStr=True,
#     collect=True,
#     onFailedPolicy='abort',
#     onFailedRetryInterval=1,
#     batch=1,
#     duration=0,
#     trimStream=False)
# log(f'Register P OK')