# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.crawler import CrawlerProcess
from raise_money.items import RaiseMoneyItem

class RaisespiderSpider(scrapy.Spider):
    name = 'raisemoneyspider'
    allowed_domains = ['fundrazr.com']
    start_urls = ['https://fundrazr.com/find?category=Health']
    custom_settings = {
    'LOG_FILE': 'logs/raise_money.log',
    'LOG_LEVEL':'DEBUG'
     }

    def parse(self, response):
        print('Processing..' + response.url)

        for money in response.css('div.widget'):
		Link = response.urljoin(money.css('h2.title > a::attr(href)').extract_first())
		Title = money.css('h2.title > a::text').extract_first()
		Location = money.css('p.location > a::text').extract_first()
		Author = money.css('p.byline::text').extract_first()
		yield Request(Link, callback=self.parse_page, meta={'Link': Link, 'Title': Title, 'Location': Location, 'Author': Author})

	relative_next_url = response.css('li.next > a::attr(href)').extract_first()
        absolute_next_url = response.urljoin(relative_next_url)
        yield Request(absolute_next_url, callback=self.parse)

    def parse_page(self, response):
	item = RaiseMoneyItem()
	item['Link'] = response.meta.get('Link')
	item['Title'] = response.meta.get('Title')
	item['Location'] = response.meta.get('Location')
	item['Author'] = response.meta.get('Author')[3::]
	item['Story'] = response.css('div.wysiwyg-content > p::text').extract_first().strip()
	item['Description'] = response.css('span.content::text').extract_first().strip()
	item['Amount'] = response.css('span.amount-raised::text').extract_first() + response.css('span.currency-symbol::text').extract_first()
	item['Progress'] = response.css('span.raised-progress::text').extract_first()
	item['Contributores'] = response.css('span.donation-count::text').extract_first()
	yield item
