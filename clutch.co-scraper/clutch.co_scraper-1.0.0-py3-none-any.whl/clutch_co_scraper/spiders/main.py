from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.crawler import CrawlerProcess
from clutch_co_scraper.clutch_co_scraper.items import FirmItem, FirmLoader
from scrapy.http import HtmlResponse
import re


class MainSpider(CrawlSpider):

    custom_settings = {
        "ITEM_PIPELINES": {
           'clutch_co_scraper.clutch_co_scraper.pipelines.ClutchCoScraperPipeline': 300,
        },

        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
            'scrapy_fake_useragent.middleware.RetryUserAgentMiddleware': 401,
        },

        'FAKEUSERAGENT_PROVIDERS': [
            'scrapy_fake_useragent.providers.FakeUserAgentProvider',
            'scrapy_fake_useragent.providers.FakerProvider',
            'scrapy_fake_useragent.providers.FixedUserAgentProvider',
        ],

        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',

        'ROBOTSTXT_OBEY': False,

        'DOWNLOAD_DELAY': 0,
        'DOWNLOAD_TIMEOUT': 30,
        'RANDOMIZE_DOWNLOAD_DELAY': True,

        'REACTOR_THREADPOOL_MAXSIZE': 128,
        'CONCURRENT_REQUESTS': 256,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 256,
        'CONCURRENT_REQUESTS_PER_IP': 256,

        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 0.25,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 128,
        'AUTOTHROTTLE_DEBUG': True,

        'RETRY_ENABLED': True,
        'RETRY_TIMES': 3,

    }

    name = 'main'
    allowed_domains = ['clutch.co']
    start_urls = ['http://clutch.co']
    rules: list
    # Filters specified by user
    kwargs: dict
    start_url_response: HtmlResponse
    # Xpaths to info about firm
    xpaths = {
        'name': './/a[@class="company_title directory_profile"]/text()',
        'website_link': './/a[@class="website-link__item"]/@href',
        'location': './/span[@class="locality"]/text()',
        'min_project_size': './/div[@class="module-list"]/div[1]/span[not(@class)]/text()',
        'avg_hourly_rate': './/div[@class="module-list"]/div[2]/span/text()',
        'rating': './/span[@class="rating sg-rating__number"]/text()',
        'reviews': './/a[@class="reviews-link sg-rating__reviews directory_profile"]/text()'
    }

    def __init__(self, *args, **kwargs):
        super(MainSpider, self).__init__(*args, **kwargs)
        self.kwargs = kwargs['kwargs']
        rules = []
        category_xpath = f'button[@class="sitemap-button collapsed"]'
        subcategory_xpath = 'a[@class="sitemap-nav__item"]'
        xpath_func = 'translate(normalize-space(text()),"ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")'
        callback_func = 'parse_pagination'
        process_links_func = 'process_links'

        # Append links to the rules according to the categories and subcategories specified by user
        for category, subcategories in self.kwargs['categories'].items():
            if not bool(category) and not bool(subcategories[0]):
                rules.append(Rule(LinkExtractor(
                    restrict_xpaths=f'//{subcategory_xpath}'),
                        callback=callback_func, process_links=process_links_func))

            elif not bool(subcategories[0]):
                rules.append(Rule(LinkExtractor(
                    restrict_xpaths=f'//{category_xpath}[{xpath_func} = "{category}"]'
                                    f'/following-sibling::*/{subcategory_xpath}'),
                        callback=callback_func, process_links=process_links_func))
            else:
                for subcategory in subcategories:
                    rules.append(Rule(LinkExtractor(
                        restrict_xpaths=f'//{subcategory_xpath}[{xpath_func} = "{subcategory}"]'),
                            callback=callback_func, process_links=process_links_func))

        MainSpider.rules = rules
        super(MainSpider, self)._compile_rules()

    def parse_start_url(self, response, **kwargs):
        self.start_url_response = response

    def process_links(self, links):
        parameters = '?'
        if bool(self.kwargs['filters']):
            for filter_name, filter_value in self.kwargs['filters'].items():
                parameters = parameters + f'{filter_name}={filter_value}&'

        for link in links:
            link.url = f'{link.url}{parameters}'
            yield link

    def parse_pagination(self, response):
        page_count = response.xpath('//li[@class="page-item last"]/a/@data-page').get()
        if page_count is None:
            links = [response.url]
        else:
            links = [f'{response.url}page={i}' for i in
                     range(int(page_count) + 1)]

        yield from response.follow_all(links, callback=self.parse_item)

    def parse_item(self, response):
        subcategory_link = response.url.split("?")[0].replace("https://clutch.co", "")
        category = self.start_url_response.xpath(
            f'//a[@href="{subcategory_link}"]/../preceding-sibling::*/text()').get()
        subcategory = self.start_url_response.xpath(f'//a[@href="{subcategory_link}"]/text()').get()

        loader = FirmLoader(item=FirmItem(), response=response)
        loader.add_value('category', category)
        loader.add_value('subcategory', subcategory)

        for item in response.xpath('//li[@data-position]'):
            name = item.xpath(self.xpaths['name']).get(default='not-found')
            website_link = item.xpath(self.xpaths['website_link']).get(default='not-found')
            location = item.xpath(self.xpaths['location']).get(default='not-found')
            min_project_size = ''.join(
                re.findall(r'^-1$|\d+', item.xpath(self.xpaths['min_project_size']).get(default='-1')))
            avg_hourly_rate = item.xpath(self.xpaths['avg_hourly_rate']).get(default='-1').split(' /')[0].replace('$',
                                                                                                                  '')
            rating = item.xpath(self.xpaths['rating']).get(default='-1')
            reviews = re.findall(r'^-1$|\d+', item.xpath(self.xpaths['reviews']).get(default='-1'))[0]

            loader.add_value('name', name)
            loader.add_value('website_link', website_link)
            loader.add_value('location', location)
            loader.add_value('min_project_size', min_project_size)
            loader.add_value('avg_hourly_rate', avg_hourly_rate)
            loader.add_value('rating', rating)
            loader.add_xpath('reviews', reviews)

        yield loader.load_item()


def run_spider():
    categories = {}
    while True:
        category = input('Category: ').casefold().strip()
        subcategories = [value.casefold().strip() for value in input('Subcategories: ').split(',')]
        print('-' * (15 + sum(len(i) for i in subcategories)))

        if not bool(category) and not bool(subcategories[0]):
            break

        categories[category] = []
        categories[category].extend(subcategories)

    client_budget = input('Max client budget: ')
    hourly_rate = input('Hourly rate: ')
    reviews = input('Minimum number of reviews: ')
    print('-' * (27 + sum(len(i) for i in reviews)))
    filters = {'client_budget': client_budget, 'hourly_rate': hourly_rate, 'reviews': reviews}

    for filter_name, filter_value in list(filters.items()):
        if not bool(filter_value):
            del filters[filter_name]

    process = CrawlerProcess()
    process.crawl(MainSpider, kwargs={'categories': categories, 'filters': filters})
    process.start()
