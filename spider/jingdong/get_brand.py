import json

import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from json.decoder import JSONDecodeError

headers = {
    'Cookie': '__jdv=122270672|direct|-|none|-|1508414087689; ipLoc-djd=1-72-2799-0; qrsc=3; __jda=122270672.150841408768941475105.1508414088.1508419830.1508423471.3; __jdb=122270672.1.150841408768941475105|3.1508423471; __jdc=122270672; xtest=796.cf6b6759; rkv=V0700; __jdu=150841408768941475105; 3AB9D23F7A4B3C9B=6MKXVZ6FSDIBABKUKMEWZM7HAWKQDCAY57QPAGIHX37K7O7TQ3WRAPFMZMCPQI2ANBQVW3DQNIP3U2SJDJ7GKC7ZYQ',
    'Host': 'search.jd.com',
    'Origin': 'https://search.jd.com',
    'Referer': 'https://search.jd.com/Search?keyword=%E5%8F%A3%E7%BA%A2&enc=utf-8&wq=%E5%8F%A3%E7%BA%A2&pvid=84352b793782439f88bdedbf206d8f65',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}


def get_brand_index():
    # 向路由中出入参数
    url = 'https://search.jd.com/brand.php?keyword=%E5%8F%A3%E7%BA%A2&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=%E5%8F%A3%E7%BA%A2&stock=1'
    try:
        response = requests.get(url, headers)
        print(response.status_code)
        print(response.encoding)
        if response.status_code == 200:
            print('jieguo', response)
            return response.text
        return None
    except RequestException:
        print('请求索引页出错')
        return None


# 解析索引页的json数据，并提取详情页url
def parse_page_index(html):
    try:
        data = json.loads(html)
        if data and 'data' in data.keys():
            for item in data.get('data'):
                # 用生成器的方式,惰性获取详情页的url
                yield item.get('article_url')
    except JSONDecodeError:
        pass


def main():
    get_brand_index()


if __name__ == '__main__':
    main()
