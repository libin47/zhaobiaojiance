from sqlalchemy import Column, String, create_engine, DateTime, Integer, Boolean
from sqlalchemy.orm import declarative_base
from .base import engine, DBSession, Base, DBBase


class LogError(Base):
    __tablename__ = 'log_error'
    id = Column(Integer, primary_key=True, autoincrement=True)
    log_time = Column(DateTime) # 记录时间
    source = Column(String(50)) # 来源网站
    craw_type = Column(String(50)) # 爬取类型
    craw_url = Column(String(500)) # 爬取地址
    log_type = Column(String(50)) # 日志类型
    log_text = Column(String(5000)) # 日志内容
    send = Column(Boolean, default=False) # 是否已发送



class DB_Log(DBBase):
    def insert_one(self, d):
        self.db.add(LogError(**d))

    def find_no_send(self, city):
        return self.db.query(LogError).filter(LogError.send==False).all()

    def close(self):
        self.db.close()