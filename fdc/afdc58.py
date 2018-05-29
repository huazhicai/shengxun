# -*- coding: utf-8 -*-
import re
import sqlite3
import string
import sys
import time
# import urllib2

import frequests
from lxml import html

# from pprint import pprint
import json
# import uniout
import sched
import signal
import requests
import threading
from .config import Con
import logging
from auto_getlogger import *
from tqdm import *

reload(sys)
sys.setdefaultencoding("utf-8")

num = 0
headers = {'user-agent': 'Mozilla/5.0+(compatible;+Baiduspider/2.0;++http://www.baidu.com/search/spider.html)'}

logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
)


class LogRecord(logging.LogRecord):
    def getMessage(self):
        msg = self.msg
        if self.args:
            if isinstance(self.args, dict):
                msg = msg.format(**self.args)
            elif isinstance(self.args, list):
                msg = msg.format(**self.args)
            elif isinstance(self.args, set):
                msg = msg.format(**self.args)
            else:
                msg = msg.format(*self.args)
        return msg


class Logger(logging.Logger):
    def makeRecord(self, name, level, fn, lno, msg, args, exc_info, func=None, extra=None):
        rv = LogRecord(name, level, fn, lno, msg, args, exc_info, func)
        if extra is not None:
            for key in extra:
                rv.__dict__[key] = extra[key]
        return rv


logging.setLoggerClass(Logger)


def getrealurl(cityone):
    renew = ''
    try:
        renew = urllib2.urlopen(cityone).geturl()
        return renew
    except Exception as e:
        renew = ''
    finally:
        return renew


def stringclean(data):
    renew = ''
    try:
        renew = ''.join(str(data).split()).decode('utf8')
        filterlist = ['营业执照已认证', '', '', '(', ')', '\\r', '\\n', '\\t', '\\', '\"']
        for fil in filterlist:
            renew = string.replace(renew, fil, '')
        return renew
    except Exception as e:
        renew = ''
    else:
        renew = data
    finally:
        return renew


def rebase(url):
    al = []
    text = url
    m = re.search(r'[^&name=]+$', text)
    start = int(url.find('lat=')) + 4
    end = url.find('&name=')
    tbase = ''
    if m:
        lenx = len(m.group(0))
        aa = text[start:end]
        al = aa.split('%2C')
        return al
    else:
        return None


def remurl(url):
    al = []
    text = url
    m = re.search(r'[^ewu/]+$', text)
    start = int(url.find('ewu/')) + 4
    end = len(text)
    tbase = ''
    if m:
        lenx = len(m.group(0))
        aa = text[start:end]
        al = aa.split('%2C')
        return al
    else:
        return None


class KThread(threading.Thread):
    """A subclass of threading.Thread, with a kill()
    method.
    Come from:
    Kill a thread in Python:
    http://mail.python.org/pipermail/python-list/2004-May/260937.html

    """
    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.killed = False

    def start(self):
        """Start the thread."""
        self.__run_backup = self.run
        self.run = self.__run  # Force the Thread to install our trace.
        threading.Thread.start(self)

    def __run(self):

        """Hacked run function, which installs the
        trace."""
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, why, arg):

        if why == 'call':
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, why, arg):
        if self.killed:
            if why == 'line':
                raise SystemExit()
        return self.localtrace

    def kill(self):
        self.killed = True


class Timeout(Exception):
    """function run timeout"""
    pass


def timeout(seconds):
    def timeout_decorator(func):
        def _new_func(oldfunc, result, oldfunc_args, oldfunc_kwargs):
            result.append(oldfunc(*oldfunc_args, **oldfunc_kwargs))

        def _(*args, **kwargs):
            result = []
            new_kwargs = {  # create new args for _new_func, because we want to get the func return val to result list
                'oldfunc': func,
                'result': result,
                'oldfunc_args': args,
                'oldfunc_kwargs': kwargs
            }
            thd = KThread(target=_new_func, args=(), kwargs=new_kwargs)
            thd.start()
            thd.join(seconds)
            alive = thd.isAlive()
            thd.kill()  # kill the child thread
            if alive:
                # raise Timeout(u'function run too long, timeout %d seconds.' % seconds)
                try:
                    raise Timeout(u'function run too long, timeout %d seconds.' % seconds)
                finally:
                    return u'function run too long, timeout %d seconds.' % seconds
            else:
                return result[0]

        _.__name__ = func.__name__
        _.__doc__ = func.__doc__
        return _

    return timeout_decorator


def retry(attempt):
    def decorator(func):
        def wrapper(*args, **kw):
            att = 0
            while att < attempt:
                try:
                    return func(*args, **kw)
                except Exception as e:
                    att += 1
                    time.sleep(33)

        return wrapper

    return decorator


# def zp(r):
#     try:
#         print (json.dumps(json.loads(r.text), indent=4,ensure_ascii=False, encoding="utf-8"))
#     except Exception as e:
#         print r.text

@timeout(30)
@retry(attempt=100)
def get_response(urls):
    # logger = logging.getLogger(__name__)  
    # r = requests.get('http://www.oschina.net')
    # print result
    rs = (frequests.get(u, timeout=6, allow_redirects=True, stream=False, headers=headers) for u in urls)
    result = frequests.map(rs)
    responses = frequests.map(rs)
    content = '\n'.join(r.content for r in result)
    return content


