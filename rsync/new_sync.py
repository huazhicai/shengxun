#!/usr/bin/env python
# coding:utf-8
# author: dainel & Seven
import json
import os
from operator import methodcaller
import time
from datetime import datetime
import logging
import smtplib
from email.mime.text import MIMEText
# from logging.handlers import TimedRotatingFileHandler
import sys
import subprocess

try:
    from os import scandir
except ImportError:
    from scandir import scandir

remote_ip = sys.argv[1]
logging.basicConfig(level=logging.INFO, format='%(asctime)s-%(levelname)s-%(message)s')

# 读取ai配置文件里录音的路径,ai产生录音的文件夹
with open('/robotvoip/ai_cfg.txt') as f:
    config = json.load(f)
    recordfile_dir = config["compress_dest_dir"]

# 本机备份录音文件的路径
recordfile_bak = '/data/recordfile_bak'


""" 注意:web服务器录音文件的存放路径,需手动修改"""
remote_dir = '/home/recordfile/'


class SyncRecord(object):
    """上传录音的程序"""

    def __init__(self):
        if not os.path.exists(recordfile_dir):
            os.mkdir(recordfile_dir)
        self.recordfile_dir = recordfile_dir
        if not os.path.exists(recordfile_bak):
            os.mkdir(recordfile_bak)
        self.mv_dst = recordfile_bak
        self.scp_dst = 'root@{0}:{1}'.format(remote_ip, remote_dir)

    def send_email(self, sub, content):
        mailto_list = ["sa@lsrobot.vip"]
        # 设置服务器，用户名、口令
        mail_server = "smtp.exmail.qq.com"
        mail_user = "caizhihua@lsrobot.vip"
        mail_passwd = "Listenrobot123"

        msg = MIMEText(content, 'html', 'utf-8')
        msg['Subject'] = sub
        msg['From'] = mail_user + "<new_sync>"
        msg['To'] = ",".join(mailto_list)
        try:
            server = smtplib.SMTP()
            server.connect(mail_server)
            server.login(mail_user, mail_passwd)
            server.sendmail(mail_user, mailto_list, msg.as_string())
            server.close()
            return True
        except Exception as e:
            logging.error("Email failed:" + str(e))
            return False

    def sync(self):
        dir_entities = scandir(self.recordfile_dir)
        # 按inode的modifytime排序，时间倒叙
        # dir_entities = sorted(dir_entities, key=methodcaller('inode'))
        # 遍历文件夹'/home/recordfile'内的所有文件
        for dir_entity in dir_entities:
            path = dir_entity.path
            name = path[-3:]
            if name == 'tar':
                cur_time = time.time()
                m_time = os.path.getmtime(path)
                # 复制一分钟前的文件到远程服务器
                if cur_time - m_time > 10:
                    try:
                        scp_cmd = 'scp %s %s' % (path, self.scp_dst)
                        subprocess.check_call(scp_cmd, shell=True)
                        logging.info('%s has been copy to %s ' % (path, self.scp_dst))
                        # 复制成功后的文件移到备份目录中
                        try:
                            mv_cmd = 'mv %s %s' % (path, self.mv_dst)
                            subprocess.check_call(mv_cmd, shell=True)
                            logging.info('%s has been moved to %s ' % (path, self.mv_dst))
                        except subprocess.CalledProcessError as e:
                            # 移动文件失败，应该是根目录磁盘满了，发邮件警告
                            logging.error(str(e) + "move failed")
                            host_name = os.popen('hostname').read().strip()
                            self.send_email(host_name,
                                            'Failed move %s to %s, program will halt 10 minutes or manaul stop process'
                                            % (path, self.mv_dst))
                            time.sleep(400)
                            # 根目录磁盘满了,退出进程
                            # sys.exit()
                    except subprocess.CalledProcessError as e:
                        # 复制到远程失败，发送警告邮件
                        logging.error(str(e))
                        host_name = os.popen('hostname').read().strip()
                        message1 = '%s: %s, Failed transfer %s to %s \n' % (
                            datetime.now(), e, path, self.scp_dst)
                        message2 = "The program sleeps for 10 minutes and checks the network and id_rsa.pub"
                        self.send_email(host_name, message1 + message2)
                        # 程序休眠10分钟，检查网络
                        time.sleep(400)
            # else:
                # 非tar包文件，直接移到备份目录'/recordfile_bak'
                # subprocess.check_call('mv %s %s' % (dir_entity.path, self.mv_dst), shell=True)
                # logging.warning('%s has been move to %s' % (dir_entity.path, self.mv_dst))


def main():
    # 日志回滚
    # logging.basicConfig()
    # logger = logging.getLogger('logger')
    # logger.setLevel(logging.INFO)
    # if not os.path.exists('./log'):
    #     os.mkdir("./log")
    # # 创建日志处理对象，保留5天内的日志
    # timefile_handler = TimedRotatingFileHandler('log/sync.log', when='MIDNIGHT', interval=1, backupCount=5)
    # timefile_handler.suffix = "%Y-%m-%d"
    # formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    # timefile_handler.setFormatter(formatter)
    # logger.addHandler(timefile_handler)

    sync_record = SyncRecord()
    while True:
        sync_record.sync()
        time.sleep(0.1)


if __name__ == '__main__':
    main()
