import pprint
import requests

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
}

def params2dict(s):
    """
    :param s:
    :return:
    >>> s = 'typeId=0&timestamp=1542941455874&rankSort=100'
    >>> print(params2dict(s))
    >>> {'rankSort': '100', 'timestamp': '1542941455874', 'typeId': '0'}
    """
    d = {}
    for kv in s.split('&'):
        k, v = kv.split('=')
        d[k]=v
    return d

def download_img(url):
    """
    https://img1.cohimg.net/is/image/Coach/54466_blk_a0?fmt=jpeg&wid=727&hei=727&bgc=240,240,240&qlt=85,0&op_sharpen=1&resMode=bicub&op_usm=0,0,0,0&iccEmbed=0&fit=hfit
    :param url:
    :return:
    """
    with open('test.jpg', 'wb') as fout:
        fout.write(requests.get(url, headers=headers).content)

if __name__ == '__main__':
    url = 'http://img1.cohimg.net/is/image/Coach/54466_blk_a0?fmt=jpeg&wid=727&hei=727&bgc=240,240,240&qlt=85,0&op_sharpen=1&resMode=bicub&op_usm=0,0,0,0&iccEmbed=0&fit=hfit'
    download_img(url)