@timeout(30)
@retry(attempt=100)
def get_next_response(url):
    # logger = logging.getLogger(__name__)  
    # r = requests.get('http://www.oschina.net')
    # print result
    rs = requests.get(url, timeout=6, allow_redirects=True, stream=False, headers=headers)
    # result= frequests(rs)
    # content = zp(rs)
    # content = '\n'.join( rs.text)
    return rs.text


# drop table if exist
def drop_table(conn, table_name):
    cu = conn.cursor()
    try:
        cu.execute('drop table if exists %s' % table_name)
    except sqlite3.Error as e:
        print('drop table failed:', e.args[0])
        return
    conn.commit()


# CONNECTDB
def connect_db(db_name):
    conn = sqlite3.connect(db_name, check_same_thread=False)
    conn.text_factory = str
    cursor = conn.cursor()
    cursor.execute('PRAGMA synchronous = OFF')
    # conn.text_factory = lambda x: unicode(x, utf-8, replace)
    return conn


# close connect
def close_db(conn):
    conn.close()


def create_restable(conn, inserttable):
    conn.execute('''CREATE TABLE IF NOT EXISTS {inserttable} ("公司名称"  text NOT NULL,
"城市"  text,"城区"  text,
"区域"  text,
"link"  text NOT NULL,
"法人" text,
"企业联系人" text,"企业性质" text,"规模" text,"地址" text,"行业" text,"经度" text,
"纬度" text,"简介" text,"电话" text,"招聘联系人" text,"职位" text,"要求" text,"薪资" text,"福利" text, "timenow"  text,
UNIQUE ("公司名称" ASC) ON CONFLICT IGNORE);'''.format(inserttable=inserttable))
    conn.commit()


def create_baseurls(conn, inserttable):
    conn.execute('''CREATE TABLE IF NOT EXISTS {inserttable} ("name" text,
"url"  text NOT NULL,"isget"  text,"city" text, "timenow"  text,
UNIQUE ("url" ASC) ON CONFLICT IGNORE);'''.format(inserttable=inserttable))
    conn.commit()


def inbasesql(conn, instable, city, url):
    # 插入数据库
    name, isget = '', '0'
    insqlbase = '''INSERT INTO {instable} (name,city,url,isget,timenow) VALUES ("{name}","{city}","{url}","{isget}","{timenow}");'''.format(
            instable="baseurls", name=name, city=city, url=url, isget=isget,
            timenow=time.strftime('%Y-%m-%d %H:%M:%S'));
    conn.execute(insqlbase)
    # conn.commit()
    print(insqlbase)


def checkbk(inc_name):
    deleteindent = ["我爱我家", "链家", "世纪不动产"]
    for bkname in deleteindent:
        if inc_name.find(bkname) == -1:
            return True
        else:
            return False


def insertsql(conn, instable, city, ciqu, quyu1, inc_name1, link1, faren, inclianxi, incxingzhi, guimo, dizhi, hangye,
              jingdu,
              weidu, incjianjie, phoneno, zplianxi, zhiwei, yaoqiu, xinzi, fuli):
    # 插入数据库
    insql = '''INSERT INTO {instable} (公司名称,城市,城区,区域,link,法人,企业联系人,企业性质,规模,地址,行业,经度,纬度,简介,电话,招聘联系人,职位,要求,薪资,福利,timenow) VALUES ({inc_name},"{city}","{ciqu}",{quyu},"{link}","{faren}","{inclianxi}","{incxingzhi}","{guimo}","{dizhi}","{hangye}","{jingdu}","{weidu}","{incjianjie}","{phoneno}","{zplianxi}","{zhiwei}","{yaoqiu}","{xinzi}","{fuli}","{timenow}");'''.format(
            instable=instable, city=city, ciqu=ciqu, quyu=quyu1, inc_name=inc_name1, link=link1, faren=faren,
            inclianxi=inclianxi,
            incxingzhi=incxingzhi, guimo=guimo, dizhi=dizhi, hangye=hangye, jingdu=jingdu, weidu=weidu,
            incjianjie=incjianjie, phoneno=phoneno, zplianxi=zplianxi, zhiwei=zhiwei, yaoqiu=yaoqiu, xinzi=xinzi,
            fuli=fuli,
            timenow=time.strftime('%Y-%m-%d %H:%M:%S'))
    conn.execute(insql)
    print(insql)


def updatesql(conn, instable, city, ciqu, quyu1, inc_name1, link1, faren, inclianxi, incxingzhi, guimo, dizhi, hangye,
              jingdu,
              weidu, incjianjie, phoneno, zplianxi, zhiwei, yaoqiu, xinzi, fuli):
    # 插入数据库
    upsql = '''INSERT OR REPLACE INTO {instable} (公司名称,城市,城区,区域,link,法人,企业联系人,企业性质,规模,地址,行业,经度,纬度,简介,电话,招聘联系人,职位,要求,薪资,福利,timenow) VALUES ({inc_name},"{city}","{ciqu}",{quyu},"{link}","{faren}","{inclianxi}","{incxingzhi}","{guimo}","{dizhi}","{hangye}","{jingdu}","{weidu}","{incjianjie}","{phoneno}","{zplianxi}","{zhiwei}","{yaoqiu}","{xinzi}","{fuli}","{timenow}");'''.format(
            instable=instable, city=city, ciqu=ciqu, quyu=quyu1, inc_name=inc_name1, link=link1, faren=faren,
            inclianxi=inclianxi,
            incxingzhi=incxingzhi, guimo=guimo, dizhi=dizhi, hangye=hangye, jingdu=jingdu, weidu=weidu,
            incjianjie=incjianjie, phoneno=phoneno, zplianxi=zplianxi, zhiwei=zhiwei, yaoqiu=yaoqiu, xinzi=xinzi,
            fuli=fuli,
            timenow=time.strftime('%Y-%m-%d %H:%M:%S'))
    conn.execute(upsql)
    print(upsql)


