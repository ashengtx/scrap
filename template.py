# _*_ coding: utf-8 _*_
import os
import re
from urllib import parse, request
from bs4 import BeautifulSoup
import http.cookiejar
from PIL import Image
import cv2
import time
import random
import json
import hashlib

# 建立LWPCookieJar实例，可以存Set-Cookie3类型的文件。
# 而MozillaCookieJar类是存为'/.txt'格式的文件
cookie = http.cookiejar.LWPCookieJar('cookie')
# 若本地有cookie则不用再post数据了
try:
    cookie.load(ignore_discard=True)
except IOError:
    print('Cookie未加载！')

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36'}

opener = request.build_opener(request.HTTPCookieProcessor(cookie))
# 给openner添加headers, addheaders方法接受元组而非字典
opener.addheaders = [(key, value) for key, value in headers.items()]

base_url = 'http://www.zdic.net/c/cibs/'

foutput = open("output.txt", 'w', encoding='utf8')

def md5_encode(string):
    m = hashlib.md5()
    m.update(string.encode('utf8'))
    v=m.hexdigest()
    return v

def pwd_encode(pwd, username, captcha_code):
    c1 = md5_encode(pwd+username)
    return md5_encode(c1+captcha_code.lower())

def time_13():
    """
    13位时间毫秒序列
    """
    return str(round(time.time()*1000))

def my_open(url, post_data=None, encoding='utf8'):
    if post_data:
        return opener.open(url, post_data).read().decode(encoding)
    else:
        return opener.open(url).read().decode(encoding)

def html2dom(html):
    return BeautifulSoup(html, 'html.parser')

def main():
    url = base_url
    print(my_open(url))


if __name__ == '__main__':

    main()

