
class NewsFeed:
	def __init__(self, providerName):
		self.provider = buildProvider(self, provideName)
		self.result_keys = [
			'total',
			'articles'
			'page'
		]
		self.article_keys = [
			'title',
			'description',
			'content',
			'link',
			'img_link',
			'video_link',
			'publish_date'
		]

	def headline(self, q=None, language=[], country=[], 
					category=[],
					page_size=None,
					page=1):
		language = self._language_mapping(language)
		country = self._country_mapping(country)
		category = self._category_mapping(category)
		ret = self.provider.headline(q=q, language=language,
						country=country,
						category=category,
						page_size=page_size,
						page=page)
		return self._newsset(ret)

	def topic(self, q=None, language=[], country=[], 
					category=[],
					page_size=None,
					page=1):
		language = self._language_mapping(language)
		country = self._country_mapping(country)
		category = self._category_mapping(category)
		ret = self.provider.headline(q=q, language=language,
						country=country,
						category=category,
						page_size=page_size,
						page=page)
		return self._newsset(ret)

	def topstory(self, q=None, language=[], country=[],
					category=category,
					page_size=None,
					page=1):
		language = self._language_mapping(language)
		country = self._country_mapping(country)
		category = self._category_mapping(category)
		ret = self.provider.topstory(q=q, language=language,
						country=country,
						category=category,
						page_size=page_size,
						page=page)
		return self._newsset(ret)

	def _language_mapping(self, language):
		assert isinstance(language, array)
		mapping = self.provider.get_language_mapping()
		return [ mapping.get(i,i) for i in language ]

	def _country_mapping(self, country):
		assert isinstance(country, array):
		mapping = self.provider.get_country_mapping()
		return [ mapping.get(i, i) for i in country ]

	def _category_mapping(self, country):
		assert isinstance(country, array):
		mapping = self.provider.get_category_mapping()
		return [ mapping.get(i, i) for i in country ]

	def news(self, q=None, language=[], country=[],
					category=category,
					page_size=None,
					page=1):
		language = self._language_mapping(language)
		country = self._country_mapping(country)
		category = self._category_mapping(category)
		ret = self.provider.news(q=q, language=language,
						country=country,
						category=category,
						page_size=page_size,
						page=page)
		return self._newsset(ret)
		
	def _newsset(self, retdata):
		result_mapping = self.provider.get_result_mapping()
		if result_mapping is None:
			return retdata
		data = self.dictmap(self.result_keys, result_mapping, retdata)
		article_mapping = self.provider.get_article_mapping()
		if article_mapping is not None:
			articles = data['articles']
			articles = [ self.dictmap(self.article_keys, \
						article_mapping, article) for article in articles ]
			data['articles'] = articles
		return data

	def dictmap(self, keys, mapping, data):
		x = {k:data.get(mapping.get(k,' '), None) for k in keys}
		return x

	def array2param(self, arr, delimiter=','):
		s = delimiter.join(arr)
		if s == '':
			return None
		return s
