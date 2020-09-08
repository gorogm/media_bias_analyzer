import scrapy
import os
from datetime import datetime, timedelta


def datetime_range(start=None, end=None):
    span = end - start
    for i in range(span.days + 1):
        yield start + timedelta(days=i)

class IndexSpider(scrapy.Spider):
    def __init__(self):
        if os.path.exists('index_scraped.json'):
            os.remove('index_scraped.json')

    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'DOWNLOAD_DELAY': 1.0,
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter' # needed for index
    }

    name = 'index_scraped'
    start_urls = []
    rovat = 'gazdasag'
    start_urls = ['https://index.hu/24ora?s=&tol=2012-01-01&ig=2019-12-31&profil=&rovat='+rovat+'&cimke=&word=1&pepe=1']

    def parse(self, response):
        count = 0
        for quote in response.css('article.rovatajanlo'):
            count += 1
            yield {
                'date': quote.xpath('header/a/@data-date').get(),
                'url': quote.xpath('header/a/@href').get(),
                'text': '',
                'title': quote.xpath('div/h2/a/text()').get(),
                'ajanlo': quote.css('p.ajanlo::text').get(),
                'rovat' : quote.css('a.rovat::attr(href)').get().replace('/', ''),
            }

        index_items_per_response = 60
        if count >= index_items_per_response:
            current_url = response.request.url
            if '&p=' in current_url:
                remaining_str = current_url[current_url.index('&p=') + 3 : ]
                if '&' in remaining_str:
                    remaining_str = remaining_str[0 : remaining_str.index('&')]
                current_page = int(remaining_str)
                next_page = current_url.replace('&p=' + str(current_page), '&p=' + str(current_page+1))
            else:
                next_page = current_url + '&p=1'
            yield response.follow(next_page, self.parse)