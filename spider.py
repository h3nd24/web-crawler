# -*- coding: utf-8 -*-
# Web crawler that starts from a google search and then crawls the internet for the file types of interests.
# At the moment the starting query and the output directory are still hard-coded.
# Credit to https://dev.to/muhajirdev/scraping-from-google-visualizing-most-common-word-with-wordcloud-4mko,
# https://www.imagescape.com/blog/2018/08/20/scraping-pdf-doc-and-docx-scrapy/,
# and https://docs.scrapy.org/en/latest/intro/tutorial.html for the inspiration.
# Don't forget to set the ROBOTSTXT_OBEY = False in settings.py (according to the first link)

import scrapy
import re
import hashlib 

def is_google(url):
    return bool(re.search("/search", url))

INTERESTING_EXTENSIONS = [".json", ".otf", ".icc", ".ogg", ".png"]
query = "q=json+files"

class JSONSpider(scrapy.Spider):
    name = 'webcrawler'
    start_urls = ['https://www.google.com/search?' + query]
 
    def parse(self, response):
        google_next = ""
        max_start = 0
        # find the "next" button from google search. 
        # It is characterized by the existence of the query and keyword "start" in the GET parameter
        for href in response.css('a'):
            url = href.attrib['href']
            if is_google(url):
                if (query in url) and ("start" in url):
                    start_index = int(re.match(r".*start=(\d+)", url).group(1))
                    if start_index > max_start:
                        max_start = start_index
                        google_next = url

        # What is `kCrYT a`
        # If you do `scrapy shell https://www.google.com/search?q=Sukijan&oq=sukijan&aqs=chrome.0.69i59j0l5.1739j0j7&sourceid=chrome&ie=UTF-8#ip=1`
        # And then do `view(response)`. It will open up a browser
        # From there do inspect element, locate a link, And you'll find that most of the links fall under `.kCrYT` class
        for href in response.css('.kCrYT a'):
            url = href.attrib['href']
            # We want to open url these links. But we don't want to open Google's url
            # For example url `More images for Sukijan`, etc.
            if not is_google(url):
                # This basically means 'Hey scrapy` follow this url.
                # When you find it run parse_text function on it.
                yield response.follow(href, self.parse_search_result)

        # follow the next google page
        if google_next: 
            google_next = response.urljoin(google_next)
            print("===================" + google_next + "========================")
            with open("google_log","a") as f:
                f.write(google_next + "\n")
            yield scrapy.Request(google_next, callback=self.parse)

    # we should not be in Google-land anymore, only crawl the link up to depth 1
    def parse_search_result(self, response):
        for href in response.css('a'):
            next_page = response.urljoin(href.attrib['href'])
            yield scrapy.Request(next_page, callback=self.parse_item)

    def parse_item(self, response):
        # only take those links that ends with the file extension of interest
        extension = list(filter(lambda x: response.url.lower().endswith(x), INTERESTING_EXTENSIONS))
        if extension:
            # only take files that are less than 1MB
            if len(response.body) <= 1048576:
              # we use md5 to "deduplicate" the crawling results"
              fname = hashlib.md5(response.body).hexdigest() + extension[0]
              with open("scraped/" + extension[0] + "/" + fname, "wb") as f:
                  f.write(response.body)
