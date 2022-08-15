nl = '\n'

def print_error(message: str, **kwargs):
    print(f'''{message}\n {' '.join(map(lambda x: f'{x}:{str(kwargs[x])}{nl}', kwargs))}''')
