# coding:utf-8
# Author: Seven

from fabric.api import *
from fabric.colors import *
from fabric.contrib.console import confirm

env.user = 'root'
env.port = '22'
env.gateway = '192.168.20.5'

listen = ['192.168.20.40', '192.168.20.41', '192.168.20.88', 'root@dream1.listenrobot.cn:10022',
          'xiaoshouaim.synvn.com:10022', 'xiaoshouaim.synvn.com:10023']

ling = ['192.168.20.7', '192.168.20.9', '192.168.20.53', '192.168.20.13', '192.168.20.26', '192.168.20.28',
        '192.168.20.65', '192.168.20.35', '192.168.20.37', '192.168.20.52', '192.168.20.55', '192.168.20.68',
        '192.168.20.69', '192.168.20.70', '192.168.20.71', '192.168.20.86', '192.168.20.87', '192.168.20.89']

jinlun = ['jinlun2', 'jinlun3', 'jinlun4', 'jinlun5']

env.roledefs = {'listenrobot': listen, 'lingsheng': ling, 'jinlun': jinlun}

# 本地file移动到remote_dir
remote_dir = '/robotvoip/aim'
file = 'miko_sync.py'
sed = 'sed -i "s#command=python /robotvoip/aim/miko_sync.py#' \
      'command=python /robotvoip/aim/miko_sync.py {}#g" /etc/supervisord.conf'


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



@task
@roles('listenrobot')
def modify_listenrobot(web_ip='116.62.222.55', dir='/datahome/recordfile'):
    run(sed.format(web_ip))
    with cd('/robotvoip/aim/'):
        run('sed -i "s#/home/recordfle/#{}#g" miko_sync.py'.format(dir))


@task
@roles('lingsheng')
def modify_lingsheng(web_ip='47.97.175.17'):
    run(sed.format(web_ip))


@task
@roles('jinlun')
def modify_jinlun(web_ip='172.16.213.200'):
    run(sed.format(web_ip))


# 启动进程
@task
def start_miko_sync():
    run('supervisorctl reload')


@task
def go():
    put_file()
    modify_listenrobot()
    modify_jinlun()
    modify_lingsheng()
