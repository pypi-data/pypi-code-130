import requests, time


def down(url, format, m='none'):
    try:
        r = requests.get(f'https://loader.to/ajax/download.php?format={format}&url={url}').json()
        id = r['id']
        while True:
            get_download = requests.get(f'https://loader.to/ajax/progress.php?id={id}').json()
            download_url = get_download['download_url']
            if 'https' in str(download_url):
                return download_url
            else:
                if m == 'none':
                    pass
                else:
                    print(m)
                    time.sleep(1.5)
    except:
        return 'Error while downloading!'


def f():
    return ['360','480','720','1080','4k','8k','mp3','ogg','wav','webm_audio','m4a','aac','flac','opus']