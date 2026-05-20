import pymysql

class Collection(object):
    def __init__(self, tablename=''):
        self.db = pymysql.connect(host='localhost', user='bilin', passwd='123456', port=3306, db='zhaobiao')
        self.table = tablename
        cursor = self.db.cursor()
        # cursor.execute("DROP TABLE IF EXISTS %s"%tablename)
        sqltext = """CREATE TABLE %s (
                     name  CHAR(200) NOT NULL,
                     href  TEXT NOT NULL,
                     date_y INT,  
                     date_m INT,  
                     date_d INT,  
                     area CHAR(200),
                     source CHAR(200),
                     city  CHAR(20) )"""%tablename
        try:
            cursor.execute(sqltext)
            self.db.commit()
        except:
            pass
        cursor.close()

    def insert_one(self, data):
        sql = """INSERT INTO `%s` (`name`, `href`, `date_y`, `date_m`, `date_d`, `area`, `source`, `city`)
                 VALUES ('%s', '%s', %s, %s, %s, '%s', '%s', '%s')"""%(self.table, data['name'],
                                                               data['href'],data['date_y'],
                                                               data['date_m'],data['date_d'], "",
                                                               data['source'], data['city'])
        cursor = self.db.cursor()
        cursor.execute(sql)
        self.db.commit()
        cursor.close()

    def count_documents(self, data):
        if "name" in data.keys():
            sql = """SELECT COUNT(*) 
                     FROM %s
                     WHERE name='%s'"""%(self.table, data['name'])
        else:
            sql = """SELECT COUNT(*) 
                     FROM %s
                     WHERE source='%s' AND href='%s'"""%(self.table, data['source'], data['href'])
        cursor = self.db.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()[0][0]
        cursor.close()
        return int(result)

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
    # db.insert_one(d)