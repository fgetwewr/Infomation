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

    def __init__(self):
        super(InformationSpider, self).__init__()
        self.kwd_dict = {}

        # def __init__(self, base_url=base_url, *args, **kwargs):
        #     super(InformationSpider, self).__init__(*args, **kwargs)
        # self.start_urls = []

    def start_requests(self):
        base_url = 'https://www.baidu.com/s?ie=utf-8&cl=2&rtt=1&bsst=1&tn=news&word={}&pn=0'

        # 海底捞
        domian_url = 'https://www.baidu.com/s?wd=site:qq.com 海底捞&pn=30&ie=utf-8'
        # 三只松鼠

        # 连接数据库
        settings = get_project_settings()
        host = settings['MONGODB_HOST']
        port = settings['MONGODB_PORT']
        dbname = settings['MONGODB_DBNAME']
        sheetname = settings['MONGODB_KWDSHEET']
        myclient = pymongo.MongoClient(host=host, port=port)
        kwd_db = myclient[dbname]
        kwd_sheet = kwd_db[sheetname]
        yield scrapy.Request(url=domian_url, callback=self.domain_parse)

        # 查询数据库，获取关键字及对应id, 并构造请求start_url
        for kwd in kwd_sheet.find().limit(1):
            self.kwd_dict['{}'.format(kwd.get('name'))] = kwd.get('id')
            # self.start_urls.append(base_url.format(kwd.get('name')))
            url = base_url.format(kwd.get('name'))
            # print(kwd.get('name'))
            # yield scrapy.Request(url=url, callback=self.generic_parse)

    def generic_parse(self, response):
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

            # 对外暴露id
            rand_num = random.random() * 9000
            num = round(rand_num) + 1000
            timed = round(time.time() * 1000)
            item['autoId'] = str(num) + str(timed)

            # 通过判断response.meta['relateId']， 如果存在说明是从更多资讯传递过来的参数，否则按照正常逻辑执行
            try:
                relateId = response.meta['relateId']
                item['relateId'] = relateId
                # print('try%s' % item)
            except:
                item['relateId'] = ''
                # print('except%s' % item)

            # 判断是否有 "查看更多相关资讯"，如果有继续回调parse进行抓取
            more_info = info.xpath('.//span[@class="c-info"]/a[re:test(text(),".*?查看更多相关资讯.*?")]/@href').extract_first()
            if more_info:
                # print('----------------------------------------')
                # print('这是相关资讯里的内容')
                relateId = item['autoId']   # 设置relateId, 关联autoId， 并将其传递给回调函数
                more_info_url = response.urljoin(more_info)
                yield scrapy.Request(
                    url=more_info_url,
                    meta={'relateId': relateId},
                    callback=self.generic_parse,
                )

            # 获取网站链接
            item['sourceWeb'] = info.xpath('./h3[@class="c-title"]/a/@href').extract_first()

            # 获取标题
            title_html = info.xpath('./h3[@class="c-title"]/a').extract_first()
            pattern1 = re.compile(r'target="_blank">(.*?)</a>', re.S)
            title = pattern1.findall(title_html)
            item['title'] = re.sub(r'<em>|</em>', '', title[0]).strip()

            content = info.xpath('.//div').extract_first()       # 先得到含有内容的Html
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
                item['imageLogo'] = ''

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
                    self.logger.info('超时，请求详情页%s' % e)

            item['main_url'] = response.url
            yield item

        # # 获取下一页链接
        # url_next = response.xpath('//p[@id="page"]//a[re:test(text(),"下一页")]/@href').extract_first()
        # if url_next is not None:
        #     # print('这是第%s页***********************************************')
        #     # 匹配到页码，只抓取10页以内的内容
        #     pattern_url = re.compile(r'&pn=(\d+)')
        #     page = pattern_url.findall(url_next)[0]
        #     if int(page) <= 90:
        #         url_next = response.urljoin(url_next)
        #         # print(url_next)
        #         yield scrapy.Request(
        #             url_next,
        #             callback=self.generic_parse
        #         )

    def domain_parse(self, response):
        print('这是域名关键字')
        # from scrapy.shell import inspect_response
        # inspect_response(response, self)

        # 获取请求url，正则匹配到关键字，解码， 得到域名及关键字列表
        url = response.url
        kwd_encode = re.compile(r'\?wd=(.*?)&').findall(url)
        keyword_init = urllib.parse.unquote(kwd_encode[0])
        keyword = re.sub(r'\+', ' ', keyword_init).split(' ')

        # 获取当前页面资讯列表
        info_list = response.xpath('//div[@id="content_left"]/div[@class="result c-container "]')
        # print(info_list)
        for info in info_list:
            item = InfomationItem()

            # 对外暴露id
            rand_num = random.random() * 9000
            num = round(rand_num) + 1000
            timed = round(time.time() * 1000)
            item['autoId'] = str(num) + str(timed)

            # 媒体
            item['mediaName'] = keyword[0]

            # 获取网站链接
            item['sourceWeb'] = info.xpath('./h3[@class="t"]/a/@href').extract_first()

            # 获取标题
            title_html = info.xpath('./h3[@class="t"]/a').extract_first()
            pattern1 = re.compile(r'target="_blank".*?>(.*?)</a>', re.S)
            title = pattern1.findall(title_html)
            item['title'] = re.sub(r'<em>|</em>', '', title[0]).strip()

            # 获取含有时间，内容 标签
            content = info.xpath('.//div').extract_first()
            # 获取时间
            # 获取格式为 xx年xx月xx日
            pattern_date= re.compile(r'<span class=" newTimeFactor_before_abs m">(\d+年\d+月\d+日).*?</span>')
            date = pattern_date.findall(content)
            # 获取格式为 xx天前
            pattern_days = re.compile(r'<span class=" newTimeFactor_before_abs m">(\d+)天前.*?</span>')
            days = pattern_days.findall(content)
            # 获取格式为 xx小时前
            pattern_hour = re.compile(r'<span class=" newTimeFactor_before_abs m">(\d+)小时前.*?</span>')
            hours = pattern_hour.findall(content)
            # 获取格式为 xx分钟前
            pattern_minute = re.compile(r'<span class=" newTimeFactor_before_abs m">(\d+)分钟前.*?</span>')
            minutes = pattern_minute.findall(content)
            if date:
                item['newAt'] = date[0]
            elif days:
                p_days = (datetime.datetime.now() + datetime.timedelta(days=-int(days[0]))).strftime('%Yn%my%dr %H:%M')
                item['newAt'] = p_days.replace('n', '年').replace('y', '月').replace('r', '日')
            elif hours:
                p_hours = (datetime.datetime.now() + datetime.timedelta(days=-int(hours[0]))).strftime('%Yn%my%dr %H:%M')
                item['newAt'] = p_hours.replace('n', '年').replace('y', '月').replace('r', '日')
            elif minutes:
                p_minutes = (datetime.datetime.now() + datetime.timedelta(days=-int(minutes[0]))).strftime('%Yn%my%dr %H:%M')
                item['newAt'] = p_minutes.replace('n', '年').replace('y', '月').replace('r', '日')
            else:
                item['newAt'] = ''

            # 获取内容,分三种情况，
            pattern_info1 = re.compile(r'<div class="c-abstract">(.*?)</div>', re.S)
            text1 = pattern_info1.findall(content)
            if text1:
                pattern_info2 = re.compile(r'<span .*?</span>(.*)', re.S)
                text2 = pattern_info2.findall(text1[0])
                print('text1%s' % text1[0])
                print('text2%s' % text2)
                if text2:
                    item['info'] = re.sub(r'<em>|</em>', '', text2[0].strip())
                else:
                    item['info'] = re.sub(r'<em>|</em>', '', text1[0].strip())
            else:
                print(content)
                print('*********************')
                pattern_info3 = re.compile(r'<span>视频</span>.*?</p><p>(.*?)</p><div class="g">', re.S)
                text3 = pattern_info3.findall(content)
                item['info'] = re.sub(r'<em>|</em>', '', text3[0].strip())
                print('text3%s' % text3)


            print(item)



            # '      <div class="c-abstract"><span class=" newTimeFactor_before_abs m">.*?</span>(.*?)<em>...</em></div>'
            # '      <div class="c-abstract"><span class=" newTimeFactor_before_abs m">.*?</span>(.*?)</div>'
            # 获取图片或视频链接

            # 对应关键字id

            # 判断关键字是否在标题或内容


            # 获取下一页链接


