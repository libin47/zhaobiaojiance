from sqlalchemy import Column, String, create_engine, DateTime, Integer, Boolean
from sqlalchemy.orm import declarative_base
from .base import engine, DBSession, Base, DBBase


class ZhaoBiaoBG(Base):
    __tablename__ = 'zhaobiao_biangeng'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))  # 项目名称
    href = Column(String(500))  # 页面地址
    date = Column(DateTime)  # 发布日期

    title = Column(String(100), default="")  # 标题，例如什么什么公告
    money = Column(String(20), default="")  # 预算金额
    city = Column(String(20))  # 城市，地市
    area = Column(String(20), default="")  # 地区，县区
    address = Column(String(100), default="")  # 地址

    people = Column(String(50))  # 招标人
    source = Column(String(20))  # 来源，直接来源网站
    source_base = Column(String(20))  # 二级来源，二级来源网站，例如采购网上标注来自【公共服务资源】的，应填【公共服务资源】
    send = Column(Boolean, default=False)  # 是否已发送



class DB_ZBBG(DBBase):
    def insert_one(self, d):
        self.db.add(ZhaoBiaoBG(**d))

    def insert_one_check(self, d):
        if self.count_name_time(d["name"], d['date']) == 0:
            self.insert_one(d)

    def count_name(self, data):
        return self.db.query(ZhaoBiaoBG).filter(ZhaoBiaoBG.name==data).count()

    def count_name_time(self, name, time):
        # 检查同一标题的相同发布日期，可依此判断此条数据是否已重复（不同网站之间亦可）
        return self.db.query(ZhaoBiaoBG).filter(ZhaoBiaoBG.name==name, ZhaoBiaoBG.date==time).count()

    def count_source_href(self, source, href):
        # 检查同一来源的相同链接，可依此判断此网页的爬取是否已重复
        return self.db.query(ZhaoBiaoBG).filter(ZhaoBiaoBG.source==source, ZhaoBiaoBG.href==href).count()

    def find_no_send(self, city):
        return self.db.query(ZhaoBiaoBG).filter(ZhaoBiaoBG.send==False, ZhaoBiaoBG.city==city).all()

    def close(self):
        self.db.close()