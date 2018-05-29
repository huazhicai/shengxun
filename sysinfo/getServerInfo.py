#!/usr/bin/env python
# coding:utf-8
# yum -y install mysql-devel && pip install MySQL-python psutil
import os
import re
import socket
import subprocess
import MySQLdb
import psutil
import logging
import urllib2

logging.basicConfig(level=logging.INFO, format='%(asctime)s-%(levelname)s-%(message)s')


# 获取内网ip
def get_netcard():
    info = psutil.net_if_addrs()
    for k, v in info.items():
        for item in v:
            if item[0] == 2 and (item[1].startswith('192.168') or item[1].startswith('172.16')):
                return (k, item[1])


# 获取mac地址
def get_mac():
    netcard = get_netcard()[0]
    info = psutil.net_if_addrs()
    for k, v in info.items():
        if k == netcard:
            for item in v:
                if item[0] == 17 and not item[1] == '00:00:00:00:00:0':
                    return item[1]


# 获取公网ip
def public_ip():
    try:
        sock = socket.create_connection(('ns1.dnspod.net', 6666), timeout=10)
        ip = sock.recv(16)
        sock.close()
        return ip
    except Exception as e:
        logging.error(str(e))
        ip_response = urllib2.urlopen("http://members.3322.org/dyndns/getip", timeout=10)
        return ip_response.read().strip()


# 获取供应商名称
def get_manufacturer():
    cmd = "dmidecode -s system-manufacturer"
    manu = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return manu.stdout.read().strip()


# 获取Linux系统主机名称
def get_hostname():
    return socket.gethostname()


# 获取Linux系统的版本信息
def get_version():
    if os.path.exists("/etc/redhat-release"):
        with open('/etc/redhat-release') as fd:
            os_version = fd.read().strip()
        return os_version
    else:
        return os.popen('cat /etc/issue').read().strip()


# 获取CPU的型号和CPU的核心数
def get_cpu_modle():
    with open('/proc/cpuinfo') as fd:
        for line in fd:
            if line.startswith('model name'):
                cpu_model = line.split(':')[1].strip()
                return cpu_model


def get_cpu_num():
    return str(psutil.cpu_count(logical=False))


# 获取Linux系统的总物理内存
def get_memory():
    with open('/proc/meminfo') as fd:
        for line in fd:
            if line.startswith('MemTotal'):
                mem = int(line.split()[1].strip())
                break
    mem = '%.f' % (mem / 1024.0)
    return mem


# 获取aim_sn
def get_aimsn_web():
    retval = []
    if os.path.exists('/robotvoip/aim/src/pmanage_v02/pmanage_config.py'):
        with open('/robotvoip/aim/src/pmanage_v02/pmanage_config.py') as fd:
            for line in fd:
                if 'aim_sn' in line:
                    retval.append(line.split("'")[3])
                if 'basedomain' in line:
                    retval.append(line.split("'")[3])
                if len(retval) == 2:
                    return retval
    else:
        logging.info('pmanage_config.py not exists!')


# 获取ai上限数
def get_maximum_ai():
    file = '/robotvoip/aim/pmanage.log'
    ai_max = ''
    n = 1
    while not ai_max and n < 5:
        if os.path.exists(file):
            with open(file) as fd:
                filestr = fd.read()
                aiNumRegex = re.compile(r'process count\[\d*/(\d*)\]', re.DOTALL)
                ai_max = aiNumRegex.search(filestr)
                if ai_max: return ai_max.group(1)
            file = '.'.join(['/robotvoip/aim/pmanage.log', str(n)])
            n += 1
        else:
            logging.info("%s not exists！" % file)
            break


# 获取ai版本
def get_ai_version():
    file = '/robotvoip/aim/pmanage.log'
    ai_version = ''
    n = 1
    while not ai_version and n < 5:
        if os.path.exists(file):
            with open(file) as fd:
                for line in fd:
                    if line.startswith('version:'):
                        ai_version = line.split(' ')[1]
                        if ai_version: return ai_version
            file = '.'.join(['/robotvoip/aim/pmanage.log', str(n)])
            n += 1
        else:
            logging.info("%s not exists！" % file)
            break


def connect_db():
    try:
        conn = MySQLdb.connect(host='jiangxi.listenrobot.cn',
                               port=3306,
                               charset='utf8',
                               passwd='123456',
                               user='root',
                               db='test'
                               )
        return conn
    except Exception as e:
        logging.error(str(e))
        conn = MySQLdb.connect(host='122.235.84.237',
                               port=3306,
                               charset='utf8',
                               passwd='123456',
                               user='root',
                               db='test'
                               )
        return conn


def insert_database(args):
    conn = connect_db()
    cur = conn.cursor()
    sql_insert = "INSERT INTO servers (manufacturer,os_version,cpu_num,cpu_model,memory,net_card," \
                 "mac,hostname,local_ip,public_ip,aim_sn,ai_version,ai_max,	web_ip) VALUES" \
                 " ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % tuple(args)
    try:
        cur.execute(sql_insert)
        conn.commit()
        logging.info("insert successfully!")
    except Exception as e:
        conn.rollback()
        logging.error(str(e))
    finally:
        cur.close()
        conn.close()


def update_data(args):
    conn = connect_db()
    cur = conn.cursor()
    sql_update = "UPDATE servers SET manufacturer='%s', os_version='%s',cpu_num='%s', cpu_model='%s',memory='%s'," \
                 " net_card='%s',mac='%s',hostname='%s',local_ip='%s', public_ip='%s',aim_sn='%s', ai_version='%s'," \
                 "ai_max='%s', web_ip='%s' WHERE mac = '%s'" % tuple(args)
    try:
        cur.execute(sql_update)
        conn.commit()
        logging.info("update successfully!")
    except Exception as e:
        conn.rollback()
        logging.error("update failed" + str(e))
    finally:
        cur.close()
        conn.close()


def main():
    datas = []
    datas.append(get_manufacturer())
    datas.append(get_version())
    datas.append(get_cpu_num())
    datas.append(get_cpu_modle())
    datas.append(get_memory())
    datas.append(get_netcard()[0])
    mac = get_mac()
    datas.append(mac)
    datas.append(get_hostname())
    datas.append(get_netcard()[1])
    datas.append(public_ip())
    datas.append(get_aimsn_web()[0])
    datas.append(get_ai_version())
    datas.append(get_maximum_ai())
    datas.append(get_aimsn_web()[1])
    # print(datas)

    conn = connect_db()
    cur = conn.cursor()
    cur.execute("select mac from servers where mac='%s'" % mac)
    values = cur.fetchall()
    cur.close()
    conn.close()
    if not values:
        insert_database(datas)
    else:
        datas.append(mac)
        update_data(datas)


if __name__ == '__main__':
    main()
