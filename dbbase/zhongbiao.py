from sqlalchemy import Column, String, create_engine, DateTime, Integer, Boolean
from sqlalchemy.orm import declarative_base
from .base import engine, DBSession, Base, DBBase


class ZhongBiao(Base):
    __tablename__ = 'zhongbiao'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100)) # 项目名称
    nameBag = Column(String(200)) # 项目名称（包）
    href = Column(String(500)) # 页面地址
    date = Column(DateTime) # 发布日期
    info = Column(String(500)) # 项目内容

    title = Column(String(100), default="") # 标题，例如什么什么公告
    code = Column(String(100), default="") # 招标编号
    money = Column(String(20), default="") # 预算金额
    city = Column(String(20), default="") # 城市，地市
    area = Column(String(20), default="") # 地区，县区
    address = Column(String(100), default="") # 地址

    classify = Column(String(100), default="") # 行业
    purchaseName = Column(String(100), default="") # 中标、单一来源、废标
    type = Column(String(100), default="") # 类别，货物、工程、服务

    people = Column(String(50), default="") # 招标人
    candidate = Column(String(100), default="") # 中标候选人
    winner = Column(String(100), default="") # 中标人（最终中标单位）
    winnerAddress = Column(String(100), default="") # 中标人地址

    source = Column(String(20)) # 来源，直接来源网站
    source_base = Column(String(20))  # 二级来源，二级来源网站，例如采购网上标注来自【公共服务资源】的，应填【公共服务资源】
    send = Column(Boolean, default=False) # 是否已发送



class DB_ZhongB(DBBase):
    def insert_one(self, d):
        self.db.add(ZhongBiao(**d))

    def insert_one_check(self, d):
        if self.count_name_time(d["name"], d['date']) == 0:
            self.insert_one(d)

    def count_name(self, data):
        return self.db.query(ZhongBiao).filter(ZhongBiao.name==data).count()

    def count_name_time(self, name, time):
        # 检查同一标题的相同发布日期，可依此判断此条数据是否已重复（不同网站之间亦可）
        return self.db.query(ZhongBiao).filter(ZhongBiao.name==name, ZhongBiao.date==time).count()

    def count_source_href(self, source, href):
        # 检查同一来源的相同链接，可依此判断此网页的爬取是否已重复
        return self.db.query(ZhongBiao).filter(ZhongBiao.source==source, ZhongBiao.href==href).count()

    def find_no_send(self, city):
        return self.db.query(ZhongBiao).filter(ZhongBiao.send==False,ZhongBiao.city==city).all()

    def close(self):
        self.db.close()


    def batch_update_send_true(self, ids):
        if not ids:
            return
        self.db.query(ZhongBiao) \
            .filter(ZhongBiao.id.in_(ids)) \
            .update({ZhongBiao.send: True}, synchronize_session=False)
        self.db.commit()