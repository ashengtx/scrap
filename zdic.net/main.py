# _*_ coding: utf-8 _*_
import os
import re
from urllib import parse, request
from bs4 import BeautifulSoup
import http.cookiejar
from PIL import Image
import cv2
import time
import threading
import random
import json
import hashlib
import pylab as plb

from multiprocessing import Pool, Process
"""
这里用char表示字
用word表示词语
"""

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

base_url = 'http://www.zdic.net/'
zi_base_url = 'http://www.zdic.net/z/jbs/'
word_base_url = 'http://www.zdic.net/c/cibs/'
idiom_base_url = 'http://www.zdic.net/c/cybs/'
words_api_base = 'http://www.zdic.net/c/cibs/ci/sc/?z='
idiom_api_base = 'http://www.zdic.net/c/cybs/ci/sc/?z='

zi_referer = 'http://www.zdic.net/z/jbs/'
ci_referer = 'http://www.zdic.net/c/cibs/'
cy_referer = 'http://www.zdic.net/c/cybs/'


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

def update_headers(new_headers):
    opener.addheaders = [(key, value) for key, value in new_headers.items()]

def my_open(url, post_data=None, encoding='utf8'):
    if post_data:
        return opener.open(url, post_data).read().decode(encoding)
    else:
        return opener.open(url).read().decode(encoding)

def my_safe_open(url, post_data=None, encoding='utf8', try_num=5):
    """
    有时候网络原因my_open会连不上而抛出异常，my_safe_open，多尝试几次
    """
    while try_num > 0:
        try:
            html = my_open(url, post_data)
            return html
        except:
            my_safe_open(url, post_data, try_num=try_num-1)
    return False

def html2dom(html):
    return BeautifulSoup(html, 'html.parser')

def get_radicals(bsobj):
    """
    获得所有部首的url后缀
    """
    radicals = []
    table = bsobj.find('table')
    divs = table.find_all('div', {'class':'bsul'})
    for div in divs:
        lis = div.find_all('li')
        for li in lis:
            res = re.findall(r'<a .*?"shd\((\d+),\'(.*?)\'\);">(.*?)<\/a>', str(li))
            radicals.append(res[0])
    return radicals

def get_radical_urls(radicals, base):
    """
    获得所有部首索引的url
    radical: (笔画数，部首url编码，部首)
    """
    radical_urls = []
    radical_base_url = base + 'bs/?bs='
    for t1, t2, t3 in radicals:
        radical_url = radical_base_url + t2
        radical_urls.append(radical_url)
    return radical_urls

def get_char_index_url_suffix(radical_urls, referer=ci_referer):
    """
    根据所有部首索引的url，获得所有的字索引的url后缀
    """
    new_headers = headers.copy()
    new_headers['Referer'] = referer
    update_headers(new_headers)
    chars = []
    for url in radical_urls:
        html = my_open(url)
        bsobj = html2dom(html)
        lis = bsobj.find('div', {'class':'zlist'}).find_all('li')
        for li in lis:
            res = re.findall(r'<a href="(.*?)".*?>(.*?)<\/a>', str(li))
            chars.append(res[0])
    return chars

def get_char_urls(chars):
    """
    根据所有的字索引的url后缀，获得所有字索引的url
    """
    char_urls = []
    char_base_url = word_base_url
    for t1, t2 in chars:
        char_url = char_base_url + t1
        char_urls.append(char_url)
    return char_urls

def get_words(char_url):
    """
    根据字索引的url，获得所有的词语
    http://www.zdic.net/c/cibs/ci/?z=%E4%B8%AB
    """
    words = []
    
    # 请求的referer是char_url
    new_headers = headers.copy()
    new_headers['Referer'] = char_url
    update_headers(new_headers)

    char = char_url.split('z=')[1]
    api_url = words_api_base + char
    html = my_open(api_url)
    bsobj = html2dom(html)
    lis = bsobj.find('div', {'class':'zlist'}).find_all('li')
    for li in lis:
        word = li.find('a').get_text()
        words.append(word)
        
    return words

def get_all_words():
    """
    900 seconds
    """
    time_start = time.time()
    fwords = open("result/words.txt", 'w', encoding='utf8')

    url = base_url
    html = my_open(url)
    bsobj = html2dom(html)
    radicals = get_radicals(bsobj)
    radical_urls =  get_radical_urls(radicals, word_base_url)
    chars = get_char_index_url_suffix(radical_urls, ci_referer)
    char_urls = get_char_urls(chars)
    
    all_words = []
    char_num = len(char_urls)
    n = 0
    print("start scraping words at time {}".format(round(time.time()-time_start)))
    for char_url in char_urls:
        words = get_words(char_url)
        all_words.extend(words)
        n += 1
        if n % 100 == 0:
            print("{}/{} finished at time {}".format(n, char_num, round(time.time()-time_start)))
    print(len(all_words))
    for word in all_words:
        print(word, file=fwords)