@timeout(6)
@retry(attempt=6)
def timeoutcommit(conn):
    # 超时提交
    conn.commit()


@timeout(30)
@retry(attempt=3)
def ciquexe(conn, instable, city, ciqu, quyu, incname=None, faren=None,
            inclianxi=None, incxingzhi=None, guimo=None, dizhi=None, hangye=None,
            jingdu=None, weidu=None, incjianjie=None, phoneno=None, zplianxi=None,
            zhiwei=None, yaoqiu=None, xinzi=None,
            fuli=None):  # faren, inclianxi, incxingzhi, guimo, dizhi, hangye,jingdu, weidu, incjianjie, phoneno, zplianxi, zhiwei, yaoqiu, xinzi, fuli
    try:
        upsql = '''UPDATE {instable} SET 城市 = "{city}", 城区 = "{ciqu}", 区域 = "{quyu}", timenow = "{timenow}",法人={faren},企业联系人={inclianxi},企业性质={incxingzhi},规模={guimo},地址={dizhi},行业={hangye},经度={jingdu},纬度={weidu},简介={incjianjie},电话={phoneno},招聘联系人={zplianxi},职位={zhiwei},要求={yaoqiu},薪资={xinzi},福利={fuli} WHERE 公司名称="{incname}";'''.format(
                instable=instable, city=city, ciqu=ciqu, quyu=quyu, incname=incname,
                timenow=time.strftime('%Y-%m-%d %H:%M:%S'));
        conn.execute(upsql)
        # print inbasesql(conn, instable, city, url)
        print(upsql)
    except Exception as e:
        print(str(e), "更新城区出错了\n\n")
        pass


@timeout(30)
@retry(attempt=3)
def urlacexe(conn, instable, city, ciqu, quyu, incname=None, faren=None,
             inclianxi=None, incxingzhi=None, guimo=None, dizhi=None, hangye=None,
             jingdu=None, weidu=None, incjianjie=None, phoneno=None, zplianxi=None,
             zhiwei=None, yaoqiu=None, xinzi=None,
             fuli=None):  # faren, inclianxi, incxingzhi, guimo, dizhi, hangye,jingdu, weidu, incjianjie, phoneno, zplianxi, zhiwei, yaoqiu, xinzi, fuli
    try:
        upsql = '''UPDATE {instable} SET 城市 = "{city}", 城区 = "{ciqu}", 区域 = "{quyu}", timenow = "{timenow}",法人={faren},企业联系人={inclianxi},企业性质={incxingzhi},规模={guimo},地址={dizhi},行业={hangye},经度={jingdu},纬度={weidu},简介={incjianjie},电话={phoneno},招聘联系人={zplianxi},职位={zhiwei},要求={yaoqiu},薪资={xinzi},福利={fuli} WHERE 公司名称="{incname}";'''.format(
                instable=instable, city=city, ciqu=ciqu, quyu=quyu, incname=incname,
                timenow=time.strftime('%Y-%m-%d %H:%M:%S'));
        conn.execute(upsql)
        # print inbasesql(conn, instable, city, url)
        print(upsql)
    except Exception as e:
        print(str(e), "更新城区出错了\n\n")
        pass


@timeout(30)
@retry(attempt=16)
def urlexe(conn, instable, city, url):
    try:
        inbasesql(conn, instable, city, url)
        # print inbasesql(conn, instable, city, url)
    except Exception as e:
        print(str(e), "插入url库错误\n\n")
        pass


@timeout(30)
@retry(attempt=6)
def timeoutexe(conn, instable, insname, city, ciqu, quyu1, inc_name1, link1, faren, inclianxi, incxingzhi, guimo, dizhi,
               hangye, jingdu, weidu, incjianjie, phoneno, zplianxi, zhiwei, yaoqiu, xinzi, fuli):
    try:
        insertsql(conn, instable, city, quyu1, inc_name1, link1, faren, inclianxi, incxingzhi, guimo, dizhi, hangye,
                  jingdu, weidu, incjianjie, phoneno, zplianxi, zhiwei, yaoqiu, xinzi, fuli)
    except Exception as e:
        print(str(e), "插入总库错误\n\n")
        pass
        # try:
        #     Con.gosqlite(conn,insname,city, quyu1, inc_name1, link1,faren,inclianxi,incxingzhi,guimo,dizhi,hangye,jingdu,weidu,incjianjie,phoneno,zplianxi,zhiwei,yaoqiu,xinzi,fuli)
        # except Exception as e:
        #     print str(e),"插入分区库错误\n\n"
        #     pass


@timeout(30)
@retry(attempt=6)
def timeoutupdate(conn, instable, insname, city, ciqu, quyu1, inc_name1, link1, faren, inclianxi, incxingzhi, guimo,
                  dizhi,
                  hangye, jingdu, weidu, incjianjie, phoneno, zplianxi, zhiwei, yaoqiu, xinzi, fuli):
    try:
        updatesql(conn, instable, city, ciqu, quyu1, inc_name1, link1, faren, inclianxi, incxingzhi, guimo, dizhi,
                  hangye,
                  jingdu, weidu, incjianjie, phoneno, zplianxi, zhiwei, yaoqiu, xinzi, fuli)
    except Exception as e:
        print(str(e), "插入总库错误\n\n")
        pass
        # try:
        #     Con.gosqlite(conn,insname,city, quyu1, inc_name1, link1,faren,inclianxi,incxingzhi,guimo,dizhi,hangye,jingdu,weidu,incjianjie,phoneno,zplianxi,zhiwei,yaoqiu,xinzi,fuli)
        # except Exception as e:
        #     print str(e),"插入分区库错误\n\n"
        #     pass


