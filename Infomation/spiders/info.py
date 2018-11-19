import requests
import re
import time
import random
import datetime
import pymongo
import urllib
from urllib import parse
import scrapy
from Infomation.items import InfomationItem
from scrapy.utils.project import get_project_settings


# import logging
#
# logger = logging.getLogger(__name__)


class InformationSpider(scrapy.Spider):
    name = 'info'
    allowed_domains = ['www.baidu.com']
    base_url = 'https://www.baidu.com/s?ie=utf-8&cl=2&rtt=1&bsst=1&tn=news&word={}&pn=0'

    def __init__(self, base_url=base_url, *args, **kwargs):
        super(InformationSpider, self).__init__(*args, **kwargs)
        self.start_urls = []
        self.kwd_dict = {}

        # 连接数据库
        settings = get_project_settings()
        host = settings['MONGODB_HOST']
        port = settings['MONGODB_PORT']
        dbname = settings['MONGODB_DBNAME']
        sheetname = settings['MONGODB_KWDSHEET']
        myclient = pymongo.MongoClient(host=host, port=port)
        kwd_db = myclient[dbname]
        kwd_sheet = kwd_db[sheetname]

        for kwd in kwd_sheet.find():
            self.kwd_dict['{}'.format(kwd.get('name'))] = kwd.get('id')
            self.start_urls.append(base_url.format(kwd.get('name')))
        # print('??????????????????????????????????????????????????')
        # print(self.start_urls)

    def parse(self, response):
        # scrapy shell调试使用
        # if item['title'] == '今晚十点,我们要公布一件事情':
        #     from scrapy.shell import inspect_response
        #     inspect_response(response, self)

        # 获取请求url，正则匹配到关键字，解码
        url = response.url
        kwd_encode = re.compile(r'&word=(.*?)&').findall(url)
        keyword_init = urllib.parse.unquote(kwd_encode[0])
        keyword = re.sub(r'\+', ' ', keyword_init)

        # 获取当前页面资讯列表
        info_list = response.xpath('//div[@id="content_left"]//div[@class="result"]')
        for info in info_list:
            item = InfomationItem()

            # 获取网站链接
            item['sourceWeb'] = info.xpath('./h3[@class="c-title"]/a/@href').extract_first()

            # 获取标题
            title_html = info.xpath('./h3[@class="c-title"]/a').extract_first()
            pattern1 = re.compile(r'target="_blank">(.*?)</a>', re.S)
            title = pattern1.findall(title_html)
            item['title'] = re.sub(r'<em>|</em>', '', title[0]).strip()

            # 先得到含有内容的Html
            content = info.xpath('.//div').extract_first()
            # 获取时间，媒体
            # 获得媒体
            pattern_media = re.compile(r'<p class="c-author">(\w+).*?</p>', re.S)
            item['mediaName'] = pattern_media.findall(content)[0]

            # 获取 格式为2018年10月08日 15:11 日期
            pattern_date = re.compile(r'<p class="c-author">.*?(\d+年\d+月\d+日 \d+:\d+).*?</p>', re.S)
            date = pattern_date.findall(content)
            # 获取 格式为 xx小时前 日期
            pattern_hour = re.compile(r'<p class="c-author">.*?(\w+)小时前.*?</p>', re.S)
            hours = pattern_hour.findall(content)
            # 获取 格式为 xx分钟前 日期
            pattern_minute = re.compile(r'<p class="c-author">.*?(\w+)分钟前.*?</p>', re.S)
            minutes = pattern_minute.findall(content)
            if date:
                item['newAt'] = date[0]
            elif hours:
                p_hours = (datetime.datetime.now() + datetime.timedelta(hours=-int(hours[0]))).strftime('%Yn%my%dr %H:%M')
                item['newAt'] = p_hours.replace('n', '年').replace('y', '月').replace('r', '日')
            elif minutes:
                p_minutes = (datetime.datetime.now() + datetime.timedelta(minutes=-int(minutes[0]))).strftime('%Yn%my%dr %H:%M')
                item['newAt'] = p_minutes.replace('n', '年').replace('y', '月').replace('r', '日')

            # 获取内容
            pattern_info = re.compile(r'<p class="c-author">.*?</p>(.*?)<span class="c-info">', re.S)
            text = pattern_info.findall(content)
            item['info'] = re.sub(r'<em>|</em>', '', text[0]).strip()

            # 获取图片
            image = info.xpath(r'.//div[@class="c-span6"]/a[@class]/img/@src').extract_first()
            if image is not None:
                item['imageLogo'] = image
            else:
                item['imageLogo'] = ' '

            # 对外暴露id
            rand_num = random.random() * 9000
            num = round(rand_num) + 1000
            timed = round(time.time() * 1000)
            item['autoId'] = str(num) + str(timed)

            # 对应关键字id
            item['brandWord'] = self.kwd_dict.get(keyword)

            # 判断关键字是否在标题或内容里面
            for kwd in keyword.split(' '):
                if (kwd in item['title']) and (kwd in item['info']):
                    item['wordPos'] = '3'
                    break
                elif kwd in item['title']:
                    item['wordPos'] = '1'
                    break
                elif kwd in item['info']:
                    item['wordPos'] = '2'
                    break

                # 判断关键字是否存在于详情页内容里
            else:
                # 通过requests.get()请求单条资讯url,判断关键字是否在内容里面
                try:
                    resp = requests.get(url=item['sourceWeb'], timeout=5).text
                    for kwd in keyword.split(' '):
                        if kwd in resp:
                            item['wordPos'] = '2'
                            break
                    else:
                        item['wordPos'] = '0'
                except Exception as e:
                    # print(e)
                    item['wordPos'] = '0'
                    print(item)
                    self.logger.info('请求详情页%s' % e)
            item['relateId'] = ' '
            item['main_url'] = response.url
            yield item

            # 判断是否有 "查看更多相关资讯"，如果有继续回调parse进行抓取
            more_info = info.xpath('.//span[@class="c-info"]/a[re:test(text(),".*?查看更多相关资讯.*?")]/@href').extract_first()

            if more_info:
                print('----------------------------------------')
                print(item)
                more_info_url = response.urljoin(more_info)
                # print(more_info_url)
                print('这是相关资讯里的内容')
                yield scrapy.Request(
                    url=more_info_url,
                    callback=self.parse,
                )

            # 获取下一页链接
            url_next = response.xpath('//p[@id="page"]//a[re:test(text(),"下一页")]/@href').extract_first()
            if url_next is not None:
                # print('这是第%s页***********************************************')
                # 匹配到页码，只抓取10页以内的内容
                pattern_url = re.compile(r'&pn=(\d+)')
                page = pattern_url.findall(url_next)[0]
                if int(page) <= 90:
                    url_next = response.urljoin(url_next)
                    # print(url_next)
                    yield scrapy.Request(
                        url_next,
                        callback=self.parse
                    )

    #
    # def kwd_detail(self, response):
    #     print('YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY')
    #     keyword = response.meta['kwd']
    #     print(keyword)
    #     item = response.meta['item']
    #     detail_text = response.text
    #     for kwd in keyword.split(' '):
    #         if kwd in detail_text:
    #             item['wordPos'] = '4'
    #             print('关键字在详情页关键字在详情页关键字在详情页关键字在详情页关键字在详情页关键字在详情页关键字在详情页关键字在详情页')
    #             # print(item)
    #             break
    #     else:
    #         print('关键字也不再详情页关键字也不再详情页关键字也不再详情页关键字也不再详情页关键字也不再详情页关键字也不再详情页')
    #         # print(item)
    #         item['wordPos'] = '0'
    #     print('hehehhehehehehehehehehehehhehehehehehehehhe')
    #     print(item.get('wordPos'))
    #     yield item
