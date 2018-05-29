# coding:utf-8
# Author: Seven

import os
import re

import paramiko

try:
    from os import scandir
except ImportError:
    from scandir import scandir

# 文件提取路径
with open('/robotvoip/yfs_compress.sh') as f:
    text = f.read()
    recordfilea_regex = re.compile(r'pcm_recordfile=(.*)')
    try:
        recordfile = recordfilea_regex.search(text)
        recordfile_pcm = recordfile.group(1)
    except Exception as e:
        print(str(e))
        recordfile_pcm = '/home/recordfile_pcm/'

# 文件传递到堡垒机
dst_dir = '/home/jinrong/'


# 连接堡垒机
def put_file():
    transport = paramiko.Transport(('jiangxi.listenrobot.cn', 1022))
    transport.connect(username='root', password='sdftd22')
    sftp = paramiko.SFTPClient.from_transport(transport)
    return sftp


def extract_recordfile():
    dir_entities = scandir(recordfile_pcm)
    jinrong_regex = re.compile(r'jinrong')
    sftp = put_file()
    for item in dir_entities:
        file = item.path
        name = item.name
        if jinrong_regex.search(file):
            if file.endswith('A.tar.gz'):
                sftp.put(file, ''.join([dst_dir, 'A/', name]))
                print('put: {}'.format(file))
            elif file.endswith('B.tar.gz'):
                sftp.put(file, ''.join([dst_dir, 'B/', name]))
                print('put: {}'.format(file))
            elif file.endswith('C.tar.gz'):
                sftp.put(file, ''.join([dst_dir, 'C/', name]))
                print('put: {}'.format(file))
            elif file.endswith('D.tar.gz'):
                sftp.put(file, ''.join([dst_dir, 'D/', name]))
                print('put: {}'.format(file))
            else:
                pass


if __name__ == '__main__':
    if os.path.exists(recordfile_pcm):
        extract_recordfile()
    else:
        recordfile_pcm = '/data/recordfile_pcm/'
        if os.path.exists(recordfile_pcm):
            extract_recordfile()
        else:
            print("recordfile_pcm not exits!")
