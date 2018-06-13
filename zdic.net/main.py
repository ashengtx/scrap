# _*_ coding: utf-8 _*_
import os
import re
import pprint
from urllib import parse, request
import bs4
from bs4 import BeautifulSoup
import http.cookiejar
from PIL import Image
import cv2
import time
import random
import json
import hashlib
import pylab as plb

from multiprocessing import Pool, Process

from mythread import MyThread
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
poem_base_url = 'http://sc.zdic.net/'

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

    while (try_num > 0):
        try:
            html = my_open(url, post_data)
            return html
        except:
            print("retry connecting to {} for time {}".format(url, 6-try_num))
            return my_safe_open(url, post_data, try_num=try_num-1)
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

def code2text(code):
    m = {
        'j1':'解释',
        'cc':'出处',
        'lj':'例句',
        'jy':'',
        'fy':'',
        'yf':''
    }
    if m.get(code) is not None:
        return m[code]
    else:
        return False

def get_idiom_detail(idiom_url):
    """
    """
    idiom_detail = dict()
    idiom, url = idiom_url

    html = my_safe_open(url)
    bsobj = html2dom(html)

    pinyin = []

    if re.findall(r'<script>spc\("(.+?)"\);</script>', str(html)):
        pinyin = re.findall(r'<script>spc\("(.+?)"\);</script>', str(html))[0]
    else:
        print(idiom_url)
        print("这个成语没有拼音！！！！")
        return False

    paraphrases = dict()
    tag_dict = dict()
    res = re.findall(r'\#(zdic\d+) \{background: url\(/images/(.+?)\.gif\);\}', html)
    if res == []:
        print(idiom_url)
        print("这个页面没有tag gif")
    else:
        for i, name in res:
            code = name.split('_')[-1]
            tag_dict[i] = code2text(code)

    if re.findall(r'<p class="zdic\d"><i id="(.+?)">.*?</i>(.+?)</p>', html):
        res = re.findall(r'<p class="zdic\d"><i id="(.+?)">.*?</i>(.+?)</p>', html)
        for i, p in res:
            paraphrases[tag_dict[i]] = p
    idiom_detail['name'] = idiom
    idiom_detail['pinyin'] = pinyin
    idiom_detail['paraphrases'] = paraphrases

    return idiom_detail

def get_idiom_urls(char_index_urls):
    """
    根据字索引的url，获得该索引下所有的成语的url
    char_index_url: http://www.zdic.net/c/cybs/ci/?z=%E4%B8%B0
    """
    idiom_urls = []
    
    n = 0
    url_num = len(char_index_urls)
    for char_index_url in char_index_urls:
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
            res = re.findall(r'<a href="(.+?)".*?>(.+?)</a>', str(li))
            suffix = res[0][0]
            idiom = res[0][1]
            idiom_url = base_url + suffix
            idiom_urls.append((idiom, idiom_url))
        n += 1
        if n % 100 == 0:
            print('{}/{}'.format(n, url_num))
    return idiom_urls

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

