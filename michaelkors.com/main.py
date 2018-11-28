import os, json, time
import requests
import pprint

url = 'https://www.michaelkors.com/server/data/product?productId=US_32T8GF5C0T'

url_inventory = 'https://www.michaelkors.com/server/productinventory?productList=US_MH88Y88AFT'

proxies = {
    'https': 'https://127.0.0.1:9999',
    'http': 'http://127.0.0.1:9999'
}

headers = {
    # 'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Upgrade-Insecure-Requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
}

response = requests.get(url, proxies=proxies, verify=False, headers=headers)
pprint.pprint(json.loads(response.text))

if __name__ == '__main__':

    pass
