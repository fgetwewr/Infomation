# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import os

import pymongo
import pymysql
import traceback
from pymysql.err import IntegrityError, InternalError, DataError
from scrapy.conf import settings
from pymongo.errors import DuplicateKeyError

import logging
logger = logging.getLogger(__name__)

check_file = 'isRunning.txt'


class MysqlPipeline(object):
    def __init__(self, host, database, user, password, port):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.charset = 'utf8mb4'
        self.use_unicode = True
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get("MYSQL_HOST"),
            database=crawler.settings.get("MYSQL_DATABASE"),
            user=crawler.settings.get("MYSQL_USER"),
            password=crawler.settings.get("MYSQL_PASSWORD"),
            port=crawler.settings.get("MYSQL_PORT")
        )

    def open_spider(self, spider):
        self.db = pymysql.connect(host=self.host, port=self.port, user=self.user, db=self.database, password=self.password, charset=self.charset, use_unicode=self.use_unicode)
        self.cursor = self.db.cursor()

        # # 启动爬虫时判断文件是否存在，存在则删除
        # isFileExist = os.path.isfile(check_file)
        # if isFileExist:
        #     os.remove(check_file)

    def process_item(self, item, spider):
        data = dict(item)
        keys = ','.join(data.keys())
        values = ','.join(['%s']*len(data))
        # print('*'*90)
        sql = "insert into news(%s) values (%s)" % (keys, values)
        # print(sql)
        # print(data.items())
        # print(self.cursor.execute(sql, [v for k, v in data.items()]))
        # print('_______________________________')
        try:
            self.cursor.execute(sql, [v for k, v in data.items()])
            self.db.commit()
            # print('处理成功', self.cursor.rowcount, '条数据')
        except InternalError as e:
            print('不正确的值>>>>>:', item)
            logger.info(e)
            # traceback.print_exc()
        except DataError as e:
            print('数据太长？？？？', item)
            logger.info(e)
            # traceback.print_exc()
        except Exception as e:
            self.db.rollback()
            # logger.info(e)
        # return item

    def close_spider(self, spider):
        self.cursor.close()
        self.db.close()
        f = open(check_file, 'w')       # 创建一个文件，代表爬虫结束运行
        f.close()



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