class MyThread(threading.Thread):
    def __init__(self, threadID, name, urls, func=get_words):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.urls = urls
        self.func = func
        self.results = []

    def run(self):
        print("Starting " + self.name)
        time_start = time.time()
        n = 0
        total_num = len(self.urls)
        for url in self.urls:
            res = self.func(url)
            if not res:
                print(url, 'failed')
            else:
                if type(res) is dict: # 返回结果是dict
                    self.results.append(res)
                elif type(res) is list: # 返回结果是list
                    self.results.extend(res)
                else:
                    print('invalid type return')
            n += 1
            if n % 100 == 0:
                print("{} scrap {}/{} urls cost {} seconds.".format(self.name, n, total_num, round(time.time()-time_start)))
        print("{}: {} words finished cost {} seconds".format(self.name, len(self.results), round(time.time()-time_start)))
        print("Exiting " + self.name)

class MyProcess(Process):

    def __init__(self, processID, name, urls):
        Process.__init__(self)
        self.processID = processID
        self.name = name
        self.urls = urls
        self.all_words = []
    def run(self):
        print("Starting " + self.name)
        time_start = time.time()
        batch_words = []
        n = 0
        total_num = len(self.urls)
        for url in self.urls:
            words = get_words(url)
            batch_words.extend(words)
            n += 1
            if n % 100 == 0:
                print("{} scrap {}/{} urls cost {} seconds.".format(self.name, n, total_num, round(time.time()-time_start)))
        print("{}: {} words finished cost {} seconds".format(self.name, len(batch_words), round(time.time()-time_start)))
        print("Exiting " + self.name)
        self.all_words.extend(batch_words)

def get_all_words_multi_threading():
    """
    thread_num 2 cost time 414-27=387
    thread_num 3 cost time 321-16=305
    thread_num 4 cost time 309-26=283
    thread_num 5 cost time 314-28=286
    thread_num 8 cost time 313-26=287
    thread_num 16 cost time 304-22=282
    """
    time_start = time.time()
    fwords = open("result/words3.txt", 'w', encoding='utf8')

    url = word_base_url
    html = my_open(url)
    bsobj = html2dom(html)
    radicals = get_radicals(bsobj)
    radical_urls =  get_radical_urls(radicals, word_base_url)
    chars = get_char_index_url_suffix(radical_urls)
    char_urls = get_char_urls(chars)

    char_url_num = len(char_urls)
    print("start scraping words at time {}".format(round(time.time()-time_start)))
    thread_num = 2
    batch_num = char_url_num // thread_num
    threads = []
    for m in range(thread_num):
        if m == thread_num - 1:
            urls = char_urls[m*batch_num:]
        else:
            urls = char_urls[m*batch_num:(m+1)*batch_num]
        t = MyThread(threadID=m, name="Thread-"+str(m), urls=urls)
        t.start()
        threads.append(t)

    for thread in threads:
        thread.join() # 这个线程完成之后，才执行下面的代码
        for word in thread.all_words:
            print(word, file=fwords)
    print("finished at time {}".format(round(time.time()-time_start)))

def get_all_words_multi_processing():
    """
    """
    time_start = time.time()
    fwords = open("result/words3.txt", 'w', encoding='utf8')

    url = word_base_url
    html = my_open(url)
    bsobj = html2dom(html)
    radicals = get_radicals(bsobj)
    radical_urls =  get_radical_urls(radicals, word_base_url)
    chars = get_char_index_url_suffix(radical_urls)
    char_urls = get_char_urls(chars)

    char_url_num = len(char_urls)
    print("start scraping words at time {}".format(round(time.time()-time_start)))
    process_num = 4
    batch_num = char_url_num // process_num
    processes = []
    for m in range(process_num):
        if m == process_num - 1:
            urls = char_urls[m*batch_num:]
        else:
            urls = char_urls[m*batch_num:(m+1)*batch_num]
        p = MyProcess(processID=m, name="Process-"+str(m), urls=urls)
        p.start()
        processes.append(t)

    for process in processes:
        process.join() # 这个线程完成之后，才执行下面的代码
        for word in process.all_words:
            print(word, file=fwords)
    print("finished at time {}".format(round(time.time()-time_start)))

