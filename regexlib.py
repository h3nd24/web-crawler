# -*- coding: utf-8 -*-
# This is a simple spider that crawl regexlib.com for the regexes.
import scrapy
import re
import hashlib 

class RegexSpider(scrapy.Spider):
    name = 'regexlib'
    start_urls = ['http://regexlib.com/Search.aspx?k=&c=-1&m=-1&ps=100']
 
    def parse(self, response):
        # apparently the expressions are all in the div.expressionDiv
        for div in response.css('div.expressionDiv::text'):
            regex_content = div.get()
            fname = hashlib.md5(regex_content.encode()).hexdigest()
            with open("scraped/regex/" + fname, "w") as f:
                f.write(regex_content)

        # hit the next button
        href = response.css('a#ctl00_ContentPlaceHolder1_Pager2_StepForwardOneHyperLink')
        url = href.attrib['href']
        url = response.urljoin(url)
        yield scrapy.Request(url, callback=self.parse)
