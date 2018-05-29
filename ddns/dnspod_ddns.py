#!/usr/bin/env python
# coding:utf-8
"""
DNSPod用户API文档 :https://www.dnspod.cn/docs/index.html
author: Seven
"""
import socket
import requests
import time
import logging
from logging.handlers import RotatingFileHandler
import json

# 初始化日志的基本配
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# add the log message handler to the logger
handler = RotatingFileHandler('dnspod.log', maxBytes=10 * 1024 * 1024, backupCount=2)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# 加载json配置文件
with open('config.json') as f:
    config = json.load(f)
    host_name = config["host_name"]
    sub_domain = config["sub_domain"]


class DNSPod(object):

    def __init__(self, params):
        """用params初始化对象实例"""
        self._params = params

    def get_public_ip(self):
        """通过dnspod.net获取公网ip"""
        try:
            sock = socket.create_connection(('ns1.dnspod.net', 6666), timeout=10)
            ip = sock.recv(16)
            sock.close()
            return ip.decode('utf-8')
        except Exception as e:
            logger.error(e)
            ip_response = requests.get("http://members.3322.org/dyndns/getip", timeout=10)
            return ip_response.text.strip()

    def get_record_list(self, params):
        """
        获取dnspod记录列表, 接口:
        https://dnsapi.cn/Record.List
        """
        record_list_url = 'https://dnsapi.cn/Record.List'
        try:
            response = requests.post(record_list_url, data=params)
            records = response.json()
            # 返回json数据，使用json解码器, code=1:操作成功，类似于status_code=200
            code = response.json()['status']['code']
            record_id = response.json()['records'][0]['id'] if code == '1' else ""
            ip_value = response.json()['records'][0]['value'] if code == '1' else ""
            return dict(code=code, record_id=record_id, ip_value=ip_value)
        except Exception as e:
            logger.error(e)
            time.sleep(10)
            self.get_record_list(params)

    def create_record(self, params, ip):
        """
        往记录中添加新域名，接口:
        https://dnsapi.cn/Domain.Create
        """
        try:
            params['value'] = ip
            params['ttl'] = '600'
            record_create_url = 'https://dnsapi.cn/Record.Create'
            response = requests.post(record_create_url, data=params)
            logger.warning('create new record %s.%s with IP %s' % (params['sub_domain'], params['domain'], ip))
            assert response.json()['status']['code'] == '1'
            record_id = response.json()['record']['id']
            return record_id
        except Exception as e:
            logger.error(e)
            time.sleep(10)
            self.create_record(params, ip)

    def update_ddns(self, params, ip):
        """
        更新动态DNS记录， 接口:
        https://dnsapi.cn/Record.Ddns
        """
        try:
            params['value'] = ip
            ddns_url = 'https://dnsapi.cn/Record.Ddns'
            response = requests.post(ddns_url, data=params)
            logger.info('status: %s, reason: %s' % (response.status_code, response.reason))
            return response.json()['status']['code'] == '1'
        except Exception as e:
            logger.error(e)
            time.sleep(10)
            self.update_ddns(params, ip)

    def run(self, params=None):
        if params is None:
            params = self._params
        public_ip = self.get_public_ip()
        # 获取子域名的记录id(record_id)
        record_list = self.get_record_list(params)
        if record_list['code'] == '10':
            # 创建子域名记录, code=10,表示没有记录
            record_id = self.create_record(params, public_ip)
            remote_ip = record_list['ip_value']
        elif record_list['code'] == '1':
            # 获取子域名的记录id和ip
            record_id = record_list['record_id']
            remote_ip = record_list['ip_value']
        else:
            logger.debug('!!!cna not get record_id!!!')
            return -1
        params['record_id'] = record_id

        current_ip = remote_ip
        while True:
            try:
                public_ip = self.get_public_ip()
                if current_ip != public_ip:
                    logger.warning("update IP from %s to %s" % (current_ip, public_ip))
                    if self.update_ddns(params, public_ip):
                        current_ip = public_ip
                else:
                    logger.info("IP remains %s" % public_ip)
            except Exception as e:
                logger.debug(e)
                continue
            time.sleep(20)


def main():
    # 初始化参数，使用Token登录
    params = dict(
            login_token=("51327,dc0792ca688b01c576ee541456aa9e8b"),
            format="json",
            domain="listenrobot.club",
            sub_domain=sub_domain,
            record_type="A",
            record_line="默认"
    )
    dnspod = DNSPod(params)
    dnspod.run()


if __name__ == "__main__":
    main()