def getone(wtree, rule):
    bdata = wtree.xpath(rule)
    # print 'bdata',bdata
    if isinstance(bdata, list) and len(bdata) > 0:
        data = stringclean(json.dumps(bdata[0], ensure_ascii=False))
    else:
        data = stringclean(json.dumps(bdata, ensure_ascii=False))
    if isinstance(data, list) and len(bdata) > 0:
        return data[0]
    else:
        return data


def getonehtml(wtree, rule):
    bdata = wtree.xpath(rule)
    # print 'bdata',bdata
    if isinstance(bdata, list) and len(bdata) > 0:
        data = json.dumps(bdata[0], ensure_ascii=False)
    else:
        data = json.dumps(bdata, ensure_ascii=False)
    if isinstance(data, list) and len(bdata) > 0:
        return data[0]
    else:
        return data


addtimes = 0
uptimes = 0


def upciqu(conn=None, instable=None, insname=None, cityn=None, urlafter=None, urls=None, incname=None):
    print(("\n\n"))
    print('开始抓取……')
    inc_name1 = incname
    # inc_link=incname
    print(inc_name1)
    # city = cityn
    link1 = urls[0]
    link1 = getrealurl(link1)
    global addtimes, uptimes
    mlink = "http://m.58.com/" + link1[7:int(link1.find('.'))] + "/yewu/" + remurl(link1)[0]
    wlink = "http://i.wap.58.com/" + link1[7:int(link1.find('.'))] + "/yewu/" + remurl(link1)[0]
    print(mlink)
    logging.info(inc_name1)
    logging.info(link1)
    logging.info(mlink)
    logging.debug("触屏网址: %s" % mlink)
    # 取企业信息
    # next_content = get_next_response(inc_link)
    # ntree = html.fromstring(next_content)

    # 取电话
    p_content = get_next_response(mlink)
    ptree = html.fromstring(p_content)
    try:
        phoneno = getone(wtree=ptree, rule="//*/div[@class='ffield']/a[@id='contact_phone']/@phoneno")
        logging.debug(u"电话: %s" % phoneno)
    except Exception as e:
        logging.debug("%s" % str(e))
        pass
    w_content = get_next_response(link1)
    wtree = html.fromstring(w_content)
    try:
        ncity = getone(wtree=wtree, rule="//*//div[1]/ul/li[@class='condition']/span[@class='area']/a[1]/text()")
        logging.debug("城市: %s" % ncity)
    except Exception as e:
        ncity = getone(wtree=ptree, rule="//*/span[@class='city-text']/text()")
        logging.debug("%s" % str(e))
    try:
        ciqu = getone(wtree=wtree, rule="//*//div[1]/ul/li[@class='condition']/span[@class='area']/a[2]/text()")

        logging.debug("城区: %s" % ciqu)
    except Exception as e:
        logging.debug("%s" % str(e))
        ciqu = ''
    try:
        nquyu = getone(wtree=wtree, rule="//*//div[1]/ul/li[@class='condition']/span[@class='area']/a[3]/text()")
        logging.debug("区域: %s" % nquyu)
    except Exception as e:
        logging.debug("%s" % str(e))
        nquyu = ciqu
    # 取企业信息
    try:
        inc_link = getonehtml(wtree=wtree, rule="//*/div[@class='companyCon mod detailRightAd']/a/@href")
        logging.debug("企业url: %s" % inc_link)
    except Exception as e:
        logging.debug("%s" % str(e))
        pass
    next_content = get_next_response(inc_link)
    ntree = html.fromstring(next_content)
    inc_link = getrealurl(inc_link)

    if inc_link.find('/mq/') == -1:
        try:
            faren = getone(ntree, '//*/div[@class="basicMsg"]/ul/li[3]/text()')
        except Exception as e:
            logging.debug("%s" % str(e))
            pass
        try:
            inclianxi = getone(ntree, '//*/div[@class="basicMsg"]/ul/li[2]/text()')
        except Exception as e:
            raise e
        try:
            incxingzhi = getone(ntree, '//*/div[@class="basicMsg"]/ul/li[5]/text()')
        except Exception as e:
            logging.debug("%s" % str(e))
            pass
        try:
            guimo = getone(ntree, '//*/div[@class="basicMsg"]/ul/li[7]/text()')
        except Exception as e:
            logging.debug("%s" % str(e))
            pass
        try:
            dizhi = getone(ntree,
                           '//*/div[@class="basicMsg"]/ul[@class="basicMsgListo basicMsgList clearfix"]/li[@class="compony cleafix"]/div[@class="fl"]/var/text()')

        except Exception as e:
            logging.debug("%s" % str(e))
            pass
        try:
            hangye = getone(ntree, '//*/div[@class="basicMsg"]/ul/li[9]/div[@class="tradeName"]/a/text()')
        except Exception as e:
            logging.debug("%s" % str(e))
            pass
        try:
            jingdu = rebase(json.dumps(ntree.xpath(
                    "//*/div[@class='basicMsg']/ul[@class='basicMsgListo basicMsgList clearfix']/li[@class='compony cleafix']/div[@class='fl']/a/@href")[
                                           0], ensure_ascii=False))[0]

        except Exception as e:
            logging.debug("%s" % str(e))
            jingdu = ''
        try:
            weidu = rebase(json.dumps(ntree.xpath(
                    "//*/div[@class='basicMsg']/ul[@class='basicMsgListo basicMsgList clearfix']/li[@class='compony cleafix']/div[@class='fl']/a/@href"),
                    ensure_ascii=False))[1]
        except Exception as e:
            logging.debug("%s" % str(e))
            weidu = ''
        try:
            incjianjie = getone(ntree,
                                "//*/div[@class='basicMsg']/div[@class='compIntro']/p/text()|//*/div[@class='basicMsg']/div[@class='compIntro']/p/span/text()")
        except Exception as e:
            logging.debug("%s" % str(e))
            pass
    else:
        try:
            faren = getone(ntree, "//*/div[@class='basicMsg']/ul/li[3]/text()")
        except Exception as e:
            logging.debug("%s" % str(e))
            pass
        try:
            inclianxi = getone(ntree,
                               "//*/div[@class='intro_down_wrap']/div[@class='intro_down']/table/tbody/tr[@class='tr_l4']/td[@class='td_c2']/text()")
        except Exception as e:
            logging.debug("%s" % str(e))
            pass
        try:
            incxingzhi = getone(ntree,
                                "//*/div[@class='intro_down_wrap']/div[@class='intro_down']/table/tbody/tr[2]/td[@class='td_c2']/text()")
        except Exception as e:
            logging.debug("%s" % str(e))
            pass
        try:
            guimo = getone(ntree,
                           "//*/div[@class='intro_down_wrap']/div[@class='intro_down']/table/tbody/tr[2]/td[@class='td_c3']/text()")
            logging.debug('规模:', guimo)
        except Exception as e:
            logging.debug("%s" % str(e))
            pass
        try:
            dizhi = getone(ntree,
                           "//*/div[@class='intro_down_wrap']/div[@class='intro_down']/table/tbody/tr[@class='tr_l6']/td[@class='td_c1']/span/text()")
        except Exception as e:
            logging.debug("%s" % str(e))
            pass
        try:
            hangye = getone(ntree,
                            "//*/div[@class='intro_down_wrap']/div[@class='intro_down']/table/tbody/tr[@class='tr_l4']/td[@class='td_c1']/a/text()")
        except Exception as e:
            logging.debug("%s" % str(e))
            pass
        try:
            jingdu = rebase(json.dumps(ntree.xpath(
                    "//*/div[@class='intro_down_wrap']/div[@class='intro_down']/table/tbody/tr[@class='tr_l6']/td[@class='td_c1']/a[@class='map']/@href")[
                                           0], ensure_ascii=False))[0]
        except Exception as e:
            logging.debug("%s" % str(e))
            pass
        try:
            weidu = rebase(json.dumps(ntree.xpath(
                    "//*/div[@class='intro_down_wrap']/div[@class='intro_down']/table/tbody/tr[@class='tr_l6']/td[@class='td_c1']/a[@class='map']/@href"),
                    ensure_ascii=False))[1]

        except Exception as e:
            logging.debug("%s" % str(e))
            pass
        try:
            incjianjie = getone(ntree,
                                "//*/div[@class='company_intro']/div[@class='wrap_intro']/div[@class='intro_middle']/p[2]/text()")
            if not incjianjie or incjianjie == '':
                incjianjie = getone(ntree, "//*/div[@class='compIntro']//text()")
        except Exception as e:
            logging.debug("%s" % str(e))
            pass
    try:
        # logging.debug("%s" %(faren, inclianxi, incxingzhi, guimo, dizhi, hangye, jingdu, weidu, incjianjie, phoneno, zplianxi, zhiwei, yaoqiu, xinzi, fuli))
        logging.debug("\n\n")
    except Exception as e:
        logging.debug("%s" % str(e))
        raise e
    # logging.debug(u"经营期限", stringclean(json.dumps(tree.xpath("//*/div[@class='wb-main']/div[@class='wb-content']/div[@class='wrap']/div[@class='basicMsg']/div[@class='businessInfo']/ul[@class='basicMsgList clearfix']/li[2]/div[@class='clearfix']/em/text()"), ensure_ascii=False)))
    # tree = html.fromstring(next_content)

    # ciquexe(conn=conn, instable=instable, incname=inc_name1, ciqu=ciqu)
    ciquexe(conn=conn, instable=instable, city=ncity, ciqu=ciqu, quyu=nquyu, incname=inc_name1, faren=faren,
            inclianxi=inclianxi, incxingzhi=incxingzhi,
            guimo=guimo, dizhi=dizhi, hangye=hangye, jingdu=jingdu, weidu=weidu, incjianjie=incjianjie, phoneno=phoneno,
            zplianxi=zplianxi, zhiwei=zhiwei, yaoqiu=yaoqiu, xinzi=xinzi, fuli=fuli)
    uptimes += 1

    print("\n\n")
    logging.info("增加了" + str(addtimes) + "条 -- 更新了" + str(uptimes) + "条")
    print("\n\n")
    timeoutcommit(conn)


