from scrapy import cmdline


cmdline.execute('scrapy crawl info'.split())
# cmdline.execute('scrapy crawl info -s JOBDIR=crawls/storeMyRequest'.split())