# coding:utf-8
# Author: Seven

import os
import re
import shutil


try:
    from os import scandir
except ImportError:
    from scandir import scandir

# 文件提取路径
with open('/robotvoip/yfs_compress.sh') as f:
    text = f.read()
    recordfilea_regex = re.compile(r'pcm_recordfile=(.*)')
    recordfile = recordfilea_regex.search(text)
    recordfile_pcm = recordfile.group(1)

# 文件存放路径
dst_dir = '/home/jinrong/'


def create_dir():
    if not os.path.exists(dst_dir):
        os.mkdir(dst_dir)
        os.chdir(dst_dir)
        os.mkdir('A')
        os.mkdir('B')
        os.mkdir('C')
        os.mkdir('D')


def extract_recordfile():
    dir_entities = scandir(recordfile_pcm)
    jinrong_regex = re.compile(r'jinrong')
    for item in dir_entities:
        file = item.path
        if jinrong_regex.search(file):
            if file.endswith('A.tar.gz'):
                shutil.copy(file, ''.join([dst_dir, 'A']))
                print(file)
            elif file.endswith('B.tar.gz'):
                shutil.copy(file, ''.join([dst_dir, 'B']))
                print(file)
            elif file.endswith('C.tar.gz'):
                shutil.copy(file, ''.join([dst_dir, 'C']))
                print(file)
            elif file.endswith('D.tar.gz'):
                shutil.copy(file, ''.join([dst_dir, 'D']))
                print(file)
            else:
                pass

if __name__ == '__main__':
    if os.path.exists(recordfile_pcm):
        create_dir()
        extract_recordfile()
    else:
        print("recordfile_pcm not exists!")
