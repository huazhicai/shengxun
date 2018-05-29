"""
鼎信网关配置脚本V1.2, VOS版本
建议先把序列号填到远程注册平台，
脚本运行后会自动注册上去。
"""


# 网关初始IP
BASE_IP = '192.168.11.1'


# IP 和 gateway配置
IP = '192.168.11.225'
GATEWAY = '192.168.11.2'
DNS = '8.8.8.8'


"""SIP配置"""
SIP_PROXY_IP = '47.96.155.220'  # SIP代理域名或IP地址
PASSWORD = 'admin@1234'   # 密码
SIP_ACCOUNT = 'dream-225'    # SIP注册的帐号
AUTHEN_NAME = 'dream-225'    # 认证名
LOCAL_PORT_VALUE = '5070'   # 本地sip端口值


# 号码配置
PREFIX = '157101225'
start = 0
end = 31


