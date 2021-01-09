
import scrapy
import logging
logger = logging.getLogger('scrapy_crawl')
logger.setLevel('ERROR')
import pymongo
from datetime import datetime

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}

#Initialise Database Connection
mongoClient = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=10)
try:
    mongoClient.server_info()
except Exception as e:
    raise e
mongoDB = mongoClient["rdandx"]
contentCollection = mongoDB['contentMaster']

class QuotesSpider(scrapy.Spider):
    name = "firstpost"

    def start_requests(self):
        # Home Page
        urls = [
            'https://www.firstpost.com/'
        ]
        for url in urls:
            yield scrapy.Request(url=url, headers=headers, callback=self.parse)

    def parse(self, response):     

        # Home Page 
        yield scrapy.Request(url=response.request.url, headers=headers, callback=self.parse_category, meta={'category_name': 'home'}, dont_filter=True)
        main_header = response.css('.main-menu')
        all_headers_element =  main_header.css('li')

        # Iterate Each Category Page
        for each_element in all_headers_element:
            category_name = each_element.css('a::text').extract_first()
            category_link = each_element.css('a::attr(href)').extract_first()
            yield scrapy.Request(url=category_link, headers=headers, callback=self.parse_category, meta={'category_name': category_name})
        
    def parse_category(self, response):
        category_name = response.meta['category_name']
        main_content = response.css('.main-content')
        main_story_thumb = main_content.css('.main-story-thumb')
        all_big_thumbs = main_content.css('.big-thumb')
        for each_main_story in main_story_thumb:
            news_link = each_main_story.css('::attr(href)').extract_first()
            yield scrapy.Request(url=news_link, headers=headers, callback=self.parse_page, meta={'category_name': category_name})
        for each_thumb in all_big_thumbs:
            news_link = each_thumb.css('a::attr(href)').extract_first()
            yield scrapy.Request(url=news_link, headers=headers, callback=self.parse_page, meta={'category_name': category_name})

        # Iterate each page within a category
        if(response.css('.pagination').css('.next')):
            next_page_link = response.css('.pagination').css('.next').css('a::attr(href)').extract_first()
            yield scrapy.Request(url=next_page_link, headers=headers, callback=self.parse_category, meta={'category_name': category_name})


    def parse_page(self, response):
        page_link = response.request.url
        category_name = response.meta['category_name']
        article_title = response.css('h1 *::text').extract_first().replace("\n", "").strip()
        content_text = ' '.join(response.css('.inner-copy').css('p *::text').extract())
        if not content_text:
            content_text = ' '.join(response.css('#article-full-content_9186021').css('p *::text').extract()) if response.css('#article-full-content_9186021').extract() else ''
        all_links_inside_page = list(set(response.css('.inner-copy').css('a::attr(href)').extract()))
        if not all_links_inside_page:
            all_links_inside_page = list(set(response.css('#article-full-content_9186021').css('a::attr(href)').extract())) if response.css('#article-full-content_9186021').extract() else []
        image_link = response.css('.inner-copy').css('img::attr(src)').extract_first()
        updated_date = int(datetime.now().strftime("%s")) * 1000 

        final_dict = {'page_link': page_link, 'article_title': article_title, 'category_name': category_name, 
                    'content_text': content_text, 'image_link': image_link, 'updated_date': updated_date, 'all_links':all_links_inside_page}

        # Upsert is enabled in order to avoid duplicate page links        
        result = contentCollection.update({'page_link': page_link}, {"$set": final_dict}, upsert=True)
