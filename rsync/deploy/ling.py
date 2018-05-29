# coding:utf-8
# Author: Seven

from fabric.api import *
from fabric.colors import *
from fabric.contrib.console import confirm

env.user = 'root'
env.port = '22'
# env.gateway = '192.168.20.5'
env.hosts = ['192.168.20.7', '192.168.20.9', '192.168.20.53', '192.168.20.13', '192.168.20.26', '192.168.20.28',
        '192.168.20.65', '192.168.20.35', '192.168.20.37', '192.168.20.52', '192.168.20.55', '192.168.20.68',
        '192.168.20.69', '192.168.20.70', '192.168.20.71', '192.168.20.86', '192.168.20.87', '192.168.20.89']


# 本地file移动到remote_dir
remote_dir = '/robotvoip/aim'
file = 'miko_sync.py'


# 上传脚本文件
@task
def put_file():
    print(blue('put file ...'))
    with cd(remote_dir):
        try:
            run('mkdir log')
        except:
            pass
        # warn_only当出现异常的时候继续执行
        with settings(warn_only=True):
            result = put(file, remote_dir)
        if result.failed and not confirm('put file filed,Continue[Y/N]?'):
            abort('Aborting file of %s put task!' % 'miko_sync.py')

        with settings(warn_only=True):
            result = put('./supervisord.conf', '/etc/')
        if result.failed and not confirm('put file filed,Continue[Y/N]?'):
            abort('Aborting file of %s put task!' % 'supervisord.conf')


# 安装第三方模块
@task
def install_plugin():
    run("pip install paramiko")


# 启动进程
@task
def start_miko_sync():
    run('supervisorctl reload')


@task
def go():
    put_file()
    install_plugin()
    start_miko_sync()