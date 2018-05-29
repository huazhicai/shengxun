# coding:utf-8

import json

phone = '3_13205002583_5'
tag = 'D'


with open('./phone_data.txt') as f:
        result = json.load(f)


def extract_datas():
    if result and 'data' in result.keys():
        for item in result.get('data'):
            key = item.keys()[0]
            if key == phone:
                return item.values()[0].get(tag)


if __name__ == '__main__':
    print(extract_datas())
