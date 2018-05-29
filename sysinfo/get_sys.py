#!/usr/bin/env python
# coding:utf-8
# yum -y install mysql-devel python-devel && pip install MySQL-python psutil sqlalchemy==1.1.15
import os
import re
import socket
import subprocess
import time
import MySQLdb
import psutil
import logging
import urllib2
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String

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
            logging.info("max:%s not exists！" % file)
            return


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
            logging.info("version: %s not exists！" % file)
            return


# 连接数据库
try:
    engine = create_engine("mysql://root:123456@jiangxi.listenrobot.cn:3306/test?charset=utf8", echo=False)
except Exception as err:
    print(err)
    time.sleep(3)
    engine = create_engine("mysql://root:123456@122.235.84.237:3306/test", echo=False)

Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class ServerInfo(Base):
    """服务器信息数据"""
    __tablename__ = 'servers'
    # __table_args__ = { 'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8' }
    # __table_args__ = {}
    id = Column(Integer, primary_key=True)
    manufacturer = Column(String(32))
    os_version = Column(String(64))
    cpu_num = Column(String(32))
    cpu_model = Column(String(64))
    memory = Column(String(32))
    net_card = Column(String(32))
    mac = Column(String(32))
    hostname = Column(String(64))
    local_ip = Column(String(32))
    public_ip = Column(String(32))
    aim_sn = Column(String(32))
    ai_version = Column(String(32))
    ai_max = Column(String(32))
    web_ip = Column(String(32))

# 建立表
# Base.metadata.create_all(bind=engine)


def main():
    mac = get_mac()
    aim_sn = get_aimsn_web()[0]
    ai_version = get_ai_version()
    ai_max = get_maximum_ai()
    web_ip = get_aimsn_web()[1]
    if mac:
        obj = session.query(ServerInfo).filter(ServerInfo.mac == mac).first()
        if obj:
            obj.hostname = get_hostname()
            obj.local_ip = get_netcard()[1]
            obj.public_ip = public_ip()
            if aim_sn: obj.aim_sn = aim_sn
            if ai_version: obj.ai_version = ai_version
            if ai_max: obj.ai_max = get_maximum_ai()
            if web_ip: obj.web_ip = web_ip
            session.add(obj)
            session.commit()
        else:
            new_obj = ServerInfo(
                    manufacturer=get_manufacturer(),
                    os_version=get_version(),
                    cpu_num=get_cpu_num(),
                    cpu_model=get_cpu_modle(),
                    memory=get_memory(),
                    net_card=get_netcard()[0],
                    mac=mac,
                    hostname=get_hostname(),
                    local_ip=get_netcard()[1],
                    public_ip=public_ip(),
                    aim_sn=aim_sn,
                    ai_version=ai_version,
                    ai_max=ai_max,
                    web_ip=web_ip
            )
            session.add(new_obj)
            session.commit()
    session.close()
    # engine.dispose()

if __name__ == '__main__':
    main()
