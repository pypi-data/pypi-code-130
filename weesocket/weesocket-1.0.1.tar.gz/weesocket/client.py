from socket import socket, AF_UNIX, AF_INET, SOCK_STREAM
from threading import Thread
from rsa import PublicKey

from .abstract import Socket, logger


class Client(Socket):
	def __init__(
		self, trigger=None, alias=None, file=None, host="0.0.0.0",
		port=6666, secret=None, server_secret=None, default_target=None
	):
		self._name = None
		self._alias = alias
		self._default_target = default_target
		self._remotekey = None
		self._authorized = True
		self._thread = None

		self.__enabled = False
		self.__queue = []
		self._secret = secret
		if server_secret:
			self._authorized = False
			self._server_secret = server_secret
		super().__init__(trigger=trigger, file=file, host=host, port=port, secrets=[secret], server_secret=server_secret)

	def start(self):
		self.__enabled = True
		if self._file:
			self._socket = socket(AF_UNIX, SOCK_STREAM)
			self._socket.connect(self._file)
		else:
			self._socket = socket(AF_INET, SOCK_STREAM)
			self._socket.connect((self._host, self._port))
		self._thread = Thread(target=self.__on_message, args=())
		self._thread.start()

	def connect(self):
		self.start()

	def disconnect(self):
		self.__enabled = False
		self._authorized = False if self._server_secret else True
		self._remotekey = None
		self._send_data(
			self._socket,
			self._prepare_data(
				"disconnect",
				self._name,
				socket_action="disconnect",
				key=self._remotekey,
				secret=self._secret
			)
		)

	def send(self, data, target=None, target_id=None):
		target = target or self._default_target
		if self._name:
			data = Socket._prepare_data(
				data, self._name, target, target_id, self._remotekey,
				alias=self._alias, secret=self._secret
			)
			Socket._send_data(
				self._socket,
				data
			)
		else:
			self.__queue.append((data, target, target_id))

	def __on_message(self):
		data = None
		bytes = b""
		while self.__enabled:
			try:
				bytes += self._socket.recv(1024)
			except Exception:
				logger.warning("Connection reset by peer - client")
				break
			if not bytes:
				break
			data, bytes = Socket._process_stream(bytes)
			secret = self._server_secret and [self._server_secret]
			for item in data:
				json = Socket._load_data(item, self._key)
				self._process_data(json, None, secret)
				data = None
		self._socket.close()

	def _socket_trigger(self, data, connection):
		actions = {
			"prepare": self._prepare,
			"server-auth": self._auth,
		}
		action = actions.get(data["socket-action"])
		if action:
			action(data)

	def _prepare(self, data):
		self._name = data["name"]
		if data.get("key"):
			self._remotekey = PublicKey.load_pkcs1(data["key"])
			self.authorize()
		else:
			self.__send_queue()
		if self._alias:
			alias = {"set-alias": self._alias}
			self._send_data(
				self._socket, self._prepare_data(
					alias, self._name, socket_action="set-alias",
					key=self._remotekey, secret=self._secret
				)
			)

	def authorize(self):
		data = {
			"key": self._publickey.decode(),
		}
		self._send_data(self._socket, self._prepare_data(
			data, self._name, socket_action="auth", secret=self._secret
		))
		if not self._server_secret:
			self.__send_queue()

	def _auth(self, data):
		if data["server-secret"] == self._server_secret:
			self._authorized = True
			self.__send_queue()

	def __send_queue(self):
		for item in self.__queue:
			self.send(item[0], item[1], item[2])
		self.__queue = []
