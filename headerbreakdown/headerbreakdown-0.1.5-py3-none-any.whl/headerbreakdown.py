#!/usr/bin/python3

#
#
#
# converts a collection of HTTP headers into a dictionary structure for automated analysis; creates parsed and analyzed objects; accepts strings, lists, or dictionaries of header values
#
#
#

"""
#
# Example Usage
#
from headerbreakdown import HeaderBreakdown as hb
import json
# header with multiple Host and User-Agent values
someheader = "GET /?gws_rd=ssl HTTP/1.1\r\nHost: www.google.com\r\nHost: www.bing.com\r\nHost: www.yahoo.com\r\nConnection: keep-alive\r\nAccept-Encoding: gzip, deflate\r\nAccept: */*\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/99.0\r\nCookie: 1P_JAR=2021-03-13-04"
# create the object
h = hb(someheader)
# print only the parsed version of the header
print(h.parsed)
# print the analyzed version with subvalues, minivalues, and microkeys and microvalues
print(h.analyzed)
# print as json
print(json.dumps(h.analyzed, indent=4))
"""

import copy
import json

#============================================================================

class HeaderBreakdown:
	#============================================================================
	# initialize
	#============================================================================
	def __init__(self, harg):
		""" initialize the header argument _harg and run all setters """
		self._harg = harg
		# send to call_setters, which calls set_* methods (get_* methods called at the bottom)
		self.call_setters(self._harg)

	#============================================================================
	# processing methods
	#============================================================================
	def string_to_dict(self, s) -> dict:
		""" convert a single header string "h: v" format to a dict {str(k):list(v)} """
		d = {}
		# process colon-delimited headers
		if ":" in s:
			hs = s.split(":")
			d = {hs[0].strip():[":".join(hs[1:]).strip()]}
		else:
			# process the first request or response header line which typically does not include a colon (BUT NOT ALWAYS)
			if "HTTP/" in s:
				x = s.split()
				if len(x) == 3:
					if "HTTP/" in x[0]:
						if not hasattr(self, "_direction"):
							self._direction = "response"
							d["_direction"] = "response"
						if not hasattr(self, "_httpversion"):
							self._httpversion = x[0]
							d["_httpversion"] = x[0]
						if not hasattr(self, "_responsecode"):
							self._responsecode = x[1]
							d["_responsecode"] = x[1]
						if not hasattr(self, "_responsephrase"):
							self._responsephrase = " ".join(x[2:]).strip()
							d["_responsephrase"] = " ".join(x[2:]).strip()
					elif "HTTP/" in x[2]:
						if not hasattr(self, "_direction"):
							self._direction = "request"
							d["_direction"] = "request"
						self.dgen(d, "method", x[0])
						self.dgen(d, "path", x[1])
						if not hasattr(self, "_httpversion"):
							self._httpversion = x[2]
							d["_httpversion"] = x[2]
		return(d)

	# input cleanup/standardization method
	def multistring_to_dict(self, s) -> dict:
		""" convert a string of headers that include \r\n between them into a dict {str(k):list(v)} """
		ss = s.split("\r\n")
		sss = [i.strip() for i in ss if len(i) > 0] # remove any blanks if there are leading or terminating \r\n
		hout = self.list_to_dict(sss)
		return(hout)

	# input cleanup/standardization method
	def list_to_dict(self, l) -> dict:
		""" convert a list of header strings ["h: v",...] to a dict {str(k):list(set(v))} """
		d = {}
		for item in l:
			id = self.string_to_dict(item) # now a dict
			for k,v in id.items():
				if k not in d.keys():
					d.setdefault(k,[])
					d[k].extend(v)
				else:
					d[k].extend(v)
		# make value lists into unique sets (ultimately remain a list)
		for key,val in d.items():
			# ignore metadata keys
			if not key.startswith("_"):
				d[key] = list(set(d[key]))
			else:
				d[key] = "".join(d[key])
		return(d)

	# input cleanup/standardization method
	def dict_to_dict(self, d) -> dict:
		""" convert values that are strings into lists """
		for k,v in d.items():
			if isinstance(v, str):
				d[k] = [d[k].strip()]
		return(d)

	# TODO: dict to list, and list to list(set())

	def post_process_header_object(self, z) -> dict:
		""" convert the values to dicts """
		d = {}
		for k,v in z.items():
			# ignore metadata keys
			if not k.startswith("_"):
				k_normalized = k.lower().replace("-","").replace("_","").strip()
				d[k_normalized] = {"key":k}
				for x in v:
					d[k_normalized]["value"] = v
			else:
				d[k] = v
		return(d)

	def dgen(self, d, k, v) -> dict:
		""" nested dictionary builder """
		if k not in d.keys():
			d.setdefault(k,[])
			d[k].append(v)
		elif k in d.keys():
			d[k].append(v)

	def identify_sub_values(self, v) -> dict:
		""" identify sub key/value pairs, using a semicolon OR comma if semicolon is not present, inside a header value """
		d = {}
		# semicolon, or comma without semicolon, determines subvalues
		if ";" in v:
			z = list(set([i.strip().replace("'","").replace('"','') for i in v.split(";")]))
			d["subvalues"] = z
		elif "," in v and ";" not in v:
			z = list(set([i.strip().replace("'","").replace('"','') for i in v.split(",")]))
			d["subvalues"] = z
		return(d)

	def identify_mini_values(self, v) -> list:
		""" identify mini key/value pairs, using a comma, inside a header value """
		z = []
		if "," in v:
			z = list(set([i.strip().replace("'","").replace('"','') for i in v.split(",")]))
		return(z)

	def identify_micro_values(self, v) -> dict:
		""" identify micro key/value pairs, using an equal sign, inside a header value """
		d = {}
		if "=" in v:
			z = [i.strip().replace("'","").replace('"','') for i in v.split("=")]
			d["microkey"] = z[0]
			d["microvalue"] = z[1]
		return(d)

	def process_dispatcher(self, d) -> dict:
		""" dispatch sub/micro/mini value logic """
		# d is the parsed dict-of-dicts
		for k,v in d.items():
			# v is a dict, with keys named "key" and "value" OR v is a string value
			if isinstance(v, dict):
				for val in v["value"]:
					# val is the raw header value, to be inspected for sub/micro/mini components
					# subvalue detection
					subs = self.identify_sub_values(val)
					if len(subs) > 0:
						d[k]["subvalues"] = subs["subvalues"]
						for sub in subs["subvalues"]:
							# minivalue detection
							minis = self.identify_mini_values(sub)
							if len(minis) > 0:
								self.dgen(d[k], "minivalues", minis)
							# microvalue detection
							mics = self.identify_micro_values(sub)
							if len(mics) > 0:
								self.dgen(d[k], "microvalues", mics)
		return(d)

	def post_process_keys_to_metadata(self, d) -> dict:
		""" add "_keys" metadata field to final object """
		if "_keys" not in d:
			d["_keys"] = []
		for k,v in d.items():
			if not k.startswith("_"):
				# use normalized keys
				d["_keys"].append(k)
				if k == "host":
					self._host = v["value"]
				elif k == "method":
					self._method = v["value"]
				elif k == "path":
					self._path = v["value"]
		return(d)

	#============================================================================
	# getters and setters
	#============================================================================
	def get_direction(self):
		return(self._direction)

	def get_httpversion(self):
		return(self._httpversion)

	def get_responsecode(self):
		return(self._responsecode)

	def get_responsephrase(self):
		return(self._responsephrase)

	def get_method(self):
		return(self._method)

	def get_host(self):
		return(self._host)

	def get_path(self):
		return(self._path)

	def get_header_object(self):
		return(self._header_object)

	def set_header_object(self, z):
		""" call processing methods to create _header_object """
		if isinstance(z, str):
			if "\r\n" in z:
				hout = self.multistring_to_dict(z.strip())
			else:
				hout = self.string_to_dict(z.strip())
		elif isinstance(z, list):
			hout = self.list_to_dict(z)
		elif isinstance(z, dict):
			hout = self.dict_to_dict(z)
		else:
			hout = z
		h = self.post_process_header_object(hout)
		self._header_object = h

	def get_header_result(self):
		""" getter for prepped result output """
		return(self._header_result)

	def set_header_results(self, z):
		""" call processing methods to create _header_result """
		z = self.process_dispatcher(z)
		self._header_result = z

	#============================================================================
	# begin processing actions by calling setters
	#============================================================================
	def call_setters(self, x):
		""" call setters and post-processing """
		# main dispatch based on the provided data type
		self.set_header_object(x)
		# deepcopy to avoid altering the same object in memory, to produce both "parsed" and "analyzed" outputs
		z = copy.deepcopy(self._header_object)
		zz = self.post_process_keys_to_metadata(z)
		self.set_header_results(zz)

	#============================================================================
	# attributes
	#============================================================================
	#header_object = property(get_header_object)
	parsed = property(get_header_object)
	direction = property(get_direction)
	httpversion = property(get_httpversion)
	responsecode = property(get_responsecode)
	responsephrase = property(get_responsephrase)
	method = property(get_method)
	host = property(get_host)
	path = property(get_path)
	#header_result = property(get_header_result)
	analyzed = property(get_header_result)

	#============================================================================
	def __repr__(self):
		""" returns the provided argument during initialization (_hdict) """
		return(f"{self._harg}")

