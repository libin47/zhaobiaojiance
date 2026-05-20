import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017")
db = myclient['zhaobiao']
# collection = db['zhaobiao']
# collection_yx = db['zhaobiao_yixiang']

class DB(object):
    def close(self):
        pass

class Collection(object):
    def __init__(self, tablename=''):
        self.db = DB()
        self.coll = db[tablename]

    def insert_one(self, data):
        return self.coll.insert_one(data)

    def count_documents(self, data):
        return self.coll.count_documents(data)


def getdb():
    return Collection("zhaobiao")

def getdb_yx():
    return Collection("zhaobiao_yixiang")


if __name__=='__main__':
    d = {
        "name": '测试',
        "href": '测试',
        "date_y": 2000,
        "date_m": 1,
        "date_d": 1,
        "area": '测试',
        "source": "test",
        "city": 'test'
    }
    db = getdb()
    db.insert_one(d)