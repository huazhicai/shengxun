# coding:utf-8
# Author: Seven

from fabric.api import *
from fabric.colors import *
from fabric.contrib.console import confirm

env.user = 'root'
env.port = '22'
# env.gateway = '192.168.20.5'
env.hosts = ['jinlun2', 'jinlun3', 'jinlun4', 'jinlun5']


# 本地file移动到remote_dir
remote_dir = '/robotvoip/aim'
file = 'miko_sync.py'


# 上传脚本文件
@task
def put_file():
    print(blue('put file ...'))
    with cd(remote_dir):
        run('mkdir log')
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
    start_miko_sync()