def get_all_idiom_details():

    time_start = time.time()
    file_idioms = open("result/idiom_details.json", 'w', encoding='utf8')

    url = idiom_base_url
    html = my_open(url)
    bsobj = html2dom(html)
    radicals = get_radicals(bsobj)
    radical_urls =  get_radical_urls(radicals, idiom_base_url)
    chars = get_char_index_url_suffix(radical_urls, cy_referer)
    char_index_urls = get_char_urls(chars)

    idiom_urls = get_idiom_urls(char_index_urls[0:1])
    idiom_url_num = len(idiom_urls)
    print("start scraping idioms at time {}".format(round(time.time()-time_start)))
    thread_num = 4
    batch_num = idiom_url_num // thread_num
    threads = []
    for m in range(thread_num):
        if m == thread_num - 1:
            urls = idiom_urls[m*batch_num:]
        else:
            urls = idiom_urls[m*batch_num:(m+1)*batch_num]
        t = MyThread(threadID=m, name="Thread-"+str(m), urls=urls, func=get_idiom_detail)
        t.start()
        threads.append(t)

    all_idiom_details = dict()
    for thread in threads:
        thread.join() # 这个线程完成之后，才执行下面的代码
        for item in thread.results:
            if item['name'] in all_idiom_details.keys():
                print(item['name'])
            all_idiom_details[item['name']] = item
    json.dump(all_idiom_details, file_idioms, ensure_ascii=False, indent='\t')
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
    return [(zi_url, zi)]
    """
    zi_urls = []
    for t1, t2 in zis:
        zi_url = base_url + t1
        zi_urls.append((t2, zi_url))
    return zi_urls

def filter_paraphrase(string):
    return string.replace('◎', '')

def get_zi_paraphrases(bsobj):
    """
    http://www.zdic.net/z/28/js/99F1.htm 这个字有一行丢了</p>标签，无解
    http://www.zdic.net/z/28/js/9AEE.htm
    """
    paraphrases = dict()
    tab_page = bsobj.find('div', {'class':'tab-page'})

    if '暂无解释，欢迎补充。' in tab_page.get_text():
        return False

    pinyin = ''
    paraphrase = []
    paraphrase_begin = False
    paraphrase_end = False
    #pattern = re.compile(r'(<p.*?</p>)', re.S)
    #p_tags = pattern.findall(str(tab_page))
    #print(p_tags)
    for child in tab_page:
        # if type(child) is bs4.element.Tag:
        #     print(child)
        #     print()
        #     text = child.get_text()
        #     #print(text+'\n')
        if paraphrase_begin:
            if 'zdic.net' in str(child).lower() or re.findall(r'<strong>.+?</strong>', str(child)):
                # 收集完一个拼音的释义
                paraphrase_begin = False
                paraphrase_end = True
            else:
                if type(child) is bs4.element.Tag:
                    text = child.get_text().strip()
                    #print("===========text==========")
                    #print(text)
                    if text.startswith('◎'):
                        # ◎开头说明只有一条释义，直接结束
                        paraphrase_begin = False
                        paraphrase_end = True
                        text = filter_paraphrase(text).strip()
                        paraphrase.append(text)
                    elif ''.join(re.split(r'\W+', text)) in ['汉典', '漢典']:
                        paraphrase_begin = False
                        paraphrase_end = True
                    else:
                        text = filter_paraphrase(text).strip()
                        paraphrase.append(text)
        else:
            if re.findall(r'<script>spz\("(.+?)"\);</script>', str(child)):
                # 匹配到拼音，开始收集释义
                pinyin = re.findall(r'<script>spz\("(.+?)"\);</script>', str(child))[0]
                paraphrase_begin = True
                #print(pinyin)
                continue
            elif re.findall(r'<span class="dicpy">(.+?)</span>', str(child)):
                # 这种情况有的拼音还写错了，要到上面去找
                # http://www.zdic.net/z/1c/js/6C62.htm
                td = bsobj.find('td', {'class':'z_i_t2_py'})
                if re.findall(r'<script>spz\("(.+?)"\);</script>', str(td)):
                    pinyin = re.findall(r'<script>spz\("(.+?)"\);</script>', str(td))[0]
                    paraphrase_begin = True
                    continue
                elif re.findall(r'<a href="/z/pyjs/\?py=" target="_blank">(.+?)</a>', str(td)): 
                    pinyin = re.findall(r'<a href="/z/pyjs/\?py=" target="_blank">(.+?)</a>', str(td))[0]
                    paraphrase_begin = True
                    continue

        if paraphrase_end:
            paraphrases[pinyin] = paraphrase
            pinyin = ''
            paraphrase = []
            paraphrase_end = False
    if pinyin != '' and paraphrase != []:
        paraphrases[pinyin] = paraphrase
    #pprint.pprint(paraphrases)
    return paraphrases

def get_zi_detail(zi_url):
    """
    根据每个字的url，解析每个字的详细信息
    """
    zi = dict()
    zi_char, url = zi_url

    html = my_safe_open(url)
    bsobj = html2dom(html)

    pinyin = []
    try:
        spans = bsobj.find('td', {'class':'z_i_t2_py'}).find_all('span', {'class':'dicpy'})
    except:
        #print(url)
        return False
    for span in spans:
        if re.findall(r'<script>spz\("(.+?)"\);</script>', str(span)):
            res = re.findall(r'<script>spz\("(.+?)"\);</script>', str(span))
            if len(res) == 1:
                pinyin.append(res[0])
            else:
                print(zi_url)
                print("出错啦！！！！！！！！！！")
        elif re.findall(r'<a href="/z/pyjs/\?py=" target="_blank">(.+?)</a>', str(span)): 
            res = re.findall(r'<a href="/z/pyjs/\?py=" target="_blank">(.+?)</a>', str(span))
            if len(res) == 1:
                pinyin.append(res[0])
            else:
                print(zi_url)
                print("出错啦！！！！！！！！！！")
        else:
            print(zi_url)
            print("没找到！！！！！！！！！！")

    zi['zi_char'] = zi_char
    zi['pinyin'] = pinyin
    
    paraphrases = get_zi_paraphrases(bsobj)
    if paraphrases == False:
        p = dict()
        p[pinyin[0]] = ['暂无释义']
        zi['paraphrases'] = p
    else:
        zi['paraphrases'] = paraphrases

    return zi

def test_get_zi_detail():
    print('==========test get zi detail===========')
    zi_url = 'http://www.zdic.net/z/25/js/8FA6.htm'
    res = get_zi_detail((0, zi_url))
    pprint.pprint(res)

def get_all_zis():
    """
    总共有38608个字
    常用字10630
    """
    time_start = time.time()
    file_zi_detail = open("result/zi_details.json", 'w')

    url = zi_base_url
    html = my_safe_open(url)
    bsobj = html2dom(html)
    radicals = get_radicals(bsobj)
    radical_urls =  get_radical_urls(radicals, zi_base_url)

    zis = get_zis(radical_urls, zi_referer)
    zi_urls = get_zi_urls(zis)

    #zi_urls = zi_urls[:100]
    zi_urls = zi_urls

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

    all_zis = dict()
    for thread in threads:
        thread.join() # 这个线程完成之后，才执行下面的代码
        for item in thread.results:
            all_zis[item['zi_char']] = item
    
    json.dump(all_zis, file_zi_detail, ensure_ascii=False, indent='\t')

    file_zi_detail.close()

def test_zi_detail():
    file_zi_detail = open('./result/zi_details.json', 'r')
    data = json.load(file_zi_detail)

    empty_num = 0
    total_num = 0
    for zi in data:
        total_num += 1
        if len(data[zi]['paraphrases'].keys()) == 0:
            empty_num += 1
            pprint.pprint(data[zi])
    print(empty_num, total_num)


def get_all_poems():
    time_start = time.time()
    file_idioms = open("result/poems.txt", 'w', encoding='utf8')

    url = poem_base_url
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


def main():
    get_all_idiom_details()

if __name__ == '__main__':

    main()