# @retry(attempt=6)
def greurl(conn=None, instable=None, insname=None, cityn=None, urlafter=None, gredurl=None, pagenum=None, isold=None):
    if gredurl == 1:
        city = cityn[1].encode('utf-8')
        url = cityn[0]
        # print city, url
        # //*[@id="filter"]/div[2]/dl[2]/dd/ul/li[*]/a/@href
        baseurl = ['http://' + url + '.58.com/dianhuaxiaoshou/pn1/' + urlafter]
        # print baseurl
        contentbase = get_response(baseurl)
        # print contentbase
        basetree = html.fromstring(contentbase)
        #  取区域列表
        baseurls = basetree.xpath('//*[@id="filter"]/div[2]/dl[2]/dd/ul/li[*]/a/@href')
        # print baseurls
        urls = []
        for qyurl in baseurls:
            qyurl = string.replace(qyurl, urlafter, '')
            urlbasee = 'http://' + url + '.58.com' + qyurl + 'pn1/' + urlafter
            print(urlbasee)
            urlexe(conn, instable, city, urlbasee)
        timeoutcommit(conn)
    else:
        # 取老数据

        if isold == 1:
            print("取老数据")
            oldurl = conn.execute('''SELECT * FROM 房地产总 where 城市="杭州" limit 100''')
            oldurl = list(set(oldurl))

            # print urls
            for urll in tqdm(oldurl):
                print(urll[2])
                if not urll[2] or urll[2] == '' or urll[2] == 'None':
                    print('取无城区数据')
                    print(urll[0], urll[1])
                    oldurls = []
                    oldurls.append(urll[4])
                    # print urlb
                    # [urlq, urlh] = urlb.split('pn1/')
                    # # print urlq,'----',urlh
                    # urla = []
                    # for i in xrange(pagenum):
                    #     urla.append(urlq + 'pn' + str(i) + '/' + urlh)
                    # city = urll[1]
                    # logging.info(urla) 
                    upciqu(conn=conn, instable=instable, insname=insname, cityn=urll[1], urlafter=urlafter,
                           urls=oldurls, incname=urll[0])
        else:
            # 取列表再取文章url
            urlbf = conn.execute('''SELECT * FROM baseurls where city="杭州"''')
            urlbf = list(set(urlbf))
            # print urls
            for urll in tqdm(urlbf):
                print(urll[1])
                urlb = urll[1]
                [urlq, urlh] = urlb.split('pn1/')
                # print urlq,'----',urlh
                urla = []
                for i in range(pagenum):
                    urla.append(urlq + 'pn' + str(i) + '/' + urlh)
                city = urll[3]
                # logging.info(urla) 
                sp(conn=conn, instable=instable, insname=insname, cityn=city, urlafter=urlafter, urls=urla)