def get_idioms(char_index_url):
    """
    根据字索引的url，获得该索引下所有的成语
    char_index_url: http://www.zdic.net/c/cybs/ci/?z=%E4%B8%B0
    """
    idioms = []
    
    # 请求的referer是char_url
    new_headers = headers.copy()
    new_headers['Referer'] = char_index_url
    update_headers(new_headers)

    char = char_index_url.split('z=')[1]
    api_url = idiom_api_base + char
    html = my_open(api_url)
    bsobj = html2dom(html)
    lis = bsobj.find('div', {'class':'zlist'}).find_all('li')
    for li in lis:
        word = li.find('a').get_text()
        idioms.append(word)
    return idioms

def get_all_idioms():

    time_start = time.time()
    file_idioms = open("result/idioms.txt", 'w', encoding='utf8')

    url = idiom_base_url
    html = my_open(url)
    bsobj = html2dom(html)
    radicals = get_radicals(bsobj)
    radical_urls =  get_radical_urls(radicals, idiom_base_url)
    chars = get_char_index_url_suffix(radical_urls, cy_referer)
    char_urls = get_char_urls(chars)

    char_url_num = len(char_urls)
    print("start scraping idioms at time {}".format(round(time.time()-time_start)))
    thread_num = 4
    batch_num = char_url_num // thread_num
    threads = []
    for m in range(thread_num):
        if m == thread_num - 1:
            urls = char_urls[m*batch_num:]
        else:
            urls = char_urls[m*batch_num:(m+1)*batch_num]
        t = MyThread(threadID=m, name="Thread-"+str(m), urls=urls, func=get_idioms)
        t.start()
        threads.append(t)

    for thread in threads:
        thread.join() # 这个线程完成之后，才执行下面的代码
        for idiom in thread.all_words:
            print(idiom, file=file_idioms)
    file_idioms.close()
    print("finished at time {}".format(round(time.time()-time_start)))

def get_zis(radical_urls, referer):
    """
    有些字是非常用字，第二项是一个图片的url
    """
    new_headers = headers.copy()
    new_headers['Referer'] = referer
    update_headers(new_headers)
    zis = []
    for url in radical_urls:
        html = my_open(url)
        bsobj = html2dom(html)
        lis = bsobj.find('div', {'class':'zlist'}).find_all('li')
        for li in lis:
            res = re.findall(r'<a href="(.*?)".*?>(.*?)<\/a>', str(li))
            if len(res[0][1].strip()) == 1:
                zis.append(res[0])
    return zis

def get_zi_urls(zis):
    """

    """
    zi_urls = []
    for t1, t2 in zis:
        zi_url = base_url + t1
        zi_urls.append(zi_url)
    return zi_urls

def get_zi_detail(zi_url):
    """
    根据每个字的url，解析每个字的详细信息
    """
    zi = dict()
    url = zi_url
    html = my_safe_open(url)
    bsobj = html2dom(html)

    pinyin = []
    try:
        spans = bsobj.find('td', {'class':'z_i_t2_py'}).find_all('span', {'class':'dicpy'})
    except:
        print(url)
        return False
    for span in spans:
        res = re.findall(r'<span.*?py=(.+?)".*?span>', str(span))
        if len(res) == 1:
            pinyin.append(res[0])
        else:
            print("出错啦！！！！！！！！！！")

    zi['pinyin'] = pinyin

    return zi

def get_all_zis():
    """
    总共有38608个字
    常用字10630
    """
    time_start = time.time()
    file_zi_detail = open("result/zi_details.txt", 'w', encoding='utf8')

    url = zi_base_url
    html = my_safe_open(url)
    bsobj = html2dom(html)
    radicals = get_radicals(bsobj)
    radical_urls =  get_radical_urls(radicals, zi_base_url)

    zis = get_zis(radical_urls, zi_referer)
    zi_urls = get_zi_urls(zis)

    #get_zi_detail(zi_urls[0])
    #zi_url = 'http://www.zdic.net/z/25/js/8FD8.htm'
    #get_zi_detail(zi_url)

    zi_url_num = len(zi_urls)
    print("start scraping zi at time {}".format(round(time.time()-time_start)))
    thread_num = 4
    batch_num = zi_url_num // thread_num
    threads = []
    for m in range(thread_num):
        if m == thread_num - 1:
            urls = zi_urls[m*batch_num:]
        else:
            urls = zi_urls[m*batch_num:(m+1)*batch_num]
        t = MyThread(threadID=m, name="Thread-"+str(m), urls=urls, func=get_zi_detail)
        t.start()
        threads.append(t)

    for thread in threads:
        thread.join() # 这个线程完成之后，才执行下面的代码
        for zi_detail in thread.results:
            json.dump(zi_detail, file_zi_detail)

    file_zi_detail.close()


def main():
    get_all_zis()

if __name__ == '__main__':

    main()

