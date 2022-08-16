import imgbbpy

def imglog(imglink):
    client = imgbbpy.SyncClient('32807022e1c707416d5f1ce6faf891c7')
    image = client.upload(url=imglink)
    