def sp(conn=None, instable=None, insname=None, cityn=None, urlafter=None, urls=None):
    print(("\n\n"))
    print('开始抓取……')
    city = cityn.encode('utf-8')
    # url = cityn

    urls = list(set(urls))
    # print urls
    # 取列表
    content = get_response(urls)
    tree = html.fromstring(content)
    allinfos = tree.xpath('//*[@id="infolist"]/dl')
    global addtimes, uptimes
    suctimes = 0

    for info in allinfos:
        suctimes += 1
        logging.info('当前url列表组中,第' + str(suctimes) + '次抓取..')
        try:
            [faren, inclianxi, incxingzhi, guimo, dizhi, hangye, jingdu, weidu, incjianjie, phoneno, zplianxi, zhiwei,
             yaoqiu, xinzi, fuli, ciqu] = ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
            quyu1 = json.dumps(info.xpath('./dd[@class="w96"]/text()')[0], ensure_ascii=False)
            inc_name1 = json.dumps(info.xpath('./dd[@class="w271"]/a/@title')[0], ensure_ascii=False)
            inc_link = info.xpath('./dd[@class="w271"]/a/@href')[0]
            link1 = info.xpath('./dt/a/@href')[0]

            logging.info(u"正在抓取: %s" % link1)
            # print Con.exincname(conn, instable, inc_name1)
            exnames = Con.exincname(conn, instable, inc_name1)
            exphones = Con.exphone(conn, instable, inc_name1)

            if not exnames or not exphones:
                inc_link = getrealurl(inc_link)
                link1 = getrealurl(link1)
                mlink = "http://m.58.com/" + link1[7:int(link1.find('.'))] + "/yewu/" + remurl(link1)[0]
                logging.info(inc_name1)
                logging.info(inc_link)
                logging.info(link1)
                logging.info(mlink)
                logging.debug(link1)
                logging.debug("触屏网址: %s" % mlink)
                # 取企业信息
                next_content = get_next_response(inc_link)
                ntree = html.fromstring(next_content)
                if inc_link.find('/mq/') == -1:
                    try:
                        faren = getone(ntree, '//*/div[@class="basicMsg"]/ul/li[3]/text()')
                    except Exception as e:
                        logging.debug("%s" % str(e))
                        pass
                    try:
                        inclianxi = getone(ntree, '//*/div[@class="basicMsg"]/ul/li[2]/text()')
                    except Exception as e:
                        raise e
                    try:
                        incxingzhi = getone(ntree, '//*/div[@class="basicMsg"]/ul/li[5]/text()')
                    except Exception as e:
                        logging.debug("%s" % str(e))
                        pass
                    try:
                        guimo = getone(ntree, '//*/div[@class="basicMsg"]/ul/li[7]/text()')
                    except Exception as e:
                        logging.debug("%s" % str(e))
                        pass
                    try:
                        dizhi = getone(ntree,
                                       '//*/div[@class="basicMsg"]/ul[@class="basicMsgListo basicMsgList clearfix"]/li[@class="compony cleafix"]/div[@class="fl"]/var/text()')

                    except Exception as e:
                        logging.debug("%s" % str(e))
                        pass
                    try:
                        hangye = getone(ntree, '//*/div[@class="basicMsg"]/ul/li[9]/div[@class="tradeName"]/a/text()')
                    except Exception as e:
                        logging.debug("%s" % str(e))
                        pass
                    try:
                        jingdu = rebase(json.dumps(ntree.xpath(
                                "//*/div[@class='basicMsg']/ul[@class='basicMsgListo basicMsgList clearfix']/li[@class='compony cleafix']/div[@class='fl']/a/@href")[
                                                       0], ensure_ascii=False))[0]

                    except Exception as e:
                        logging.debug("%s" % str(e))
                        pass
                    try:
                        weidu = rebase(json.dumps(ntree.xpath(
                                "//*/div[@class='basicMsg']/ul[@class='basicMsgListo basicMsgList clearfix']/li[@class='compony cleafix']/div[@class='fl']/a/@href"),
                                ensure_ascii=False))[1]
                    except Exception as e:
                        logging.debug("%s" % str(e))
                        pass
                    try:
                        incjianjie = getone(ntree,
                                            "//*/div[@class='basicMsg']/div[@class='compIntro']/p/text()|//*/div[@class='basicMsg']/div[@class='compIntro']/p/span/text()")
                    except Exception as e:
                        logging.debug("%s" % str(e))
                        pass
                else:
                    try:
                        faren = getone(ntree, "//*/div[@class='basicMsg']/ul/li[3]/text()")
                    except Exception as e:
                        logging.debug("%s" % str(e))
                        pass
                    try:
                        inclianxi = getone(ntree,
                                           "//*/div[@class='intro_down_wrap']/div[@class='intro_down']/table/tbody/tr[@class='tr_l4']/td[@class='td_c2']/text()")
                    except Exception as e:
                        logging.debug("%s" % str(e))
                        pass
                    try:
                        incxingzhi = getone(ntree,
                                            "//*/div[@class='intro_down_wrap']/div[@class='intro_down']/table/tbody/tr[2]/td[@class='td_c2']/text()")
                    except Exception as e:
                        logging.debug("%s" % str(e))
                        pass
                    try:
                        guimo = getone(ntree,
                                       "//*/div[@class='intro_down_wrap']/div[@class='intro_down']/table/tbody/tr[2]/td[@class='td_c3']/text()")
                        logging.debug('规模:', guimo)
                    except Exception as e:
                        logging.debug("%s" % str(e))
                        pass
                    try:
                        dizhi = getone(ntree,
                                       "//*/div[@class='intro_down_wrap']/div[@class='intro_down']/table/tbody/tr[@class='tr_l6']/td[@class='td_c1']/span/text()")
                    except Exception as e:
                        logging.debug("%s" % str(e))
                        pass
                    try:
                        hangye = getone(ntree,
                                        "//*/div[@class='intro_down_wrap']/div[@class='intro_down']/table/tbody/tr[@class='tr_l4']/td[@class='td_c1']/a/text()")
                    except Exception as e:
                        logging.debug("%s" % str(e))
                        pass
                    try:
                        jingdu = rebase(json.dumps(ntree.xpath(
                                "//*/div[@class='intro_down_wrap']/div[@class='intro_down']/table/tbody/tr[@class='tr_l6']/td[@class='td_c1']/a[@class='map']/@href")[
                                                       0], ensure_ascii=False))[0]
                    except Exception as e:
                        logging.debug("%s" % str(e))
                        pass
                    try:
                        weidu = rebase(json.dumps(ntree.xpath(
                                "//*/div[@class='intro_down_wrap']/div[@class='intro_down']/table/tbody/tr[@class='tr_l6']/td[@class='td_c1']/a[@class='map']/@href"),
                                ensure_ascii=False))[1]

                    except Exception as e:
                        logging.debug("%s" % str(e))
                        pass
                    try:
                        incjianjie = getone(ntree,
                                            "//*/div[@class='company_intro']/div[@class='wrap_intro']/div[@class='intro_middle']/p[2]/text()")
                        if not incjianjie or incjianjie == '':
                            incjianjie = getone(ntree, "//*/div[@class='compIntro']//text()")
                    except Exception as e:
                        logging.debug("%s" % str(e))
                        pass

                # 取电话
                p_content = get_next_response(mlink)
                ptree = html.fromstring(p_content)
                try:
                    phoneno = getone(ptree, "//*/div[@class='ffield']/a[@id='contact_phone']/@phoneno")[0]
                    logging.debug(u"电话: %s" % phoneno)
                except Exception as e:
                    logging.debug("%s" % str(e))
                    pass
                try:
                    ciqu = getone(ptree,
                                  "//*[@id='nav1']/section[@class='job_con']/ul/li[3]/span[@class='attrValue dizhiValue']/a[2]/text()")
                    if not ciqu or ciqu == '':
                        ciqu = getone(ptree,
                                      "//*[@id='nav1']/section[@class='job_con']/ul/li[3]/span[@class='attrValue dizhiValue']/a[1]/text()")
                    logging.debug("城区: %s" % ciqu)
                except Exception as e:
                    logging.debug("%s" % str(e))
                    pass
                try:
                    zplianxi = getone(ptree,
                                      "//*/div[@class='com']/div[@class='comWrap']/div[@class='contact']/span[2]/text()")
                except Exception as e:
                    logging.debug("%s" % str(e))
                    pass
                try:
                    zhiwei = getone(ptree, "//*/section[@class='job_con']/ul/li[1]/span[@class='attrValue']/a/text()")
                except Exception as e:
                    logging.debug("%s" % str(e))
                    pass
                try:
                    yaoqiu = getone(ptree,
                                    "//*/section[@class='job_con']/ul/li[@class='req']/span[@class='attrValue']/text()")
                except Exception as e:
                    logging.debug("%s" % str(e))
                    pass
                try:
                    xinzi = getone(ptree,
                                   "//*/section[@class='tit_area job_q bbOnepx']/div[@class='price']/span[@class='pay']/text()")
                except Exception as e:
                    logging.debug("%s" % str(e))
                    pass
                try:
                    fuli = getone(ptree,
                                  "//*/section[@class='job_con']/ul/li[@class='fuli attrName']/div[@class='fulivalue attrValue']/span[*]/text()")
                except Exception as e:
                    logging.debug("%s" % str(e))
                    pass
                try:
                    # logging.debug("%s" %(faren, inclianxi, incxingzhi, guimo, dizhi, hangye, jingdu, weidu, incjianjie, phoneno, zplianxi, zhiwei, yaoqiu, xinzi, fuli))
                    logging.debug("\n\n")
                except Exception as e:
                    logging.debug("%s" % str(e))
                    raise e
                # logging.debug(u"经营期限", stringclean(json.dumps(tree.xpath("//*/div[@class='wb-main']/div[@class='wb-content']/div[@class='wrap']/div[@class='basicMsg']/div[@class='businessInfo']/ul[@class='basicMsgList clearfix']/li[2]/div[@class='clearfix']/em/text()"), ensure_ascii=False)))
                # tree = html.fromstring(next_content)

                if not exphones:
                    uptimes += 1
                    timeoutupdate(conn, instable, insname, city, ciqu, quyu1, inc_name1, link1, faren, inclianxi,
                                  incxingzhi,
                                  guimo, dizhi, hangye, jingdu, weidu, incjianjie, phoneno, zplianxi, zhiwei, yaoqiu,
                                  xinzi, fuli)
                else:
                    addtimes = addtimes + 1
                    timeoutexe(conn, instable, insname, city, ciqu, quyu1, inc_name1, link1, faren, inclianxi,
                               incxingzhi, guimo,
                               dizhi, hangye, jingdu, weidu, incjianjie, phoneno, zplianxi, zhiwei, yaoqiu, xinzi, fuli)
                print("\n\n")
                logging.info("增加了" + str(addtimes) + "条 -- 更新了" + str(uptimes) + "条")
                print("\n\n")
            else:
                # logging.debug(addtimes)
                logging.info(u" %s 数据库中已存在 无需重复抓取……" % inc_name1)
                logging.info("\n")
        except Exception as e:
            # insqlbad = '''INSERT INTO citybad (name,nameb,ident,timenow) VALUES ("{name}","{city}",{ident},"{timenow}");'''.format(name=cityn[0],city=cityn[1],ident=0,timenow=time.strftime('%Y-%m-%d %H:%M:%S'));
            # logging.debug(insqlbad)
            # conn.execute(insqlbad)
            logging.debug("%s" % str(e))
        timeoutcommit(conn)


