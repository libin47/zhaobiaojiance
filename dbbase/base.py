import os
from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.getcwd() + os.path.sep + "sqlite.db"

# 初始化数据库连接
engine = create_engine(SQLALCHEMY_DATABASE_URI)
# 定义基类
Base = declarative_base()
# Base.metadata.create_all(engine)
# 创建 DBSession 类型
DBSession = sessionmaker(bind=engine)

class DBBase():
    def __init__(self):
        Base.metadata.create_all(engine)
        self.db = DBSession()

    def __enter__(self):
        self.db = DBSession()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.db.rollback()
        else:
            self.db.commit()
        self.db.close()
        return False  # 不吞掉异常

