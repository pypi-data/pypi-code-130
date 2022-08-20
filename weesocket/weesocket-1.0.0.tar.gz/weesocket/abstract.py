from threading import Lock
try:
	from orjson import loads, dumps
except ModuleNotFoundError:
	try:
		from ujson import loads, dumps  # type: ignore
	except ModuleNotFoundError:
		from json import loads, dumps  # type: ignore
from rsa import newkeys, encrypt, decrypt
from logging import getLogger
from base64 import b64encode, b64decode
from hmac import new
from hashlib import sha256

logger = getLogger("socket")


class Socket:
	def __init__(
		self, trigger=None, file=None, host="0.0.0.0", port=6666,
		secrets=None, server_secret=None
	):
		if trigger:
			self._trigger = trigger
		self._file = file
		self._host = host
		self._port = port
		self._lock = Lock()
		self.__counter = 1
		self._secrets = None
		self._server_secret = None
		self._key = None
		self._publickey = None
		self._remotekey = None
		if secrets:
			self._secrets = secrets
			self._server_secret = server_secret
			key = newkeys(2048)
			self._key = key[1]
			self._publickey = key[0].save_pkcs1()
		self.start()

	def start(self):
		pass

	@staticmethod
	def _process_stream(bytes, private_key=False):
		data = bytes
		data_array = []
		while data:
			parts = data.split(b"|")
			if len(parts) < 3:
				return data_array, data
			length = int(parts[1])
			header = len(parts[1]) + 2
			if header + length > len(data):
				return data_array, data
			data_array.append(data[header: header + length])
			data = data[header + length:]
		return data_array, data

	def _process_data(self, data, connection, secrets):
		if secrets:
			skip = True
			sign = data.pop("signature", False)
			for secret in secrets:
				if sign == Socket.sign(data, secret):
					skip = False
					break
			if skip:
				return
		if data.get("socket-action"):
			self._socket_trigger(data, connection)
		elif self._trigger:
			self._trigger(data)

	def _socket_trigger(self, data, connection):
		pass

	@staticmethod
	def sign(data, secret):
		if type(data) != str and type(data) != bytes:
			data = dumps(data)
		if type(data) != bytes:
			data = data.encode()
		return new(secret.encode(), data, sha256).hexdigest()

	@staticmethod
	def _prepare_data(
		data, sender, target=None, target_id=None, key=None,
		socket_action=None, alias="", secret=None
	):
		if type(data) != dict:
			data = {"data": data}
		if not data.get("sender"):
			data["sender"] = sender
		data["target"] = target
		data["target_id"] = target_id
		data["alias"] = alias
		if socket_action:
			data["socket-action"] = socket_action
		if secret:
			data["signature"] = Socket.sign(data, secret)
		data = dumps(data)
		if key:
			chunks = []
			seek = 0
			size = 245
			enc = data if type(data) == bytes else data.encode()
			while enc[seek:seek + size]:
				chunks.append(
					b64encode(encrypt(enc, key)).decode()
				)
				seek += size
			data = dumps(chunks)
		return data

	@staticmethod
	def _load_data(data, key=None, only_json=True):
		if key:
			try:
				encrypted = loads(data)
			except Exception:
				pass
			if type(encrypted) == list:
				buffer = b""
				for d in encrypted:
					buffer += decrypt(b64decode(d), key)
				data = buffer
		if type(data) == bytes:
			data = data.decode()
		try:
			data = loads(data)
		except Exception:
			if only_json:
				return
		return data

	@staticmethod
	def _send_data(connection, data):
		if type(data) != bytes:
			data = data.encode()
		try:
			data = b"|%d|%s" % (len(data), data)
			connection.send(data)
		except Exception:
			return False
		return True

	def get_name(self):
		return self._name
