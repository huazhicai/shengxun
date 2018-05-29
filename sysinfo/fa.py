# coding:utf-8
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.colors import *

env.user = 'root'
env.password = 'Sdftd11'
env.port = 10022
# 失败也继续执行
env.skip_bad_hosts = True
env.timeout = 20
env.connection_attempts = 3

env.warn_only = True  # 竟然有用

vmware = ['192.168.20.9', '192.168.20.70', '192.168.20.125', '192.168.20.162',
          '192.168.20.53', '192.168.20.71', '192.168.20.109', '192.168.20.163',
          '192.168.20.13', '192.168.20.86', '192.168.20.117', '192.168.20.153',
          '192.168.20.26', '192.168.20.87', '192.168.20.118', '192.168.20.40',
          '192.168.20.28', '192.168.20.89', '192.168.20.110', '192.168.20.41',
          '192.168.20.65', '192.168.20.90', '192.168.20.113', '192.168.20.88',
          '192.168.20.35', '192.168.20.85', '192.168.20.119', '192.168.20.6',
          '192.168.20.52', '192.168.20.32', '192.168.20.120', '192.168.20.37',
          '192.168.20.55', '192.168.20.106', '192.168.20.121', '192.168.20.15',
          '192.168.20.69', '192.168.20.108', '192.168.20.123', '115.238.71.94',
          '192.168.40.12', '115.238.34.110', '192.168.20.36', '192.168.20.193',
          '192.168.20.194', '192.168.20.195', '192.168.20.196', '192.168.20.197',
          '192.168.20.200', '192.168.20.201', '192.168.20.202', '192.168.20.180',
          '192.168.20.154', '192.168.20.104']

ling = ['shanxiyiyunhu.listenrobot.cn', 'xiaoshan1.listenrobot.cn', 'jinan1.listenrobot.cn',
        'beijingaim2.listenrobot.cn', 'taiyuan1.listenrobot.cn', 'lanzhou1.listenrobot.cn',
        'jiningaim1.listenrobot.cn', 'guangzhou1.listenrobot.cn', 'dongguanls.listenrobot.cn',
        'langfangaim2.listenrobot.cn', 'tianjin2.listenrobot.cn', 'root@shanghai4.listenrobot.cn:10023',
        'langfangaim1.listenrobot.cn', 'tianjin1.listenrobot.cn', 'shanghai.listenrobot.cn',
        'yangzhou1.listenrobot.cn', 'linyi2.listenrobot.cn', 'root@xian2.listenrobot.cn:18122',
        'foshan2.listenrobot.cn', 'linyi1.listenrobot.cn', 'xian3.listenrobot.cn',
        'yanan1.listenrobot.cn', 'xiamen1.listenrobot.cn', 'xiaoshan.listenrobot.cn',
        'dongguan3.listenrobot.cn', 'ningbo1.listenrobot.cn', 'guangzhou.listenrobot.cn',
        'dongguan2.listenrobot.cn', 'xian4.listenrobot.cn', 'shanxilingsheng.listenrobot.cn',
        'dongguan1.listenrobot.cn', 'nanjing2.listenrobot.cn', 'ningbo.listenrobot.cn',
        'zhuzhou1.listenrobot.cn', 'nanjing1.listenrobot.cn', 'tianjin.listenrobot.cn',
        'qingdao2.listenrobot.cn', 'shanghai1.listenrobot.cn', 'nanjing.listenrobot.cn',
        'qingdao1.listenrobot.cn', 'changsha1.listenrobot.cn', 'beijing.listenrobot.cn',
        'nanyang1.listenrobot.cn', 'xuzhou1.listenrobot.cn', 'shanghai3.listenrobot.cn',
        'zhengzhou2.listenrobot.cn', 'root@sjz2.listenrobot.cn:10023',
        'zhengzhou1.listenrobot.cn', 'beishan1.listenrobot.cn', 'guangzhouby.listenrobot.cn',
        'foshan1.listenrobot.cn', 'suzhou1.listenrobot.cn', 'sjz3.listenrobot.cn',
        'shenzhen1.listenrobot.cn', 'beijing1.listenrobot.cn', 'xiamen.listenrobot.cn',
        'suzhou3.listenrobot.cn', 'sjz1.listenrobot.cn', 'suzhoufangtuo.listenrobot.cn',
        'xiaoshou.listenrobot.cn']

jinlun = ['jinlun1', 'jinlun2', 'jinlun3', 'jinlun4', 'jinlun5', 'jinlun6']

# env.roledefs = {'listenrobot': local, 'lingsheng': ling, 'jinlun': jinlun}
env.hosts = ling

file = 'getServerInfo.pyc'


def failedRecord(filename):
    with open(filename, 'w+') as fd:
        fd.write(env.host_string)


@task
@runs_once
def local_task():
    local("python -m getServerInfo.py")


@task
def put_file():
    print(blue("put file ..."))
    # warn_only 当出现异常时候继续执行
    with settings(warn_only=True):
        result = put(file, '/opt')
    if result.failed:
        abort('Aborting file of %s put task!' % file)
        failedRecord('putFailed.txt')


@task
def install_plugin():
    with settings(warn_only=True):
        result = run("yum -y install mysql-devel python-devel && pip install MySQL-python psutil sqlalchemy")
    if result.failed:
        failedRecord('pluginFailed.txt')
        abort('Aborting install plugin!')


@task
def run_pyc():
    with settings(warn_only=True):
        result = run("python /opt/getServerInfo.pyc")
    if result.failed and not confirm('run getServerInfo failed,Continue[Y/N]?'):
        print(yellow('put file...'))
        local("python -m get_sys.py")
        put('get_sys.pyc', '/opt')
        with settings(warn_only=True):
            result = run("python /opt/get_sys.pyc")
        if result.failed:
            failedRecord('runFailed.txt')
            abort('Aborting run %s' % file)


@task
def go():
    local_task()
    put_file()
    install_plugin()
    run_pyc()
