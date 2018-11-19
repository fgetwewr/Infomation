import pymongo
import scrapy
from scrapy.utils.project import get_project_settings
#
#
# class KwdExistsSpider(scrapy.Spider):
#     name = 'exists'
#     allowed_domains = ['www.baidu.com']
#     start_urls = []
#     # 连接数据库
#     settings = get_project_settings()
#     host = settings['MONGODB_HOST']
#     port = settings['MONGODB_PORT']
#     dbname = settings['MONGODB_DBNAME']
#     infoname = settings['MONGODB_INFOSHEET']
#     kwdname = settings['MONGODB_KWDSHEET']
#     myclient = pymongo.MongoClient(host=host, port=port)
#     info_db = myclient[dbname]
#     info_sheet = info_db[infoname]
#     kwd_sheet = info_db[kwdname]
#     meta = {'kwd': '三只松鼠'}
#     print(':::::::::::::::::::::::')
#     for kwd in info_sheet.find({'wordPos': '0'}):
#         url = kwd.get('sourceWeb')
#         brandWord = kwd.get('brandWord')
#         word = kwd_sheet.find({'id': brandWord})[0]
#         print(word)
#
#         start_urls.append(url)
#     # print(start_urls)
#
#     def parse(self, response):
#         # kwd = response.meta['kwd']
#         print('**************************')
#         # print(kwd)
