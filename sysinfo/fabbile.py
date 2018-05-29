# coding:utf-8
# Author: Seven

from fabric.api import *
from fabric.colors import *
from fabric.contrib.console import confirm


env.user = 'root'
# env.port = '22' or '10022' or '10023'
# env.gateway = '192.168.20.5'


listen = ['192.168.20.40:22', '192.168.20.41:22', '192.168.20.88:22', 'jiangxi.listenrobot.cn:10022',
          'xiaoshouaim.synvn.com:10022', 'xiaoshouaim.synvn.com:10023']

ling = ['192.168.20.7', '192.168.20.9', '192.168.20.53', '192.168.20.13', '192.168.20.26', '192.168.20.28',
        '192.168.20.65', '192.168.20.35', '192.168.20.37', '192.168.20.52', '192.168.20.55', '192.168.20.68',
        '192.168.20.69', '192.168.20.70', '192.168.20.71', '192.168.20.86', '192.168.20.87', '192.168.20.89']

jinlun = ['jinlun1', 'jinlun2', 'jinlun3', 'jinlun4', 'jinlun5', 'jinlun6']

env.roledefs = {'listenrobot': listen, 'lingsheng': ling, 'jinlun': jinlun}

file = 'getServerInfo.pyc'
remote_dir = '/opt'


@task
def put_all():
    with cd(remote_dir):
        print(blue('put file ...'))
        # warn_only当出现异常的时候继续执行
        with settings(warn_only=True):
            result = put(file, remote_dir)
        if result.failed and not confirm('put file filed,Continue[Y/N]?'):
            abort('Aborting file of %s put task!' % file)


@task
@roles('listenrobot')
def install_plugin():
    run('yum -y install mysql-devel && pip install MySQL-python psutil')


@task
def run_all():
    with cd(remote_dir):
        run('python %s' % file)


@task
@roles('listenrobot')
def put_listenrobot():
    with cd(remote_dir):
        # warn_only当出现异常的时候继续执行
        with settings(warn_only=True):
            result = put(file, remote_dir)
        if result.failed and not confirm('put file filed,Continue[Y/N]?'):
            abort('Aborting file of %s put task!' % file)


@task
@roles('lingsheng')
def put_lingsheng():
    with cd(remote_dir):
        # warn_only当出现异常的时候继续执行
        with settings(warn_only=True):
            result = put(file, remote_dir)
        if result.failed and not confirm('put file filed,Continue[Y/N]?'):
            abort('Aborting file of %s put task!' % file)


@task
@roles('jinlun')
def put_jinlun():
    with cd(remote_dir):
        # warn_only当出现异常的时候继续执行
        with settings(warn_only=True):
            result = put(file, remote_dir)
        if result.failed and not confirm('put file filed,Continue[Y/N]?'):
            abort('Aborting file of %s put task!' % file)


@task
@roles('listenrobot')
def run_listenrobot():
    with cd(remote_dir):
        run('python %s' % file)


@task
@roles('lingsheng')
def run_lingsheng():
    with settings(warn_only=True):
        with cd(remote_dir):
            run('python %s' % file)


@task
@roles('jinlun')
def run_jinlun():
    with cd(remote_dir):
        run('python %s' % file)


@task
def go_jinlun():
    run('yum -y install mysql-devel && pip install MySQL-python psutil')
    put_jinlun()
    run_jinlun()