#============================================================================

'''
def unit_tests():
	""" unit tests """
	# sample data
	# header with multiple Host, and User-Agent values
	#H1 = "GET /?gws_rd=ssl HTTP/1.1\r\nHost: www.google.com\r\nHost: www.bing.com\r\nHost: www.yahoo.com\r\nConnection: keep-alive\r\nAccept-Encoding: gzip, deflate\r\nAccept: */*\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/99.0\r\nCookie: 1P_JAR=2021-03-13-04"
	# header with multiple Host, Method/Path, and User-Agent values
	H1 = "GET /?gws_rd=ssl HTTP/1.1\r\nDELETE /AAAA HTTP/1.1\r\nHost: www.google.com\r\nHost: www.bing.com\r\nHost: www.yahoo.com\r\nConnection: keep-alive\r\nAccept-Encoding: gzip, deflate\r\nAccept: */*\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/99.0\r\nCookie: 1P_JAR=2021-03-13-04"
	# single header as a plain string (with no \r\n)
	# note the nested_direction_* attributes will be type None with this sort of direction-ambiguous header
	H2 = "Set-Cookie: k1=v1;k2=v2"
	# normal header examples that terminate with \r\n\r\n
	H3 = "HTTP/1.1 302 Found\r\nLocation: https://www.google.com/?gws_rd=ssl\r\nCache-Control: private\r\nContent-Type: text/html; charset=UTF-8\r\nDate: Sat, 13 Mar 2021 04:15:44 GMT\r\nServer: gws\r\nContent-Length: 231\r\nX-XSS-Protection: 0\r\nX-Frame-Options: SAMEORIGIN\r\nSet-Cookie: 1P_JAR=2021-03-13-04; expires=Mon, 12-Apr-2021 04:15:44 GMT; path=/; domain=.google.com; Secure; SameSite=none\r\n\r\n"
	H4 = "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nSet-Cookie: k1=v1;k2=v2\r\n\r\n"
	H5 = "GET / HTTP/1.1\r\nHost: google.com\r\nUser-Agent: BLAHBLAH\r\nAccept: text/plain\r\n\r\n"
	H6 = ["GET / HTTP/1.1", "Host: google.com", "User-Agent: BLAHBLAH", "Accept: text/plain"]
	h1 = HeaderBreakdown(H1)
	h2 = HeaderBreakdown(H2)
	h3 = HeaderBreakdown(H3)
	h4 = HeaderBreakdown(H4)
	h5 = HeaderBreakdown(H5)
	h6 = HeaderBreakdown(H6)
	print("*"*50)
	#print([type(i) for i in [h1, h2, h3, h4, h5]])
	print(json.dumps(h1.parsed, indent=4))
	print(json.dumps(h2.parsed, indent=4))
	print(json.dumps(h3.parsed, indent=4))
	print(json.dumps(h4.parsed, indent=4))
	print(json.dumps(h5.parsed, indent=4))
	print(json.dumps(h6.parsed, indent=4))
	print("+"*50)
	print(json.dumps(h1.analyzed, indent=4))
	print(json.dumps(h2.analyzed, indent=4))
	print(json.dumps(h3.analyzed, indent=4))
	print(json.dumps(h4.analyzed, indent=4))
	print(json.dumps(h5.analyzed, indent=4))
	print(json.dumps(h6.analyzed, indent=4))
	print(":"*50)
#	print(h1)
	print("DIRECTION", h1._direction)
	print("HOST", h1._host)
	print("METHOD", h1._method)
	print("PATH", h1._path)
	print("VERS", h1._httpversion)
	print("CODE", h3._responsecode)
	print("PHRASE", h3._responsephrase)
	print("DIRECTION", h6._direction)
	print("HOST", h6._host)
	print("METHOD", h6._method)
	#print(h1)
	#print(h2)
	#print(h3)
	#print(h4)
	#print(h5)

if __name__ == "__main__":
	unit_tests()
'''