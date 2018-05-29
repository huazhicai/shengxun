# coding:utf-8
# Author: Seven

from fabric.api import *
from fabric.colors import *
from fabric.contrib.console import confirm

env.user = 'root'
env.port = '22'


env.hosts = ['jinlun1', 'jinlun2', 'jinlun3', 'jinlun4', 'jinlun5', 'jinlun6']


@task
def putfile():
    print(blue('put fle...'))
    with settings(warn_only=True):
        result = put('/home/blj/seven/financial/jinlun/jinrong.py', '/opt')
    if result.failed and not confirm('put file filed,Continue[Y/N]?'):
        abort('Aborting file put task!')


@task
def install():
    run('pip install paramiko')


@task
def execute():
    with settings(warn_only=True):
        run('python /opt/jinrong.py')


@task
def delete():
    with settings(warn_only):
        run('rm -rf /opt/jinrong.py')


@task
def go():
    putfile()
    install()
    execute()





