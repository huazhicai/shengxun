# coding:utf-8
# author: Seven
import random
from aliyunsdkalidns.request.v20150109.DescribeDomainRecordInfoRequest import DescribeDomainRecordInfoRequest
from aliyunsdkcore import client
from aliyunsdkalidns.request.v20150109 import DescribeDomainRecordsRequest, UpdateDomainRecordRequest
import json, re, requests
import requests.exceptions
import time
import logging
from logging.handlers import TimedRotatingFileHandler
from aliyunsdkcore.acs_exception.exceptions import ServerException

# from send_email import send_mail


# logging初始化工作
logging.basicConfig()
# alidns 日志器初始化
alidns = logging.getLogger('alidns')
alidns.setLevel(logging.DEBUG)

timefilehandler = TimedRotatingFileHandler('./config/alidns.log', when='MIDNIGHT', interval=1, backupCount=5)
timefilehandler.suffix = "%Y-%m-%d"
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# 为时间处理器设置格式
timefilehandler.setFormatter(formatter)
alidns.addHandler(timefilehandler)

access_key_id = "LTAI2uCU1NS2Rpk3"
access_Key_secret = "drMg8quTOTL7L0xDKcA13fcVkc6u1H"
RegionID = "cn-hangzhou"
Type = "A"
current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

with open('./config/config.json') as f:
    config = json.load(f)
    DomainName = config['DomainName']
    HostName = config['HostNameList']

# ip接口池
ip_proxy = ["http://www.taobao.com/help/getip.php",  # "http://pv.sohu.com/cityjson", "http://txt.go.sohu.com/ip/soip",
            "http://members.322.org/dyndns/getip"]


def local_ip():
    try:
        url = random.choice(ip_proxy)
        ip_response = requests.get(url)
        alidns.debug(url + " - " + str(ip_response.status_code))
        # 断言错误就跳到except执行
        assert ip_response.status_code == 200
        ip_patern = re.compile(r'\d+\.\d+\.\d+\.\d+')
        ip_value = ip_patern.findall(ip_response.text)[0]
        return ip_value
    except Exception as e:
        alidns.error("local_ip:" + str(e))
        local_ip()


# 检查第一页阿里云的ip
def check_records(dns_domain, page=1):
    clt = client.AcsClient(access_key_id, access_Key_secret, RegionID)
    # 创建描述域名记录请求实例
    request = DescribeDomainRecordsRequest.DescribeDomainRecordsRequest()
    # 添加一级域名请求参数
    request.set_DomainName(dns_domain)
    # 接受参数的格式为json
    request.set_accept_format('json')
    # 添加搜索页面的域名数量
    request.set_PageSize('100')
    request.set_PageNumber(page)
    # 客户端执行上述动作，如果异常就返回异常情况
    result = json.loads(clt.do_action_with_exception(request))
    return result


# 阿里云上的ip
def old_ip(recordId):
    clt = client.AcsClient(access_key_id, access_Key_secret, RegionID)
    request = DescribeDomainRecordInfoRequest()
    request.set_RecordId(recordId)
    request.set_accept_format('json')
    try:
        result = clt.do_action_with_exception(request)
        result = json.loads(result)['Value']
        return result
    except ServerException as e:
        alidns.error((e.get_error_code(), e.get_error_msg(), e.get_http_status()))


# 更新阿里的dns
def update_dns(HostName, RecordId, Type, IP):
    # 登录阿里客户端
    clt = client.AcsClient(access_key_id, access_Key_secret, RegionID)
    # 创建一个更新域名记录请求类实例
    request = UpdateDomainRecordRequest.UpdateDomainRecordRequest()
    # 实例调用方法，接受json格式数据
    request.set_accept_format('json')
    # 添加记录ID号
    request.set_RecordId(RecordId)
    # 添加查询参数主机名，解析值
    request.set_RR(HostName)
    # 添加搜索字段类型
    request.set_Type(Type)
    # 添加搜索字段Time To Live(生存时间值,域名解析在DNS服务器中存留时间)
    request.set_TTL('600')
    # 添加搜索字段IP值
    request.set_Value(IP)
    # 客户端执行上述添加的操作
    try:
        result = clt.do_action_with_exception(request)
        results = json.loads(result)
        return results
    except ServerException as e:
        alidns.error((e.get_error_code(), e.get_error_msg(), e.get_http_status()))
        # 输出结果转换成dict,( json.loads:str转成dict)


def main():
    # 返回阿里云第一页的域名记录
    result = check_records('listenrobot.cn')
    Records = result['DomainRecords']['Record']
    PageNumber = result['PageNumber']
    TotalCount = result['TotalCount']
    PageSize = result['PageSize']
    while PageSize * PageNumber < TotalCount:
        # 返回第N页域名记录
        result_2 = check_records('listenrobot.cn', PageNumber + 1)
        print(result_2)
        Records += result_2['DomainRecords']['Record']
        PageNumber += 1
    # print(Records)
    # 服务器本地ip
    localIP = local_ip()
    for item in Records:
        if item['RR'] == HostName and item['Type'] == Type:
            RecordId = item['RecordId']
            oldIP = old_ip(RecordId)

            while oldIP == localIP:
                localIP = local_ip()
                time.sleep(20)

            if update_dns(HostName, RecordId, Type, localIP):
                alidns.info(HostName + ': Current IP is %s, Old IP is %s, IP has been changed.....\n' % (
                    localIP, oldIP))
                # send_mail(HostName, '%s: Current IP is %s, Old IP is %s, IP has been changed.....\n' % (
                #     current_time, localIP, oldIP))

            else:
                alidns.warning("{0} update failed {1} -> {2}".format(HostName, oldIP, localIP))
                # send_mail(HostName, "update failed")
            main()
    alidns.warning('{} not exists in aliyun or Type is not A.'.format(HostName))


if __name__ == '__main__':
    main()
