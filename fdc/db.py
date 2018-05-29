# -*- coding: utf-8 -*-
from peewee import *

# db = SqliteDatabase('pc58.db', **{})
# conn = psycopg2.connect(database="test", user="postgres", password="sdf")
psql_db = PostgresqlDatabase('58fdc', user='postgres', password="sdf")


class UnknownField(object):
    pass


class BaseModel(Model):
    class Meta:
        database = psql_db


class Baseurls(BaseModel):
    url = CharField(primary_key=True)
    city = CharField(null=True)
    isget = CharField()
    name = CharField(null=True)
    timenow = CharField(null=True)

    class Meta:
        db_table = 'baseurls'


class Purls(BaseModel):
    url = CharField(primary_key=True)
    city = CharField(null=True)
    isget = CharField()
    badtimes = CharField()
    name = CharField(null=True)
    timenow = CharField(null=True)

    class Meta:
        db_table = 'purls'


class City(BaseModel):
    name = CharField(primary_key=True)
    nameb = CharField(null=True, unique=True)

    class Meta:
        db_table = 'city'


class Fdcz(BaseModel):
    '''房地产总'''
    incname = CharField(primary_key=True)  # 企业名
    city = CharField(null=True)  # 城市
    region = CharField()  # 城区
    area = CharField()  # 地区
    address = CharField()  # 地址
    incproperty = CharField()  # 企业性质
    incontact = TextField()  # 企业联系人
    contactname = CharField()  # 招聘联系人
    incowner = CharField()  # 法人
    phone = CharField(null=True)  # 电话
    weal = CharField()  # 福利
    abstract = CharField()  # 简介
    longz = CharField()  # 纬度
    lat = CharField()  # 经度
    job = CharField()  # 职位
    money = CharField()  # 薪资
    trade = CharField()  # 行业
    claim = CharField()  # 要求
    scale = CharField()  # 规模
    timenow = CharField(null=True)

    class Meta:
        db_table = 'fdcz'


# class (BaseModel):
#     link = TextField()
#     timenow = TextField(null=True)
#     企业性质 = TextField(null=True)
#     企业联系人 = TextField(null=True)
#     公司名称 = TextField(unique=True)
#     区域 = TextField(null=True)
#     地址 = TextField(null=True)
#     城市 = TextField(null=True)
#     招聘联系人 = TextField(null=True)
#     法人 = TextField(null=True)
#     电话 = TextField(null=True)
#     福利 = TextField(null=True)
#     简介 = TextField(null=True)
#     纬度 = TextField(null=True)
#     经度 = TextField(null=True)
#     职位 = TextField(null=True)
#     薪资 = TextField(null=True)
#     行业 = TextField(null=True)
#     要求 = TextField(null=True)
#     规模 = TextField(null=True)

#     class Meta:
#         db_table = '房地产东北地区'

# db.connect()
psql_db.connect()
#  创建数据库
# def createtable():
#     tables =[Fdcz,City,Baseurls,Purls]
#     tablelist = list(set(psql_db.get_tables()))
#     print tablelist
#     noextable=[]    
#     for t in tables:
#         print unicode(getattr(t,'__name__'), "utf-8")
#         if unicode(getattr(t,'__name__'), "utf-8") not in tablelist:
#             print str(unicode(getattr(t,'__name__'), "utf-8")),'不在table中'
#             noextable.append(t)

#     print 'noextable',noextable
#     if len(noextable) >=1:
#         psql_db.create_tables(noextable)
#     else:
#         pass
# try:
#     createtable()
# except Exception, e:
#     print str(e)
#     pass
# City.create(name='cs',nameb="测试")
# City.create(name='cs1',nameb="测试2")
# for i in City.select():
#     print i.nameb
#     print i.__dict__
