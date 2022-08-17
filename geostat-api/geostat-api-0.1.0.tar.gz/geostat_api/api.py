import os

def run(prod=False, base_url: str = None):
    if prod:
        if base_url is None:
            base_url = 'http://localhost:8000/'
        os.environ['PYGEOAPI_BASE_URL'] = base_url
        os.system('gunicorn -b 127.0.0.1:8000 pygeoapi.flask_app:APP')
    else:
        os.system('pygeoapi serve')




if __name__ == '__main__':
    import fire
    fire.Fire(run)
