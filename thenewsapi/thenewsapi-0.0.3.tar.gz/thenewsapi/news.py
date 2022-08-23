import requests
from appPublic.http_client import Http_Client
from appPublic.timeUtils import curDateString
from uninews.baseprovider import BaseProvider
from .version import __version__
app_info = {}

def set_app_info(appkey):
	app_info.update({
		'appkey':appkey
	})

def buildProvider(newsfeed):
	print(f'TheNewsApi version {__version__}')
	return TheNewsApi(newsfeed)

class TheNewsApi(BaseProvider):
	def __init__(self, newsfeed):
		self.newsfeed = newsfeed
		self.appkey = app_info.get('appkey')

	def get_result_mapping(self):
		return {
			'total':'meta.found',
			'rows':'meta.limit',
			'page':'meta.page',
			'articles':'data'
		}
	
	def get_article_mapping(self):
		return {
			'link':'url',
			'img_link':'image_url',
			'publish_date':'published_at'
		}
	
	def news(self, q=None, 
						categories=[],
						countries=[], 
						language=[], 
						page=0):
		url = 'https://api.thenewsapi.com/v1/news/all'
		return self._newscall(url, q, categories=categories,
					countries=countries,
					language=language, 
					page=page)

	def headline(self, keyword, categories=[],
						countries=[], language=[], page=0):
		url = 'https://api.thenewsapi.com/v1/news/headline'
		return self._newscall(url, q, 
						categories=categories,
						countries=countries,
						language=language, page=page)

	def topstory(self, q=None, categories=[],
						countries=[], language=[], page=0):
		url = 'https://api.thenewsapi.com/v1/news/top'
		return self._newscall(url, q, 
						categories=categories,
						countries=countries,
						language=language, page=page)

	def topic(self, q=None, language=[], countries=[],
				categories=[], page_size=20,
				page=0):
		return None

	def _newscall(self, url, keyword, 
						categories=[], 
						countries=['cn'],
						language=['zh'], 
						page=0):
		hc = Http_Client()
		if keyword == '':
			keyword = None
		categories = self.newsfeed.array2param(categories)
		language_str = self.newsfeed.array2param(language)
		countries_str = self.newsfeed.array2param(countries)
		p = {
			'api_token':self.appkey,
			'categories':categories, 
			'language':language_str,
			'published_on':curDateString(),
			'locale':countries,
			'limit':50,
			'page':page,
			'search':keyword
		}
		x = hc.get(url, params=p)
		return x

if __name__ == '__main__':
	print('input appkey:')
	appkey=input()
	set_app_info(appkey)
	nc = TheNewsApi()
	while True:
		print('key word to search news, ":quit" to exit')
		x = input()
		if x == ':quit':
			break
		news = nc.getNews(x)
		print(news.keys())
		print(news['results'][0].keys())