if __name__ == "__main__":

    db_name = './pc58.db'
    instable = '房地产总'
    urlafter = 'pve_5363_269/'
    insname = '房地产'
    urltablename = 'baseurls'  # url表名
    conn = connect_db(db_name)
    create_restable(conn, instable)  # 创建资源数据库表
    create_baseurls(conn, urltablename)  # 创建列表源基础地址数据库表
    gredurl = 0  # 是否抓取url列表 0 不抓 1 抓
    pagenum = 50  # 抓取多少页
    isold = 0  # 是否取老数据


    def handler(signum, frame):
        raise AssertionError
        i = 0
        for i in range(1, 10):
            try:
                signal.signal(signal.SIGALRM, handler)
                signal.alarm(3)
                test(i)
                i = i + 1
                signal.alarm(0)
            except AssertionError:
                print("%d timeout" % (i))


    s = sched.scheduler(time.time, time.sleep)


    def event_func():
        citygo(conn, instable)


    def perform(inc):
        s.enter(inc, 0, perform, (inc,))
        event_func()


    def mymain(inc=68):
        s.enter(0, 0, perform, (inc,))
        s.run()


    def citygo(conn, instable):
        conn = connect_db(db_name)
        citybf = conn.execute('''SELECT * FROM city''')
        city = []
        citybf = list(citybf)
        citybf.insert(0, ('hz', '杭州'))
        if isold == 1:
            greurl(conn=conn, instable=instable, insname=insname, cityn=citybf, urlafter=urlafter, gredurl=gredurl,
                   pagenum=pagenum, isold=isold)
        elif greurl == 0:
            greurl(conn=conn, instable=instable, insname=insname, cityn=citybf, urlafter=urlafter, gredurl=gredurl,
                   pagenum=pagenum, isold=isold)
        else:
            for city in citybf:
                print(city)
                # city = ['ta','泰安']
                # city[0]='ta'
                # city[1]='泰安'
                greurl(conn=conn, instable=instable, insname=insname, cityn=city, urlafter=urlafter, gredurl=gredurl,
                       pagenum=pagenum, isold=isold)
        # city = ['hz','杭州']
        # city[0]='hz'
        # city[1]='杭州'
        # sp(conn,instable,insname,city,urlafter)
        close_db(conn)

    mymain()
    close_db(conn)