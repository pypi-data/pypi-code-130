# Limited HTTP server for REST services

import socket
import http.client
from rutifu import *

class HttpRequest(object):
    def __init__(self, client, addr, method, path, query, protocol, headers, data):
        self.client = client
        self.addr = addr
        self.method = method
        self.path = path
        self.query = query
        self.protocol = protocol
        self.headers = headers
        self.data = data

class HttpResponse(object):
    def __init__(self, client, protocol, status=200, headers={}, data=None):
        self.client = client
        self.protocol = protocol
        self.status = status
        self.headers = headers
        self.data = data

class HttpServer(object):
    def __init__(self, name, port, handler=None, args=(), start=False):
        self.name = name
        self.port = port
        self.handler = handler
        self.args = args
        self.socket = None
        if start:
            self.start()

    def start(self):
        debug("debugHttpServer", self.name, "starting")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(("", self.port))
        debug("debugHttpServer", "opened socket on port", self.port)
        self.socket.listen(1)
        startThread(self.name, self.getRequests)

    # read and parse HTTP requests
    def getRequests(self):
        debug("debugHttpServer", "waiting for request")
        while True:
            (client, addr) = self.socket.accept()
            debug("debugHttpServer", "request from", addr)
            clientFile = client.makefile()
            # start a new request
            line = clientFile.readline()
            (method, uri, protocol) = (line.strip("\n").split(" ")+3*[""])[0:3]
            debug("debugHttpServer", "method:", method)
            debug("debugHttpServer", "uri:", uri)
            debug("debugHttpServer", "protocol:", protocol)
            # parse the path string into components
            try:
                (pathStr, queryStr) = uri.split("?")
                query = dict([queryItem.split("=") for queryItem in queryStr.split("&")])
            except ValueError:
                pathStr = uri
                query = {}
            path = pathStr.lstrip("/").rstrip("/").split("/")
            debug("debugHttpServer", "path:", path)
            debug("debugHttpServer", "query:", query)
            # read the headers
            headers = {}
            (headerName, headerValue) = (clientFile.readline().strip("\n").split(":")+2*[""])[0:2]
            while headerName != "":
                headers[headerName.strip()] = headerValue.strip()
                (headerName, headerValue) = (clientFile.readline().strip("\n").split(":")+2*[""])[0:2]
            debug("debugHttpServer", "headers:", headers)
            # read the data
            try:
                data = clientFile.read(int(headers["Content-Length"]))
            except KeyError:
                data = None
            # send it to the handler
            clientFile.close()
            try:
                self.handler(HttpRequest(client, addr, method.upper(), path, query, protocol, headers, data),
                             HttpResponse(client, protocol), *self.args)
            except Exception as ex:
                self.sendResponse(HttpResponse(client, protocol, 500, {}, str(ex)+"\n"))

    # send an HTTP response
    def sendResponse(self, response):
        debug("debugHttpServer", "protocol:", response.protocol)
        debug("debugHttpServer", "status:", response.status)
        debug("debugHttpServer", "headers:", response.headers)
        response.client.send(bytes(response.protocol+" "+str(response.status)+" "+http.client.responses[response.status]+"\n", "utf-8"))
        for header in response.headers:
            response.client.send(bytes(header+": "+str(response.headers[header])+"\n", "utf-8"))
        if response.data:
            response.client.send(bytes("Content-Length: "+str(len(response.data))+"\n\n", "utf-8"))
            response.client.send(bytes(response.data, "utf-8"))
        response.client.close()
