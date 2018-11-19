import random
import time
import pymongo
from scrapy.utils.project import get_project_settings
from auto_id import getNextValue

'''
星空媒体
海底捞
三只松鼠
三只松鼠 霉变
软文街
小龙坎 地沟油


关键词表
id              数据库自增id 
name,           关键词名称
wordType,       关键词分类    品牌词，竞品词，负面舆论监测
platform,       搜索平台      百度，微信，微博
autoId          对外暴露id    可用随机数加当天时间戳
'''


class Storage_kwd:

    def __init__(self):
        settings = get_project_settings()
        host = settings["MONGODB_HOST"]
        port = settings["MONGODB_PORT"]
        dbname = settings["MONGODB_DBNAME"]
        sheetname = settings['MONGODB_KWDSHEET']

        # 创建mongodb数据库连接
        client = pymongo.MongoClient(host=host, port=port)
        # 指定数据库
        self.mydb = client[dbname]
        # 存放数据库的表名称(集合)
        self.kwd_sheet = self.mydb[sheetname]
        #
        self.ids = self.mydb['ids']
        self.kwd_dict = {}

    def storage(self):

        self.kwd_dict['name'] = '小龙坎 地沟油'
        self.kwd_dict['wordType'] = '品牌词'
        self.kwd_dict['platform'] = '百度'

        # 对外暴露id
        rand_num = random.random() * 9000
        num = round(rand_num) + 1000
        timed = round(time.time() * 1000)
        self.kwd_dict['autoId'] = str(num) + str(timed)
        # 自增id
        self.kwd_dict['id'] = getNextValue('productid')

    def insert_kwd(self):
        self.kwd_sheet.insert(self.kwd_dict)
        print('关键字插入成功')



if __name__ == '__main__':

    kwd_list = ['星空媒体, 海底捞, 三只松鼠, 三只松鼠 霉变, 软文街, 小龙坎 地沟油']

    kwd = Storage_kwd()
    for i in kwd_list:
        kwd.storage()
        kwd.insert_kwd()
