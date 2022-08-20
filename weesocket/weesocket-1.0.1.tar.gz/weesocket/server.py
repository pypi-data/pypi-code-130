from os import remove
from socket import (
	socket, AF_UNIX, AF_INET, SOCK_STREAM,
	SOL_SOCKET, SO_REUSEADDR, SHUT_RDWR
)
from threading import Thread
from rsa import PublicKey
from .abstract import Socket, logger


class Server(Socket):
	def __init__(
		self, trigger=None, name="server", file=None,
		host="0.0.0.0", port=6666, secrets=None, server_secret=None, proxy=False
	):
		self._counter = 0
		self._name = name
		self._connections = {}
		self.__proxy = proxy
		self.__aliases = {}
		self.__enabled = False
		self._remotekey = False
		super().__init__(trigger=trigger, file=file, host=host, port=port, secrets=secrets, server_secret=server_secret)

	def start(self):
		if self.__enabled:
			return
		self.__enabled = True
		if self._file:
			self._socket = socket(AF_UNIX, SOCK_STREAM)
			try:
				remove(self._file)
			except OSError:
				pass
			self._socket.bind(self._file)
		else:
			self._socket = socket(AF_INET, SOCK_STREAM)
			self._socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
			try:
				self._socket.bind((self._host, self._port))
			except Exception as e:
				logger.error("Bind error", e)
		self._socket.listen(1)
		t = Thread(target=self.__listen, args=())
		t.daemon = True
		t.start()

	def stop(self):
		if not self.__enabled:
			return
		self.__enabled = False
		self._lock.acquire()
		connections = self._connections.copy()
		for connection in connections:
			connections[connection]["connection"].close()
			if self._connections.get(connection):
				self._connections.pop(connection)
		self.__aliases = {}
		self._lock.release()
		if not self._file:
			self._socket.shutdown(SHUT_RDWR)
		self._socket.close()
		if self._file:
			remove(self._file)

	def send(self, data, target=None, target_id=None, skip=None):
		self._lock.acquire()
		if target_id:
			c = self._connections.get(target_id)
			if c:
				Socket._send_data(c["connection"], Socket._prepare_data(
						data, self._name, target, target_id, c["key"], secret=self._server_secret
				))
		elif target:
			for c in self.__aliases.get(target, []):
				Socket._send_data(c["connection"], Socket._prepare_data(
					data, self._name, target, target_id, c["key"], secret=self._server_secret
				))
		else:
			for c in self._connections.values():
				if c["connection"] != skip:
					Socket._send_data(c["connection"], Socket._prepare_data(
						data, self._name, target, target_id, c["key"], secret=self._server_secret
					))
		self._lock.release()

	def __listen(self):
		while self.__enabled:
			try:
				conn, addr = self._socket.accept()
			except Exception:
				break
			t = Thread(target=self.__on_connection, args=(conn, addr))
			t.daemon = True
			t.start()

	def __on_connection(self, connection, address):
		self._counter += 1
		name = "client_%d" % self._counter
		if self._secrets:
			Socket._send_data(
				connection,
				Socket._prepare_data(
					{"name": name, "key": self._publickey.decode()}, self._name,
					socket_action="prepare", secret=self._server_secret
				)
			)
		else:
			Socket._send_data(connection, Socket._prepare_data(
				{"name": name}, self._name, socket_action="prepare", secret=self._server_secret
			))
		obj = {"connection": connection, "key": False}
		data = None
		bytes = b""
		while self.__enabled:
			try:
				bytes += connection.recv(1024)
			except Exception as e:
				logger.warning("Socket expired", connection, e)
				break
			if not bytes:
				break
			data, bytes = Socket._process_stream(bytes)
			for item in data:
				json = Socket._load_data(item, self._key)
				if name not in self._connections:
					self._connections[name] = obj
				if self.__proxy and (json["target"] != self._name or json["target_id"]) and not json.get("socket-action"):
					if json["target"] == "*":
						json["target"] = None
						self._process_data(json, connection, self._secrets)
					self.send(json, target=json["target"], target_id=json["target_id"], skip=connection)
				else:
					self._process_data(json, connection, self._secrets)
		connection.close()
		self._lock.acquire()
		self._clear(self._connections.copy(), connection)

	def _clear(self, connections, connection):
		for key in connections:
			if self._connections[key] == connection:
				del self._connections[key]
		for alias in self.__aliases:
			values = len(self.__aliases[alias])
			for i in range(values):
				if self.__aliases[alias][i]["connection"] == connection:
					self.__aliases[alias][i] = None
			try:
				self.__aliases[alias].remove(None)
			except Exception:
				pass
		self._lock.release()

	def _socket_trigger(self, data, connection):
		actions = {
			"auth": self._auth,
			"set-alias": self._set_alias,
			"disconnect": self._disconnect_client
		}
		action = actions.get(data["socket-action"])
		if action:
			action(data, connection)

	def _disconnect_client(self, data, connection):
		connections = self._connections.copy()
		for connection in connections:
			if connection == data["sender"]:
				connections[connection]["connection"].close()
				if self._connections.get(connection):
					self._connections.pop(connection)

	def _auth(self, data, connection):
		self._connections[data["sender"]]["key"] = PublicKey.load_pkcs1(data["key"])

	def _set_alias(self, data, connection):
		for c in self._connections.values():
			if c["connection"] == connection:
				if not data["set-alias"] in self.__aliases:
					self.__aliases[data["set-alias"]] = [c]
				else:
					self.__aliases[data["set-alias"]].append(c)

	def get_aliases(self):
		return self.__aliases
