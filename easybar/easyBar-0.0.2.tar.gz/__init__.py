import sys


def easyBar(curr, total, barLength=15, end='\r', flush=True, sep=' ', file=sys.stdout, *args, **kwargs):
    print(f'''[{''.join(['=']*round(curr/total*barLength))}{''.join([' '])*round((1-(curr/total))*barLength)}] 进度：{format(curr/total, '.2f')}%''',
          end=end, flush=flush, sep=sep, file=file, *args, **kwargs)
