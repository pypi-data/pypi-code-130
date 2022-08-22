import importlib

def buildProvider(newsfeed, providerName):
	_module = importlib.import_module(providerName)
	return _module.buildProvider(tts)

class NewsFeed:
	def __init__(self, providerName):
		self.provider = buildProvider(self, provideName)
		self.result_keys = [
			'total',
			'articles'
			'page'
		]
		self.catepory = [
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
		self.languages = [
			'ar',
			'bg',
			'bn',
			'cs',
			'da',
			'de',
			'el',
			'en',
			'es',
			'et',
			'fa',
			'fi',
			'fr',
			'he',
			'hi',
			'hr',
			'hu',
			'id',
			'it',
			'ja',
			'ko',
			'lt',
			'multi',
			'nl',
			'no',
			'pl',
			'pt',
			'ro',
			'ru',
			'sk',
			'sl',
			'sv',
			'ta',
			'th',
			'tr',
			'uk',
			'vi',
			'zh'
		]
		self.countries = [
			'ar',
			'am',
			'au',
			'at',
			'by',
			'be',
			'bo',
			'br',
			'bg',
			'ca',
			'cl',
			'cn',
			'co',
			'hr',
			'cz',
			'ec',
			'eg',
			'fr',
			'de',
			'gr',
			'hn',
			'hk',
			'in',
			'id',
			'ir',
			'ie',
			'il',
			'it',
			'jp',
			'kr',
			'mx',
			'nl',
			'nz',
			'ni',
			'pk',
			'pa',
			'pe',
			'pl',
			'pt',
			'qa',
			'ro',
			'ru',
			'sa',
			'za',
			'es',
			'ch',
			'sy',
			'tw',
			'th',
			'tr',
			'ua',
			'gb',
			'us',
			'uy',
			've'
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

	def get_data_by_key(self, data, k_str):
		ks = '.'.split()
		x = data.get(ks[0]
		for k in ks[1:]:
			if x is None:
				return None
			x = x.get(k)
		return x

	def dictmap(self, keys, mapping, data):
		x = {k:self.get_data_by_key(data, mapping.get(k,k)) for k in keys}
		return x

	def array2param(self, arr, delimiter=','):
		s = delimiter.join(arr)
		if s == '':
			return None
		return s

	def get_countrys(self):
		return {
				'ar':'Argentina',
				'am':'Armenia',
				'au':'Australia',
				'at':'Austria',
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
