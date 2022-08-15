from hhlpy.gui.server import *
import webbrowser
from threading import Timer

port = 8000

def open_browser():
      webbrowser.open_new('http://127.0.0.1:{0}/'.format(port))

if __name__ == "__main__":
    websocketServer = WebSocketServer(
        ('', port),
        Resource(OrderedDict([('/', HHLPyApplication)]))
    )
    try:
        computationProcess = startComputationProcess()
        startHttpProcess(port)
        Timer(3, open_browser).start();
        print("Running websocket server on ws://localhost:{0}".format(port), flush=True)
        websocketServer.start()
        while True:
            checkComputationProcess() # Check whether there are new computation results
            gevent.sleep(0) # Pause to allow the server to handle new requests from the client
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        print("Closing python websocket server")
        websocketServer.stop()
