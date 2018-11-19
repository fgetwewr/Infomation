import pymongo
from scrapy.utils.project import get_project_settings


settings = get_project_settings()
host = settings["MONGODB_HOST"]
port = settings["MONGODB_PORT"]
dbname = settings["MONGODB_DBNAME"]

client = pymongo.MongoClient(host=host, port=port)
# 链接数据库
db = client[dbname]

# ids 创建数据库集合
ids = db['ids']


# 自增函数
def getNextValue(name):
    ret = ids.find_and_modify({'_id': name}, {'$inc': {'sequence_value': 1}}, safe=True, new=True)
    new = ret['sequence_value']
    return new


if __name__ == '__main__':
    # 执行前先运行，实现增id 的归零
    ids.insert_one(({'_id': 'productid', 'sequence_value': 0}))
    print('初始化Id成功')
