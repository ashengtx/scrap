"""
盒宫大会
http://hg.jfbapp.cn/quiz/

http://hg.jfbapp.cn/quiz/5 是第一期
8是第二期
18是第十二期

"""
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
import pylab as plb

# 建立LWPCookieJar实例，可以存Set-Cookie3类型的文件。
# 而MozillaCookieJar类是存为'/.txt'格式的文件
cookie = http.cookiejar.LWPCookieJar('cookie')
# 若本地有cookie则不用再post数据了
try:
    cookie.load(ignore_discard=True)
except IOError:
    print('Cookie未加载！')

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36'
           }
opener = request.build_opener(request.HTTPCookieProcessor(cookie))
# 给openner添加headers, addheaders方法接受元组而非字典
opener.addheaders = [(key, value) for key, value in headers.items()]

base_url = 'https://api-staging.jfbapp.cn/quiz/'

foutput = open("output.txt", 'w', encoding='utf8')

PHONE_NUMBER = '15606069771'
DC = 86 # 国际区号

def md5_encode(string):
    m = hashlib.md5()
    m.update(string.encode('utf8'))
    v=m.hexdigest()
    return v

def pwd_encode(pwd, username, captcha_code):
    c1 = md5_encode(pwd+username)
    return md5_encode(c1+captcha_code.lower())

def time_13():
    return str(round(time.time()*1000))

def my_open(url, post_data=None, encoding='utf8'):
    if post_data:
        return opener.open(url, post_data).read().decode(encoding)
    else:
        return opener.open(url).read().decode(encoding)


def login(phone_number=PHONE_NUMBER):
    """
    输入自己的账号密码，模拟登录知乎
    """
    data = {
        'mobile': phone_number
    }
    
    # 获取验证码        
    captcha_code = get_captcha(phone_number)
    quit()
    data['verification'] = captcha_code
    post_data = parse.urlencode(data).encode('utf8')

    login_url = base_url + 'account/login'
    res = my_open(login_url)
    print(res)
    quit()
    # 保存cookie到本地
    cookie.save(ignore_discard=True, ignore_expires=True)

    find_result = re.findall(r'"UserName":"(.*?)\|', res)
    print(find_result)
    if find_result != [] and find_result[0] == username:
        print("登录成功")
        return True
    else:
        print("登陆失败")
        print(res, file=foutput)
        return False

def get_photo_score_by_stage(stage_num='8'):
    """
    获取每期的照片链接和分数
    """
    url = base_url + str(stage_num)
    try:
        res = my_open(url)
    except Exception as e:
        print(e)
        return False
    data = json.loads(res)
    stage = data['quiz']['title'] # 第几期
    if not os.path.isdir(stage):
        os.mkdir(stage)

    questions = data['questions']
    for q in questions:
        q_id = q['id']
        q_score = q['avgScore']
        q_url = q['image']
        image = get_photo(q_url)
        image_name = stage + '/' + q_id + '-' + str(q_score) + '.jpg'
        with open(image_name, 'wb') as f:
            f.write(image)
    '''
    print(data)
    print(data.keys())
    print(data['quiz'])
    print(data['questions'])'''

def test_get_photo_score_by_stage(stage_num = '18'):
    
    url = base_url + str(stage_num)
    try:
        res = my_open(url)
    except Exception as e:
        print(e.code)
        return False
    data = json.loads(res)
    stage = data['quiz']['title'] # 第几期
    print(stage)

def get_photo(url):
    """
    根据照片url获取照片，保存到本地
    """
    #url = 'https://i1.jfbapp.cn/ping/question/image/ef8950bb-258d-43a7-ae60-04de713bc80e.jpg'
    image_data = opener.open(url).read()
    return image_data
    '''
    with open('test.jpg', 'wb') as f:
        f.write(image_data)
    im = Image.open('test.jpg')
    im.show()'''

def get_photo_score():
    for stage_num in range(5, 19):
        get_photo_score_by_stage(stage_num)

if __name__ == '__main__':
    #test_get_photo_score_by_stage(6)
    get_photo_score()

