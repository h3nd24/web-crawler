# -*- coding: utf-8 -*-
# This is a simple spider that crawl https://archive.org for various file types.
# The starting point is currently still the hard-coded image media type.
# We are using the scraping API provided by the https://archive.org, which provides list of ID / title in the form of JSON.

import scrapy
import re
import hashlib 
import json

INTERESTING_EXTENSIONS = [".json", ".otf", ".icc", ".ogg", ".png", "woff2"]
scrapingAPI = 'https://archive.org/services/search/v1/scrape?q=mediatype:image&count=250'

class InternetArchiveSpider(scrapy.Spider):
    name = 'InternetArchive'
    start_urls = [scrapingAPI] # internet archive image collections
 
    def parse(self, response):
        result_obj = json.loads(response.text)
        cursor = result_obj['cursor']
        items = result_obj['items']
    
        # iterate over the items
        for item in items:
            yield scrapy.Request("https://archive.org/detail/" + item['identifier'], self.parse_title)

        # continue scraping
        if cursor is not None:
            yield scrapy.Request(scrapingAPI + "&cursor=" + cursor, self.parse)

    # parse a particular title / ID pointed out by the scraping API
    def parse_title(self, response):
        # the "show all" button that leads to all the files is located in "boxy-ttl"
        for href in response.css('a.boxy-ttl'):
            url = href.attrib['href']
            yield response.follow(url, self.parse_download)

    # parse the list of files (and subdirectories in that title
    def parse_download(self, response):
        # the file list is located in "directory-listing-table"
        for href in response.css('.directory-listing-table a'):
            url = href.attrib['href']
            # ignore backjump
            if "/details/" in url:
                continue
            # traverse directories
            if url.endswith("/"): 
                yield response.follow(url, self.parse_download)
            # parse item
            else:
                extension = list(filter(lambda x: url.lower().endswith(x), INTERESTING_EXTENSIONS))
                # only follow the link to files that have extension of interest
                if extension:
                    yield response.follow(url, self.parse_item)

    # actually follow the link to the file and save it
    def parse_item(self, response):
        # this is duplicate with the check, but it will prevent opening links that are useless
        extension = list(filter(lambda x: response.url.lower().endswith(x), INTERESTING_EXTENSIONS))
        if extension:
            print ("============================= Parse Item : " + response.url + " ===================================")
            # only take files that are less than 1MB
            if len(response.body) <= 1048576:
              # we use md5 to "deduplicate" the crawling results"
              fname = hashlib.md5(response.body).hexdigest() + extension[0]
              with open("scraped/" + extension[0] + "/" + fname, "wb") as f:
                  f.write(response.body)
