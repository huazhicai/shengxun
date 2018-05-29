#!/usr/bin/ python

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text

# 初始化数据库连接:
engine = create_engine("mysql+pymysql://root:110@localhost:3306/huludb?charset=utf8")

Session = sessionmaker(bind=engine)

Base = declarative_base()


class News(Base):
    ''' 新闻类型 '''

    __tablename__ = 'news'
    id = Column(Integer, primary_key=True)
    title = Column(String(128), nullable=False)
    content = Column(Text, nullable=False)
    types = Column(String(32), nullable=False)
    image = Column(String(300))
    author = Column(String(64))
    view_count = Column(Integer)
    created_at = Column(DateTime)
    is_valid = Column(Boolean)

    def __repr__(self):
        return "<News {}>".format(self.title)


class MysqlOrmTest(object):
    def __init__(self):
        self.session = Session()

    def add_one(self):
        ''' 添加数据 '''

        new_obj = News(
                title='ORM标题',
                content='content',
                types="百家"
        )
        self.session.add(new_obj)
        self.session.commit()
        return new_obj

    def get_one(self):
        return self.session.query(News).get(1)

    def get_more(self):
        return self.session.query(News).filter_by(is_valid=1)

    def update_data(self):
        obj = self.session.query(News).get(1)
        obj.is_valid = 0
        self.session.add(obj)
        self.session.commit()
        return obj

    def delete_data(self):
        data = self.session.query(News).get(3)
        self.session.delete(data)
        self.session.commit()


def main():
    obj = MysqlOrmTest()
    # rest = obj.add_one()
    # print(dir(rest))
    # print(obj.get_one().title)

    # print(obj.get_more().count())
    # for row in obj.get_more():
    #     print(row.title)

    # print(obj.update_data())

    obj.delete_data()


if __name__ == '__main__':
    main()
