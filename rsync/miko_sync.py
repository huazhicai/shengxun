#!/usr/bin/env python
# coding:utf-8
# Author: Seven
import json
import os
import time
import logging
import smtplib
from email.mime.text import MIMEText
import sys

import paramiko
import shutil

try:
    from os import scandir
except ImportError:
    from scandir import scandir
logging.basicConfig(level=logging.INFO, format='%(asctime)s-%(levelname)s-%(message)s')
remote_ip = sys.argv[1]


"""注意:检查web服务器录音文件的存放路径,而且最后斜线必须加!!!!"""
remote_dir = '/home/recordfile/'


# 读取ai配置文件里录音的路径,ai产生录音的文件夹
with open('/robotvoip/ai_cfg.txt') as f:
    config = json.load(f)
    recordfile_dir = config["compress_dest_dir"]

# 本机备份录音文件的路径
recordfile_bak = '/data/recordfile_bak'


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
        self.sftp = self._sftp_client

    def send_email(self, sub, content):
        mailto_list = ["sa@lsrobot.vip"]
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

    @property
    def _sftp_client(self):
        """用paramiko.SFTPClient对象在不同的服务器间传递文件"""
        transport = paramiko.Transport(remote_ip, 22)
        try:
            private_key = paramiko.RSAKey.from_private_key_file('/root/.ssh/id_rsa')
            transport.connect(username="root", pkey=private_key)
        except Exception as e:
            logging.warning(str(e))
            host_name = os.popen('hostname').read().strip()
            self.send_email(host_name, "Connection failed, \nchecks the remote network or  local id_rsa.pub")
            transport.connect(username='root', password=os.getenv('PASSWORD'))  # 密码连接
        sftp = paramiko.SFTPClient.from_transport(transport)
        return sftp

    def sync(self):
        dir_entities = scandir(self.recordfile_dir)  # 默认按照时间循序排序
        for dir_entity in dir_entities:
            path = dir_entity.path
            file_name = dir_entity.name
            name = path[-3:]
            if name == 'tar':
                cur_time = time.time()
                m_time = os.path.getmtime(path)
                if cur_time - m_time > 5:
                    try:
                        self.sftp.put(path, ''.join([remote_dir, file_name]))
                        logging.info('%s has been copy to %s ' % (path, self.scp_dst))
                        shutil.move(path, self.mv_dst)
                        logging.info('%s has been moved to %s ' % (path, self.mv_dst))
                    except Exception as e:
                        logging.error(str(e))
                        time.sleep(5)
                        self.sftp = self._sftp_client
                        # break  


def main():
    sync_record = SyncRecord()
    while True:
        sync_record.sync()
        time.sleep(0.1)


if __name__ == '__main__':
    main()
