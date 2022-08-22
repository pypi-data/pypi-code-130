import requests
from appPublic.http_client import Http_Client
app_info = {}
# myapp_key='eq2eutdVspOBY58qzXCRKs6uVCzoZnjhk9yLFams'
def set_app_info(appkey):
	app_info.update({
		'appkey':appkey
	})

def buildProvider(newfeed):
	return TheNewsApi(newsfeed)

class TheNewsApi:
	def __init__(self):
		self.newsfeed = newsfeed
		self.appkey = app_info.get('appkey')
		self.categorys = [
			'business',
			'entertainment',
			'environment',
			'food',
			'health',
			'politics',
			'science',
			'sports',
			'technology',
			'top',
			'world'
		]
		self.result_keys = ['status', 'totalResults', 'results', 'nextPage']
		self.news_keys = [
			"title",
			"link",
			"creator",
			"video_url",
			"description",
			"content",
			"pubDate",
			"image_url",
			"source_id",
			"country",
			"category",
			"language"
		]

	def get_countrys(self):
		return {
				'ar':'Argentina',
				'am':'Armenia',
				'au':'Australia',
				'at	Austria',
				'by':'Belarus',
				'be':'Belgium',
				'bo':'Bolivia',
				'br':'Brazil',
				'bg':'Bulgaria',
				'ca':'Canada',
				'cl':'Chile',
				'cn':'China',
				'co':'Colombia',
				'hr':'Croatia',
				'cz':'Czechia',
				'ec':'Ecuador',
				'eg':'Egypt',
				'fr':'France',
				'de':'Germany',
				'gr':'Greece',
				'hn':'Honduras',
				'hk':'Hong Kong',
				'in':'India',
				'id':'Indonesia',
				'ir':'Iran',
				'ie':'Ireland',
				'il':'Israel',
				'it':'Italy',
				'jp':'Japan',
				'kr':'Korea',
				'mx':'Mexico',
				'nl':'Netherlands',
				'nz':'New Zealand',
				'ni':'Nicaragua',
				'pk':'Pakistan',
				'pa':'Panama',
				'pe':'Peru',
				'pl':'Poland',
				'pt':'Portugal',
				'qa':'Qatar',
				'ro':'Romania',
				'ru':'Russia',
				'sa':'Saudi Arabia',
				'za':'South Africa',
				'es':'Spain',
				'ch':'Switzerland',
				'sy':'Syria',
				'tw':'Taiwan',
				'th':'Thailand',
				'tr':'Turkey',
				'ua':'Ukraine',
				'gb':'United Kingdom',
				'us':'United States Of America',
				'uy':'Uruguay',
				've':'Venezuela'
			}
	def getNews(self, keyword, category=[],language=[], page=0):
		url = 'https://api.thenewsapi.com/v1/news/all'
		return self._newcall(url, keyword, category=category,
					language=language, page=page)

	def getHeadlines(self, keyword, category=[],language=[], page=0):
		url = 'https://api.thenewsapi.com/v1/news/top'
		return self._newcall(url, keyword, category=category,
					 language=language, page=page)

	def _newcall(self, keyword, category=[], language=[], page=0):
		hc = Http_Client()
		if keyword == '':
			keyword = None
		category = [ c for c in category if c in self.categorys ]
		category_str = ','.join(category)
		language_str = ','.join(language)
		if language_str == '':
			language_str = None
		if category_str == '':
			category_str = None
		p = {
			'api_token':self.appkey,
			'category':category_str, 
			'language':language_str,
			'page':page,
			'q':keyword
		}
		x = hc.get(url, params=p)
		return x

if __name__ == '__main__':
	set_app_info()
	nc = NewsDataIo()
	while True:
		print('key word to search news, ":quit" to exit')
		x = input()
		if x == ':quit':
			break
		news = nc.getNews(x)
		print(news.keys())
		print(news['results'][0].keys())
