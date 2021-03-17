import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import NewwbItem
from itemloaders.processors import TakeFirst
import json
pattern = r'(\xa0)?'
base = 'https://proxy.newb.coop/api/v1/Posts/preview?skip={}&take=6'

class NewwbSpider(scrapy.Spider):
	name = 'newwb'

	page = 0
	start_urls = [base.format(page)]

	def parse(self, response):
		data = json.loads(response.text)
		for index in range(len(data)):
			links = data[index]['slug'][0]['value']
			full_url = "https://www.newb.coop/nl/blog/"+links
			yield response.follow(full_url, self.parse_post)
		if not response.text == "[]":
			self.page += 5
			yield response.follow(base.format(self.page),self.parse, dont_filter=True)

	def parse_post(self, response):
		try:
			date = response.xpath('//h1/strong/text()').get().split(' . ')[0]
		except AttributeError:
			date= "None"
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//div[@class="article__description"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=NewwbItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
