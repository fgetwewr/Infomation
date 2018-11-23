# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class InfomationItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    brandId = scrapy.Field()      # 品牌词id

    title = scrapy.Field()       # 标题

    info = scrapy.Field()       # 内容

    link = scrapy.Field()      # 文章链接

    newsAt = scrapy.Field()      # 文章发布时间

    newsType = scrapy.Field()       # 新闻对应类型，0: 无(默认),1: 图片地址, 2：视频地址

    newsLogoUrl = scrapy.Field()         # 文章包含的图片或视频地址， 如文章未包含媒体信息，则默认为空字符

    mediaName = scrapy.Field()        # 媒体名称

    mediaType = scrapy.Field()      # 媒体类型

    fromSrc = scrapy.Field()        # 抓取来源 1: 百度新闻抓取,2: 百度网页抓取，3: 今日头条抓取

    brandPos = scrapy.Field()       # 关键词位置 0 不在标题和内容中,1 在标题中，2 在内容中，3，在标题和内容中

    autoId = scrapy.Field()         # 对外暴露id

    relatedId = scrapy.Field()       # 相关资讯关联id 此id是某一信息表id

    createdAt = scrapy.Field()      # 创建时间

    updatedAt = scrapy.Field()      # 更新时间

    note = scrapy.Field()       # 备注
