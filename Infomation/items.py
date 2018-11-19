# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class InfomationItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    # 标题
    title = scrapy.Field()
    # 媒体
    mediaName = scrapy.Field()
    # 日期时间
    newAt = scrapy.Field()
    # 内容
    info = scrapy.Field()
    # 文章链接
    sourceWeb = scrapy.Field()
    # 图片
    imageLogo = scrapy.Field()
    # 对外暴露id
    autoId = scrapy.Field()
    # 关键词位置
    wordPos = scrapy.Field()
    # 对应品牌词id
    brandWord = scrapy.Field()

    main_url = scrapy.Field()