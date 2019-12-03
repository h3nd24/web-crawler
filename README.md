# web-crawler
Simple Scrapy-based web crawler used in the MoonLight Project.

Disclaimer: still alpha version, so do let me know if this approach is wrong, etc.

To use, follow the scrapy installation procedure in https://docs.scrapy.org/en/latest/intro/install.html.
For example, we are creating a project with the name of "webcrawler", which is the spider that crawls from Google:
```
scrapy startproject webcrawler
```

Create the directories to store the scraped contents
```
mkdir -p webcrawler/scraped/.png
mkdir -p webcrawler/scraped/.ogg
mkdir -p webcrawler/scraped/.otf
mkdir -p webcrawler/scraped/.json
mkdir -p webcrawler/scraped/.icc
mkdir -p webcrawler/scraped/regex
```

Then, copy the spider into spiders subdirectory
```
ln spider.py webcrawler/webcrawler/spiders
```

And finally, have fun scraping the Internet
```
scrapy crawl webcrawler
```
