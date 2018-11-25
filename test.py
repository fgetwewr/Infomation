import re
import json
import datetime

t = datetime.datetime.now()
y = datetime.timedelta(seconds=-58)
y2 = datetime.timedelta(minutes=-10)
y3 = datetime.timedelta(days=120)
s = y + t
s2 = y2 + t
s3 = y3 + t

print(t)
print(y)
print(s)
print(s2)
print(s3)


#
# string1 = '星界游神巴德掌控星空之力的强大辅助 LOL新英雄星界游神巴德即将...'
# string2 = '星界游神巴德掌控星空媒体之力的强大辅助 LOL新英雄星界游神巴德即将...'
# s = '星空媒体'
# if s in string1:
#     print('在1')
# if s in string2:
#     print('在2')
#
# b = '百家号\xa0\xa0\t\t\t\t\n\t\t\t\t\t\t2018年10月14日 08:02\n\t\t\t'
# c = '百家号\xa0\xa0\t\t\t\t\n\t\t\t\t\t\t1分钟前\n\t\t\t'
# d = '百家号\xa0\xa0\t\t\t\t\n\t\t\t\t\t\t1小时前\n\t\t\t'


# a = ["\n      心理测试:哪一幅<em>星空</em>图最美?测出你的心累指数!\n    "]
# c = a[0]
# d = c.strip('').replace('<em>', '').replace('</em>', '')
# s = re.sub('<em>|</em>', '', c).strip()
# s = b.split()
# c = s[1] + s[-1]
# print(c)
# print(s)

# s = ''.join(b[0].split())
# s = '2018-11-07 01:53'
# ss = re.sub(r'-', '年', s)
# print(ss)
# now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
# print(now_time)
# print(datetime.datetime.now() + datetime.timedelta(hours=-1))
# print(datetime.datetime.now() + datetime.timedelta(hours=-1))

# p_hours = (datetime.datetime.now() + datetime.timedelta(hours=-2)).strftime('%Yn%my%dr %H:%M')
# print(p_hours)
# itdate'] = p_hours.replace('n', '年').replace('y', '月').replace('r', '日')
# print(date)
import urllib
# import urllib
# from urllib import parse
#
# print(urllib.parse.unquote('%E4%B8%89%E5%8F%AA%E6%9D%BE%E9%BC%A0'))


# (random()* 9000 + 1000) + ''

# import random
# import time
# rand_num = random.random() * 9000
# num = round(rand_num) + 1000
# timed = round(time.time()*1000)
# n = str(num) + str(timed)
# print(n)

# s = '三只松鼠+霉变'
# s2 = s.split('+')
# print(s2)
# if isinstance('三', s2):
#     print('jag')


# for i in range(3):
#     if '三' in s:
#         print('zai')
#         break
# else:
#     print('heheh')


# title = '2016年最热销10款零食6款上黑榜:三只松鼠百草味在列'
# info = '更引人注意的其次则是三只松鼠、百草味、良品铺子...5.如果吃到霉变、发苦的坚果,应立即吐掉,并用清水...'
# keyword = '三只松鼠+霉变'
# for kwd in keyword.split('+'):
#     if (kwd in title) and (kwd in info):
#         print('都在')
#         break
#     elif kwd in title:
#         print('在标题')
#         break
#     elif kwd in info:
#         print('在内容')
#         break
# else:
#     print('都不在')
# from pymongo.cursor import Cursor
# from scrapy.utils.project import get_project_settings
# import pymongo
# # from pymongo import cursor
#
# settings = get_project_settings()
#
# host = settings["MONGODB_HOST"]
# port = settings["MONGODB_PORT"]
# dbname = settings["MONGODB_DBNAME"]
# sheetname = settings['MONGODB_KWDSHEET']
# myclient = pymongo.MongoClient(host=host, port=port)
# db = myclient[dbname]
# kwd_sheet = db[sheetname]


