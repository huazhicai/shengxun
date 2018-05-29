# coding:utf-8

import requests
import json


def get_datas():
    phones = []
    response = requests.get('http://ai1.listenrobot.com/tool-callphone:sum/?minutes=5')
    r = response.content.decode()

    with open('./phone_data.txt', 'w') as f:
        f.write(r)

    result = json.loads(r)
    if result and 'data' in result.keys():
        for item in result.get('data'):
            tmp = item.keys()[0]
            phone = {"{#PHONENUMBER}": tmp}
            phones.append(phone)
        return json.dumps({"data": phones})


if __name__ == '__main__':
    results = get_datas()
    print(results)
