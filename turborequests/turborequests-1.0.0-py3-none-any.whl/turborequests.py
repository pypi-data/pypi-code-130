import requests

class TurboRequests:
	def get(self, url, var):
		request = requests.get(url)
		if var == "status":
			pr = request.status_code
		elif var == "text":
			pr = request.text
		else:
			print("status or text")
		print(pr)