# print('11111111111111111111')
# url = 'https://www.baidu.com/s?ie=utf-8&cl=2&rtt=1&bsst=1&tn=news&word={}&pn=0'
# kwd_list = []
# for kwd in kwd_sheet.find():
#     print(kwd)
#     kwd_list.append(kwd.get('name'))
# print(kwd_list)

#
# kwd_dict = {}
# kwd_list = []
# for kwd in kwd_sheet.find():
#     kwd_list.append(kwd.get('name'))
    # kwd_dict['{}'.format(kwd.get('name'))] = kwd.get('id')

# url = 'https://www.baidu.com/s?ie=utf-8&cl=2&rtt=1&bsst=1&tn=news&word={}&pn=0'
# start_urls = [url.format(kwd) for kwd in kwd_list]
# print(start_urls)
# for x in range(100):

# kwd = kwd_sheet.find({'id': {'$gt': 2}})
# kwd = kwd_sheet.find().batch_size(2)
# print(kwd[1])
# cursor = kwd_sheet.find()
# # cursor.hasNext()
# ent = cursor[:]
# print(ent)
# for value in ent:
#     print(value)
# import datetime
# hours[0] = 7
# p_hours = (datetime.datetime.now() + datetime.timedelta(days=-(hours[0]))).strftime('%Yn%my%dr %H:%M')
# item['newAt'] = p_hours.replace('n', '年').replace('y', '月').replace('r', '日')


# import pymysql
# from scrapy.utils.project import get_project_settings
#
# settings = get_project_settings()
# port = settings['MYSQL_PORT']
# host = settings['MYSQL_HOST']
# user = settings['MYSQL_USER']
# dbname = settings['MYSQL_DATABASE']
# password = settings['MYSQL_PASSWORD']
#
# db = pymysql.connect(host=host, port=port, user=user, db=dbname, password=password)
# cursor = db.cursor()
#
# brand_sql = """select * from media;"""
# cursor.execute(brand_sql)
# result = cursor.fetchall()
# print(result)
# for i in result:
#     print(i)


# print(result[0][0], result[0][1])
# print(result[1][0], result[1][1])
# print(result[2][0], result[2][1])



# cursor.execute("drop table if exists Info")
#
# sql = """create table Info(
# id int primary key auto_increment,
# autoId char(17) not null,
# relateId char(17),
# sourceWeb varchar(240),
# title varchar(80),
# mediaName varchar(12),
# newAt varchar(20),
# info varchar(120),
# imageLogo varchar(120),
# brandWord varchar(10),
# wordPos char(1),
# unique key pn (sourceWeb))"""
# cursor.execute(sql)

# data = {
# 	"autoId" : "66001542678902826",
# 	"relateId" : "64121542678899349",
# 	"sourceWeb" : "http://finance.sina.com.cn/stock/s/2018-11-20/doc-ihmutuec1819309.shtml",
# 	"title" : "千山药机董秘因个人原因 此前曾表示对三季报不负责",
# 	"mediaName" : "新浪",
# 	"newAt" : "2018年11月20日 09:17",
# 	"info" : "千山药机董秘因“个人原因”辞职此前曾表示对三季报不负责上周五晚间,千山药机(300216)发布公告:公司副总经理、董秘陈龙晖因个人原因申请辞职。值得一提的是,就...",
# 	"imageLogo" : "https://ss2.baidu.com/6ONYsjip0QIZ8tyhnq/it/u=2448508487,3224046481&fm=55&app=22&f=GIF?w=121&h=81",
# 	"brandWord" : "3",
# 	"wordPos" : 0}
# keys = ','.join(data.keys())
# print(keys)
# values = ','.join(['%s']*len(data))
# print(values)
# print('*'*90)
# sql = "insert into Info(%s) values (%s)" % (keys, values)
# cursor.execute(sql, [v for k, v in data.items()])
# db.commit()
# #
# # db.commit()
# cursor.close()
# db.close()

# import time
# import datetime
# print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') )



