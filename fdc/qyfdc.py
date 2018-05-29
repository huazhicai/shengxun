# -*- coding: utf-8 -*-
import sqlite3
import sys

from .config import Con

reload(sys)
sys.setdefaultencoding("utf-8")
quyu = Con.quyu()
print(quyu)


def retlist(diqu, quyu):
    for qu in quyu:
        # print json.dumps(qu, ensure_ascii=False)
        # print json.dumps(qu[0], ensure_ascii=False)
        # print json.dumps(qu[1], ensure_ascii=False)
        if diqu in qu[1]:
            return qu[0]
    return "未知"


def gosqlite(dbname, fromname, insname):
    conn = sqlite3.connect(dbname, timeout=10)
    # cursor=conn.execute('''SELECT 公司名称 FROM 房地产标题 LIMIT 10''')
    citybf = conn.execute('''SELECT * FROM {fromname}'''.format(fromname=fromname))
    # citybf = ['bj', 'sh','tj','cq','qd','jn','yt','wf','linyi','zb','jining','ta','lc','weihai','zaozhuang','dz','rizhao','dy','heze','shouguang','su','nj','wx','cz','xz','nt','yz','yangcheng','ha','suqian','zj','shuyang','dongtai','danyang','hz','nb','wz','jh','jx','tz','sx','huzhou']
    # UNIQUE ("公司名称" ASC) ON CONFLICT IGNORE,DROP TABLE IF EXISTS "main"."{tablename}";

    for city in citybf:
        tname = city[0].encode('utf-8')
        print(tname)
        diqu = city[1]
        print(insname)
        print(retlist(diqu, quyu))
        fenquname = retlist(diqu, quyu)
        tablename = insname + fenquname
        sqlfire = Con.sqlfire(tablename)
        sqlinsert = Con.sqlinsert(tablename, fromname, tname)
        # print sqlfire.decode('utf-8')
        try:
            conn.execute(sqlfire)
            conn.execute(sqlinsert)
        except Exception as e:
            print(str(e))
    try:
        conn.commit()
    except Exception as e:
        print(str(e))
        conn.close()
    conn.close()
    print(u'成功完成分区域')
    # for row in cursor:
    #     print row
    # 'CREATE TABLE 房地产标题 (link text ,职位 text ,公司名称 text ,区域 text ,timestamp int);'


if __name__ == '__main__':
    dbname = './pc58.db'
    fromname = '房地产总'
    insname = '房地产'
    gosqlite(dbname, fromname, insname)
