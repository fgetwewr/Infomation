import os
import traceback
import pymysql
import datetime
from scrapy.utils.project import get_project_settings
from Infomation import settings

import logging
logger = logging.getLogger(__name__)

check_file = 'isRunning.txt'

isFileExsit = os.path.isfile(check_file)
if isFileExsit:
    print('爬虫结束')


class Statistical:
    def __init__(self):
        self.db = pymysql.connect(
            host=settings.MYSQL_HOST,
            db=settings.MYSQL_DATABASE,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
        )
        self.cursor = self.db.cursor()

    def newsByDay(self):
        """ 该表保存系统中品牌词每天的抓取量，对应系统中的火力时间功能，计算逻辑是：抓取完品牌词后增量扫描所有数据，
        并计算前一天数据抓取的信息量"""

        # sql = 'select * from news where to_days(newsAt) = to_days(now()) group by brandId;'
        # self.cursor.execute(sql)
        # result = self.cursor.fetchall()
        # for x in result:
        #     print(x)

        # 按照brandId分组查询，统计出每个关键字当天的抓取的数量
        select_sql = 'select brandId, count(*) from news where to_days(createdAt) = to_days(now()) group by brandId;'
        self.cursor.execute(select_sql)
        result_tuple = self.cursor.fetchall()
        for result in result_tuple:
            # print(result)
            brandId = result[0]     # 品牌词id
            dayCount = result[1]        # 品牌词每天搜索的信息量
            dayDate = datetime.datetime.now().strftime('%Y-%m-%d')      # 统计日期
            createdAt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            updatedAt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            insert_sql = "insert into newsbyday(brandId, dayCount, dayDate, createdAt, updatedAt) " \
                         "values ('%s', '%s', '%s', '%s', '%s')" % (brandId, dayCount, dayDate, createdAt, updatedAt)
            try:
                self.cursor.execute(insert_sql)
                self.db.commit()
            except Exception as e:
                # traceback.print_exc()
                logger.info(e)

    def mediaByDay(self):
        """该表保存系统媒体表中每个媒体每天的抓取量，计算逻辑是：抓取完品牌词数据后增量扫描所有信息在每个媒体上的数据量"""

        # 先从media表中查询id和mediaName
        select_media = "select id, mediaName from media;"
        self.cursor.execute(select_media)
        media_tuple = self.cursor.fetchall()
        # 遍历媒体库，按当前日期查询每个媒体对应的根据关键词爬取的数据数量
        count = 1
        for media in media_tuple:
            mediaId = media[0]
            mediaName = media[1]
            select_news = "select brandId, count(*) from news where to_days(createdAt) = to_days(now()) and " \
                          "mediaName like '%{}%' group by brandId;".format(mediaName)
            self.cursor.execute(select_news)
            news_tuple = self.cursor.fetchall()

            for news in news_tuple:
                brandId = news[0]       # 品牌词id
                dayCount = news[1]       # 品牌词每天搜索的信息量
                dayDate = datetime.datetime.now().strftime('%Y-%m-%d')      # 统计日期
                createdAt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                updatedAt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                insert_sql = "insert into mediabyday(mediaId, brandId, dayCount, dayDate, createdAt, updatedAt) " \
                             "values ('%s', '%s', '%s', '%s', '%s', '%s')" \
                             % (mediaId, brandId, dayCount, dayDate, createdAt, updatedAt)
                try:
                    self.cursor.execute(insert_sql)
                    self.db.commit()
                    print('成功插入%s条数据' % count)
                    count += 1
                except Exception as e:
                    logger.info(e)

    def subBrandByDay(self):
        """该表保存系统中副词每天抓取量，计算逻辑是：抓取完品牌词数据后增量扫描每个副词前一天的抓取量，"""


        select_brand = "select id from brand;"
        select_subBrand = "select id, name from subbrand;"
        select_news = "select brandId, title, info from news where to_days(createdAt)=to_days(now());"
        self.cursor.execute(select_brand)
        brandId_tuple = self.cursor.fetchall()

        # 创建关键字计数字典
        count_dic = {}
        for brandId in brandId_tuple:
            count_dic[brandId[0]] = 0

        self.cursor.execute(select_news)
        news_tuple = self.cursor.fetchall()

        self.cursor.execute(select_subBrand)
        subBrand_tuple = self.cursor.fetchall()

        # 遍历副词表，news表，
        for subBrand in subBrand_tuple:
            subBrandId = subBrand[0]
            subBrand = subBrand[1]
            dayDate = datetime.datetime.now().strftime('%Y-%m-%d')
            for news in news_tuple:
                brandId = news[0]
                title = news[1]
                info = news[2]
                # 判断副词是否在标题或内容里，如果在，相应的主词计数加一，
                if subBrand in title or subBrand in info:
                    count_dic[brandId] += 1

            for brandId, dayCount in count_dic.items():
                sub_sql = "insert into subBrandByDay (brandId, subBrandId, dayDate, dayCount) values " \
                      "('%s','%s','%s','%s')" % (brandId, subBrandId, dayDate, dayCount)

                try:
                    self.cursor.execute(sub_sql)
                    self.db.commit()
                    print('成功插入数据')
                except Exception as e:
                    logger.info(e)


    def mediaByDay2(self):
        """该表保存系统媒体表中每个媒体每天的抓取量，计算逻辑是：抓取完品牌词数据后增量扫描所有信息在每个媒体上的数据量"""

        # 先从media表中查询id和mediaName
        select_media = "select id, mediaName from media;"
        select_brand = "select id from brand;"
        select_news = "select brandId,mediaName from news where to_days(NOW()) - TO_DAYS(createdAt) <= 1;"
                      # "select brandId, title, info from news where to_days(createdAt)=to_days(now());"

        self.cursor.execute(select_media)
        media_tuple = self.cursor.fetchall()

        self.cursor.execute(select_brand)
        brandId_tuple = self.cursor.fetchall()

        self.cursor.execute(select_news)
        news_tuple = self.cursor.fetchall()

        # 创建关键字计数字典
        count_dic = {}
        for brandId in brandId_tuple:
            count_dic[brandId[0]] = 0


        # 遍历媒体库，按当前日期查询每个媒体对应的根据关键词爬取的数据数量

        dayDate = datetime.datetime.now().strftime('%Y-%m-%d')  # 统计日期
        count = 1
        for media in media_tuple:
            mediaId = media[0]
            mediaName = media[1]    # 媒体库中的媒体名


            for news in news_tuple:
                brandId = news[0]       # 品牌词id
                news_mediaName = news[1]     # 新闻资讯中媒体名

                if mediaName in news_mediaName:
                    count_dic[brandId] += 1

            for brandId, dayCount in count_dic.items():
                createdAt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                updatedAt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                insert_sql = "insert into mediabyday(mediaId, brandId, dayCount, dayDate, createdAt, updatedAt) " \
                             "values ('%s', '%s', '%s', '%s', '%s', '%s')" \
                             % (mediaId, brandId, dayCount, dayDate, createdAt, updatedAt)
                try:
                    self.cursor.execute(insert_sql)
                    self.db.commit()
                    print('成功插入%s条数据' % count)
                    count += 1
                except Exception as e:
                    logger.info(e)

    def mediaAddByDay(self):
        pass


if __name__ == '__main__':
    s = Statistical()
    # s.newsByDay()
    # s.mediaByDay()
    s.mediaByDay2()
    # s.subBrandByDay()