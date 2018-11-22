import requests
import re
import time
import random
import datetime
import pymysql
import urllib
from urllib import parse
import scrapy
from Infomation.items import InfomationItem
from scrapy.utils.project import get_project_settings

settings = get_project_settings()

# import logging
#
# logger = logging.getLogger(__name__)


class InformationSpider(scrapy.Spider):
    name = 'info'
    # allowed_domains = ['www.baidu.com']

    def __init__(self):
        super(InformationSpider, self).__init__()

        # 连接数据库
        self.port = settings['MYSQL_PORT']
        self.host = settings['MYSQL_HOST']
        self.user = settings['MYSQL_USER']
        self.dbname = settings['MYSQL_DATABASE']
        self.password = settings['MYSQL_PASSWORD']
        self.db = pymysql.connect(host=self.host, port=self.port, user=self.user, db=self.dbname, password=self.password)
        self.cursor = self.db.cursor()

        self.brand_dict = {}
        self.media_dict = {}

    def start_requests(self):
        # 百度新闻资讯
        # base_url = 'https://www.baidu.com/s?ie=utf-8&cl=2&rtt=1&bsst=1&tn=news&word={}&pn=0'
        brand_sql = "select * from brand;"
        self.cursor.execute(brand_sql)
        brand_result = self.cursor.fetchall()
        print(brand_result)
        for brand in brand_result:
            print(brand)
            self.brand_dict['{}'.format(brand[1])] = brand[0]
            brand_url = 'https://www.baidu.com/s?ie=utf-8&cl=2&rtt=1&bsst=1&tn=news&word={}&pn=0'.format(brand[1])
            # yield scrapy.Request(url=brand_url, callback=self.brand_parse)

        # 查询数据库，获取关键字及对应id, 并构造请求start_url
        # for kwd in kwd_sheet.find().limit(2):
        #     self.kwd_dict['{}'.format(kwd.get('name'))] = kwd.get('id')
        #     # self.start_urls.append(base_url.format(kwd.get('name')))
        #     url = base_url.format(kwd.get('name'))
        #     # print(kwd.get('name'))
        #     yield scrapy.Request(url=url, callback=self.generic_parse)

        # 百度网页新闻
        # domian_url = 'https://www.baidu.com/s?wd=site:{} {}&pn=0&ie=utf-8'
        media_sql = 'select * from media;'
        self.cursor.execute(media_sql)
        media_result = self.cursor.fetchall()
        for media in media_result:
            self.media_dict['{}'.format(media[4])] = media[2]
            for brand in brand_result:
                media_url = 'https://www.baidu.com/s?wd=site:{} {}&pn=0&ie=utf-8'.format(media[4], brand[1])
                yield scrapy.Request(url=media_url, callback=self.domain_parse)

    def brand_parse(self, response):
        # scrapy shell调试使用
        # if item['title'] == '今晚十点,我们要公布一件事情':
        #     from scrapy.shell import inspect_response
        #     inspect_response(response, self)

        # 获取请求url，正则匹配到关键字，解码
        url = response.url
        kwd_encode = re.compile(r'&word=(.*?)&').findall(url)
        keyword = urllib.parse.unquote(kwd_encode[0])
        # keyword = re.sub(r'\+', ' ', keyword_init)
        print("{{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{")
        print(self.brand_dict)
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
                    callback=self.brand_parse,
                )

            # 获取网站链接
            item['newsLink'] = info.xpath('./h3[@class="c-title"]/a/@href').extract_first()

            # 获取标题
            title_html = info.xpath('./h3[@class="c-title"]/a').extract_first()
            pattern1 = re.compile(r'target="_blank">(.*?)</a>', re.S)
            title = pattern1.findall(title_html)
            item['title'] = re.sub(r'<em>|</em>', '', title[0]).strip()

            content = info.xpath('.//div').extract_first()       # 先得到含有内容的Html
            # 获取时间，媒体
            # 获得媒体
            # pattern_media1 = re.compile(r'<p class="c-author">(\w+).*?</p>', re.S)
            # pattern_media2 = re.compile(r'<img class="source-icon".*?>(\w+).*?</p>', re.S)
            media = info.xpath('.//p[@class="c-author"]/text()').extract()
            if media[-1]:
                pattern_media = re.compile(r'(\w+).*?').findall(media[-1])
                item['mediaName'] = pattern_media[0]
            else:
                item['mediaName'] = ''
            # print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
            # print(media)
            # print('extract', media.extract())
            # print('extract_first', media.extract_first())
            # print(pattern_media)

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
                date = date[0].replace('年', '-').replace('月', '-').replace('日', '')
                item['newsAt'] = date
            elif hours:
                p_hours = (datetime.datetime.now() + datetime.timedelta(hours=-int(hours[0]))).strftime('%Y-%m-%d %H:%M:%S')
                # item['newsAt'] = p_hours.replace('n', '年').replace('y', '月').replace('r', '日')
                item['newsAt'] = p_hours
            elif minutes:
                p_minutes = (datetime.datetime.now() + datetime.timedelta(minutes=-int(minutes[0]))).strftime('%Y-%m-%d %H:%M:%S')
                # item['newsAt'] = p_minutes.replace('n', '年').replace('y', '月').replace('r', '日')
                item['newsAt'] = p_minutes
            # 获取内容
            pattern_info = re.compile(r'<p class="c-author">.*?</p>(.*?)<span class="c-info">', re.S)
            text = pattern_info.findall(content)
            item['info'] = re.sub(r'<em>|</em>', '', text[0]).strip()

            # 获取图片
            image = info.xpath(r'.//div[@class="c-span6"]/a[@class]/img/@src').extract_first()
            if image is not None:
                item['newsLogo'] = image
                item['logoType'] = '1'      # 新闻Logo对应类型，0: 无(默认),1: 图片地址, 2：视频地址
            else:
                item['newsLogo'] = ''
                item['logoType'] = '0'

            # 对应关键字id
            item['brandId'] = self.brand_dict.get(keyword)

            # 判断关键字是否在标题或内容里面
            if (keyword in item['title']) and (keyword in item['info']):
                item['brandPos'] = '3'
            elif keyword in item['title']:
                item['brandPos'] = '1'
            elif keyword in item['info']:
                item['brandPos'] = '2'
            # 判断关键字是否存在于详情页内容里
            else:
                # 通过requests.get()请求单条资讯url,判断关键字是否在内容里面
                try:
                    resp = requests.get(url=item['newsLink'], timeout=5).text
                    if keyword in resp:
                        item['brandPos'] = '2'
                        break
                    else:
                        item['brandPos'] = '0'
                except Exception as e:
                    # print(e)
                    item['brandPos'] = '0'
                    print(item)
                    self.logger.info('超时，请求详情页%s' % e)

            item['fromSrc'] = '1'       # 抓取来源 1: 百度新闻资讯抓取,2: 百度网页抓取，3: 今日头条抓取
            item['createdAt'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')     # 创建时间
            item['updatedAt'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')     # 更新时间

            yield item

        # 获取下一页链接
        url_next = response.xpath('//p[@id="page"]//a[re:test(text(),"下一页")]/@href').extract_first()
        if url_next is not None:
            # print('这是第%s页***********************************************')
            # 匹配到页码，只抓取10页以内的内容
            pattern_url = re.compile(r'&pn=(\d+)')
            page = pattern_url.findall(url_next)[0]
            if int(page) <= 90:
                url_next = response.urljoin(url_next)
                yield scrapy.Request(
                    url_next,
                    callback=self.brand_parse
                )

    def domain_parse(self, response):
        print('这是域名关键字')
        # from scrapy.shell import inspect_response
        # inspect_response(response, self)

        # 获取请求url，正则匹配到关键字，解码， 得到域名及关键字列表
        url = response.url
        kwd_encode = re.compile(r'\?wd=(.*?)&').findall(url)
        keyword_init = urllib.parse.unquote(kwd_encode[0])
        print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
        print(keyword_init)
        keyword = re.sub(r'\+', ' ', keyword_init).replace('site:', '').split(' ')
        print(keyword)

        # print(response.text)
        with open('baidu.html', 'a', encoding='utf8') as f:
            f.write(response.text)

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
            item['mediaName'] = self.media_dict[keyword[0]]

            # 获取网站链接
            item['newsLink'] = info.xpath('./h3[@class="t"]/a/@href').extract_first()

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
                date = date[0].replace('年', '-').replace('月', '-').replace('日', '')
                item['newsAt'] = date
            elif days:
                p_days = (datetime.datetime.now() + datetime.timedelta(days=-int(days[0]))).strftime('%Yn%my%dr %H:%M:%S')
                # item['newAt'] = p_days.replace('n', '年').replace('y', '月').replace('r', '日')
                item['newsAt'] = p_days
            elif hours:
                p_hours = (datetime.datetime.now() + datetime.timedelta(days=-int(hours[0]))).strftime('%Yn%my%dr %H:%M:%S')
                # item['newAt'] = p_hours.replace('n', '年').replace('y', '月').replace('r', '日')
                item['newsAt'] = p_hours
            elif minutes:
                p_minutes = (datetime.datetime.now() + datetime.timedelta(days=-int(minutes[0]))).strftime('%Yn%my%dr %H:%M:%s')
                # item['newAt'] = p_minutes.replace('n', '年').replace('y', '月').replace('r', '日')
                item['newsAt'] = p_minutes
            else:
                item['newsAt'] = ''

            # 获取内容,分三种情况，
            pattern_info1 = re.compile(r'<div class="c-abstract">(.*?)</div>', re.S)
            text1 = pattern_info1.findall(content)
            if text1:
                pattern_info2 = re.compile(r'<span .*?</span>(.*)', re.S)
                text2 = pattern_info2.findall(text1[0])
                if text2:
                    item['info'] = re.sub(r'<em>|</em>', '', text2[0].strip())
                else:
                    item['info'] = re.sub(r'<em>|</em>', '', text1[0].strip())
            else:
                pattern_info3 = re.compile(r'<span>视频</span>.*?</p><p><span class=" newTimeFactor_before_abs m">.*?</span>(.*?)</p><div class="g">', re.S)
                text3 = pattern_info3.findall(content)
                if text3:
                    item['info'] = re.sub(r'<em>|</em>', '', text3[0].strip())
                else:
                    pattern_info4 = re.compile(r'<span>视频</span>.*?<p>(.*?)</p><div class="g">', re.S)
                    print('|||||||||||||||||||||||||||||||||||')
                    print(content)
                    text4 = pattern_info4.findall(content)
                    print(text4)
                    item['info'] = re.sub(r'<em>|</em>', '', text4[0].strip())

            # 获取图片
            image1 = info.xpath(r'.//a[@class="c-img6"]/img/@src').extract_first()      # 普通图片
            image2 = info.xpath(r'./div/a/img/@src').extract_first()                    # 视频图片
            if image1:
                item['newsLogo'] = image1
                item['logoType'] = '1'
            elif image2:
                item['newsLogo'] = image2
                item['logoType'] = '2'
            else:
                item['newsLogo'] = ''
                item['logoType'] = '0'

            # 对应关键字id
            item['brandId'] = self.brand_dict.get(keyword[1])

            # 判断关键字是否在标题或内容
            if keyword[1] in item['title'] and keyword[1] in item['info']:
                item['brandPos'] = '3'
            elif keyword[1] in item['title']:
                item['brandPos'] = '1'
            elif keyword[1] in item['info']:
                item['brandPos'] = '2'
            else:
                # 通过requests.get()请求单条资讯url, 判断关键字是否在内容里面
                try:
                    resp = requests.get(url=item['newsLink'], timeout=5).text
                    if keyword[1] in resp:
                        item['brandPos'] = '2'
                    else:
                        item['brandPos'] = '0'
                except Exception as e:
                    item['brandPos'] = '0'
                    self.logger.info('超时， 请求详情页%s' % e)

            item['fromSrc'] = '2'       # 抓取来源 1: 百度新闻资讯抓取,2: 百度网页抓取，3: 今日头条抓取
            item['createdAt'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 创建时间
            item['updatedAt'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 更新时间

            yield item
        # 获取下一页链接
        url_next = response.xpath('//div[@id="page"]/a[re:test(text(),"下一页")]/@href').extract_first()
        if url_next:
            # 匹配到页码，之抓取10页以内的内容
            pattern_url = re.compile(r'&pn=(\d+)')
            page = pattern_url.findall(url_next)[0]
            if int(page) <= 90:
                url_next = response.urljoin(url_next)
                yield scrapy.Request(
                    url=url_next,
                    callback=self.domain_parse
                )

