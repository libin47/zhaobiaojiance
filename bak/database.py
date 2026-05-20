from config import env



def getdb():
    if env == "master":
        import database_mysql
        return database_mysql.getdb()
    else:
        import database_mongo
        return database_mongo.getdb()


def getdb_yx():
    if env == "master":
        import database_mysql
        return database_mysql.getdb_yx()
    else:
        import database_mongo
        return database_mongo.getdb_yx()

