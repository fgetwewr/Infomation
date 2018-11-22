import pymysql
from scrapy.utils.project import get_project_settings
settings = get_project_settings()


class CreateTable:
    def __init__(self):
        self.port = settings['MYSQL_PORT']
        self.host = settings['MYSQL_HOST']
        self.user = settings['MYSQL_USER']
        self.dbname = settings['MYSQL_DATABASE']
        self.password = settings['MYSQL_PASSWORD']

        self.db = pymysql.connect(host=self.host, port=self.port, user=self.user, db=self.dbname, password=self.password)
        self.cursor = self.db.cursor()
        # print(self.host, self.port, self.user, self.dbname, self.password)
        # print(self.db)
        # print(self.cursor)

    # def create_test(self):
    #     self.cursor.execute("drop table if exists Info")
    #     sql = """create table Info(
    #     id int primary key auto_increment,
    #     autoId char(17) not null,
    #     relateId char(17),
    #     sourceWeb varchar(240),
    #     title varchar(80),
    #     mediaName varchar(12),
    #     newAt varchar(20),
    #     info varchar(120),
    #     imageLogo varchar(120),
    #     brandWord varchar(10),
    #     wordPos char(1),
    #     unique key pn (sourceWeb))"""
    #     self.cursor.execute(sql)
    #     self.db.commit()

    def create_brand(self):
        """品牌词（主词）表"""
        self.cursor.execute("drop table if exists Brand")
        sql = """create table Brand (
        id int primary key auto_increment,
        brandName varchar(10) not null,
        totalCount int,
        post float,
        mid float,
        nega float,
        createdAt datetime,
        updatedAt datetime,
        note varchar(64)
        )"""
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            print(e)

    def create_media(self):
        """媒体信息表"""
        self.cursor.execute("drop table if exists Media")
        sql = """create table Media (
        id int primary key auto_increment,
        user int default 0,
        mediaName varchar(12),
        mediaType int,
        domain varchar(20),
        logoUrl Varchar(20),
        createdAt datetime,
        updatedAt datetime,
        note varchar(64))"""
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            print(e)

    def create_news(self):
        self.cursor.execute("drop table if exists News")

        sql = """create table News (
        id int primary key auto_increment,
        brandId int,
        title varchar(80),
        info varchar(120),
        newsLink varchar(255),
        newsAt datetime,
        logoType varchar(240),
        newsLogo varchar(240),
        mediaName varchar(20),
        fromSrc int,
        brandPos int,
        autoId char(17) not null,
        relateId char(17),
        createdAt datetime,
        updatedAt datetime,
        note varchar(64),
        unique key (newsLink, brandId))"""

        self.cursor.execute(sql)
        self.db.commit()

    def __del__(self):
        self.cursor.close()
        self.db.close()


if __name__ == '__main__':
    table = CreateTable()
    # table.create_test()
    # table.create_brand()
    # table.create_media()
    table.create_news()
