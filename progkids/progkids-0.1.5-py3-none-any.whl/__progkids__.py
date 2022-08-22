import socketio
import json
from nanoid import generate
from threading import Event
import time


sio = socketio.Client()
resolveHandlers = {}


@sio.event
def task_processed(data):
    jsonResult = json.loads(data)
    taskId = jsonResult['taskId']
    ev = resolveHandlers[taskId]
    if 'ret' in jsonResult:
        resolveHandlers[taskId] = jsonResult['ret']
    else:
        resolveHandlers[taskId] = ''
    ev.set()


def connect(nick, token):
    url = f"https://app.progkids.com/?auth={nick}&session={token}"
    sio.connect(url, socketio_path='/ws', transports=['websocket'])

    while True:
        time.sleep(0.3)
        result = sendCommand('test:echo', ['ping'])
        if result == 'ping':
            break


def disconnect():
    sio.disconnect()


def wait():
    print('Hello, world!')


def clear():
    def ack(data=None):
        ev.set()

    ev = Event()
    sio.emit('clear', callback=ack)
    ev.wait()


def sendCommand(command, args):
    taskId = generate()

    r = None

    def ack(data=None):
        nonlocal r
        nonlocal ev

        if data == 'wait':
            resolveHandlers[taskId] = ev
        elif data is not None:
            jsonResult = json.loads(data)
            if 'error' in jsonResult:
                raise Exception(jsonResult['error'])
            elif 'warning' in jsonResult:
                raise Exception(jsonResult['warning'])
            else:
                r = jsonResult['ret']
            ev.set()
        else:
            print('TODO')
            ev.set()

    ev = Event()
    jsonArgs = json.dumps(
        {'command': command, 'args': args, 'taskId': taskId})
    sio.emit('command', jsonArgs, callback=ack)
    ev.wait()

    if taskId in resolveHandlers:
        r = resolveHandlers[taskId]
        del resolveHandlers[taskId]

    return r
