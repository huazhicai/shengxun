# coding:utf-8
# Author: Seven
import re
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth
import time
import schedule
from multiprocessing import Pool
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s-%(levelname)s-%(message)s')


# 发送目标号码和短信内容 user_id依次递增
def send_sms(ip):
    param = [{"number": "10010", "text_param": ["CXHF"], "user_id": 1},
             {"number": "10001", "text_param": ["101"], "user_id": 2}]
    url = 'http://{}/api/send_sms'.format(ip)
    auth = HTTPBasicAuth('admin', 'admin')
    for i in range(32):
        payload = {
            "text": "#param#", "port": [i],
            "param": param
        }
        res = requests.post(url, json=payload, auth=auth)
        print(res.text)
        time.sleep(1)


# send_sms('192.168.20.44')


# 通知短信
def notice_sms(ip, port, message):
    param = [{"number": "18701943997", "text_param": [ip + ": " + str(port) + "\n" + message], "user_id": 1},
             {"number": "15198002725", "text_param": [ip + ": " + str(port) + "\n" + message], "user_id": 2},
             {"number": "18969089900", "text_param": [ip + ": " + str(port) + "\n" + message], "user_id": 3}]
    url = 'http://{}/api/send_sms'.format(ip)
    auth = HTTPBasicAuth('admin', 'admin')

    payload = {
        "text": "#param#", "port": [port],
        "param": param
    }
    res = requests.post(url, json=payload, auth=auth)
    print(res.text)


# 读取短信
# 由于每次返回的大小都是8k所以要多次请求
def read_sms(ip):
    result = list()
    com_id = 0
    while True:
        url = 'http://{0}/api/query_incoming_sms?flag=all&incoming_sms_id={1}'.format(ip, com_id)
        auth = HTTPBasicAuth('admin', 'admin')
        resp = requests.get(url, auth=auth)
        datas = resp.json()
        com_id = datas['sms'][-1]["incoming_sms_id"]
        read = datas["read"]
        unread = datas["unread"]
        result.extend(datas['sms'])
        if com_id >= read + unread:
            break
    print(result)
    balanceRegex = re.compile(r'余额.*?(\d*\.?\d*)元')
    for item in result:
        if item['number'] in ('10010', '10001', '10086') and \
                        item['timestamp'].split(' ')[0] == datetime.now().strftime("%Y-%m-%d"):
            matchRegex = balanceRegex.search(item['text'])
            if matchRegex:
                retval = matchRegex.group(1)
                if float(retval) <= 10.0:
                    print(retval)
                    notice_sms(ip, item['port'], item['text'])


# def main():
#     pool = Pool()     # 设置进程池中的进程数
#     schedule.every().day.at("15:40").do(pool.map(send_sms, ['192.168.20.4' + str(i) for i in range(1, 6)]))
#     schedule.every().day.at("8:00").do(pool.map(read_sms, ['192.168.20.4' + str(i) for i in range(1, 6)]))
#     while True:
#         schedule.run_pending()
#         time.sleep(1)
#
#
# if __name__ == '__main__':
#     main()

schedule.every().day.at("1:00").do(send_sms, '192.168.20.47')
schedule.every().day.at("1:15").do(send_sms, '192.168.20.42')
schedule.every().day.at("1:30").do(send_sms, '192.168.20.43')
schedule.every().day.at("1:45").do(send_sms, '192.168.20.44')
schedule.every().day.at("2:00").do(send_sms, '192.168.20.45')

schedule.every().day.at("8:00").do(read_sms, '192.168.20.47')
schedule.every().day.at("8:10").do(read_sms, '192.168.20.42')
schedule.every().day.at("8:20").do(read_sms, '192.168.20.43')
schedule.every().day.at("8:30").do(read_sms, '192.168.20.44')
schedule.every().day.at("8:40").do(read_sms, '192.168.20.45')

while True:
    schedule.run_pending()
    time.sleep(1)