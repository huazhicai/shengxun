# coding:utf-8
# Author: Seven

from fabric.api import *
from fabric.colors import *
from fabric.contrib.console import confirm

env.user = 'root'
env.port = '22'
# env.gateway = '192.168.20.5'
env.passwords = {'1921.68.20.68:22': 'Sdftd11'}

listen = ['192.168.20.40', '192.168.20.41', '192.168.20.88', 'root@dream1.listenrobot.cn:10022',
          'xiaoshouaim.synvn.com:10022', 'xiaoshouaim.synvn.com:10023']

env.hosts = ['192.168.20.41',
             '192.168.20.88',
             '192.168.20.6',
             '192.168.20.37',
             '192.168.20.15',
             '192.168.20.7',
             '192.168.20.9',
             '192.168.20.53',
             '192.168.20.13',
             '192.168.20.26',
             '192.168.20.28',
             '192.168.20.65',
             '192.168.20.35',
             '192.168.20.55',
             '192.168.20.69',
             '192.168.20.70',
             '192.168.20.71',
             '192.168.20.86',
             '192.168.20.87',
             '192.168.20.89',
             '192.168.20.90',
             '192.168.20.85',
             '192.168.20.32',
             '192.168.20.105',
             '192.168.20.106',
             '192.168.20.108',
             '192.168.20.125',
             '192.168.20.109',
             '192.168.20.117',
             '192.168.20.118',
             '192.168.20.110',
             '192.168.20.111',
             '192.168.20.112',
             '192.168.20.113',
             '192.168.20.119',
             '192.168.20.120',
             '192.168.20.121',
             '192.168.20.123',
             '192.168.20.68'
             ]


@task
def putfile():
    print(blue('put fle...'))
    with settings(warn_only=True):
        result = put('jinrong.py', '/home')
    if result.failed and not confirm('put file filed,Continue[Y/N]?'):
        abort('Aborting file put task!')


@task
def execute():
    with settings(warn_only=True):
        run('python /home/jinrong.py')

@task
def install():
    run('pip install paramiko')


@task
def scandir():
    run('yum install python-devel && yum install gcc')
    run('pip install scandir')


# 取回文件
@task
def get_file():
    print(yellow('get file ...'))
    with with_settings(warn_only=True):
        result = get('/home/jinrong', './')
    if result.failed and not confirm('get file filed,Continue[Y/N]?'):
        abort('Aborting file get task!')


@task
def go():
    putfile()
    execute()
