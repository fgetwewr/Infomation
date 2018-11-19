# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import pymongo
from scrapy.conf import settings
from pymongo.errors import DuplicateKeyError

import logging
logger = logging.getLogger(__name__)


class InfomationPipeline(object):

    def open_spider(self, spider):
        self.fp = open('info.json', 'w', encoding='utf-8')

    def close_spider(self, spider):
        self.fp.close()

    def process_item(self, item, spider):
        obj = dict(item)
        string = json.dumps(obj, ensure_ascii=False)
        self.fp.write(string + '\n')
        return item


class MongoPipeline(object):

    def __init__(self):
        host = settings["MONGODB_HOST"]
        port = settings["MONGODB_PORT"]
        dbname = settings["MONGODB_DBNAME"]
        sheetname = settings['MONGODB_INFOSHEET']
        # 创建mongodb数据库连接
        client = pymongo.MongoClient(host=host, port=port)
        # 指定数据库
        mydb = client[dbname]
        # 存放数据库的表名称
        self.post = mydb[sheetname]
        self.post.create_index([('sourceWeb', pymongo.ASCENDING), ('brandWord', pymongo.ASCENDING)], unique=True)

    def process_item(self, item, spider):
        data = dict(item)
        # print('guandaoguandaoguandaoguandao')
        # print(data)
        try:
            self.post.insert(data)
            # print('更新成功')

            # 存在 更新，不存在 插入
            # self.post.update({'sourceWeb': item['sourceWeb']}, {'$set': data}, True)

            # 先查询，再插入
            # result = self.post.find_one({'sourceWeb': item['sourceWeb']})
            # if result == None:
            #     self.post.insert(data)
            #     print('更新成功')
            #     print(data)
            # else:
            #     print('已存在')
            #     pass

        except DuplicateKeyError as e:
            print('存在了，跳过')
            # print(e)
            # logger.warning(e)

        # return item
