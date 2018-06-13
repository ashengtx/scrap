import os, re
import time
import json
import pprint

import numpy as np

from collections import OrderedDict

from scraper import Scraper
from mythread2 import MyThread

poem_base_url = 'http://sc.zdic.net'

file_log = open('log.txt', 'w', encoding='utf8')

def now():
    return time.strftime("%H:%M:%S", time.localtime(int(time.time())))

def get_dynasty(html):
    """
    从首页获得朝代的链接
    """
    try:
        res = re.findall(r'<a href="(/shiren/.+?/)">(.+?)</a>', html)
    except:
        print('这个页面没有朝代的链接')
        return None
    result = []
    for suffix, dynasty in res:
        url = poem_base_url + suffix
        result.append((url, dynasty))
    return result

def get_next_page_url(html):
    next_page_url = ''
    links = re.findall(r'(<a href=.+?>.+?<\/a>)?', html)
    pattern = r'<a href=(.+?)>下一页</a>'
    for link in links:
        if re.findall(pattern, link):
            res = re.findall(pattern, link)[0]
            next_page_url = poem_base_url + res[1:-1]
            break
    return next_page_url.replace('amp;', '')

def get_poet(html):
    """
    获取本页的诗人信息，以及下一页的url
    """
    try:
        res = re.findall(r'<dt><a href="(.+?)" title="(.+?)" target="_blank">(.+?)</a></dt>',html)
    except:
        print("这个页面没有诗人的链接")
        return []
    result = []
    for suffix, poet1, poet2 in res:
        if poet1 != poet2.strip():
            print("诗人名字冲突")
        url = poem_base_url + suffix
        result.append((url, poet2))

    next_page_url = ''
    links = re.findall(r'(<a href=.+?>.+?<\/a>)?', html)
    pattern = r'<a href=(.+?)>下一页</a>'
    for link in links:
        if re.findall(pattern, link):
            res = re.findall(pattern, link)[0]
            next_page_url = poem_base_url + res[1:-1]
            break
    return result, next_page_url

def get_all_page_poet(scrp, url):

    result = []
    html = scrp.open(url)
    poet_result, next_page_url = get_poet(html)
    #print(next_page_url)
    result.extend(poet_result)
    while next_page_url != '':
        try:
            next_page = scrp.open(next_page_url)
        except Exception as e:
            print('===========')
            print(next_page_url)
            print('===========')
            print(e)
            quit()
        next_page_result, next_page_url = get_poet(next_page)
        result.extend(next_page_result)
    return result

def get_poet_infos(scrp, dynasty_result, load_from_json=False):
    file_path = './result/poet_infos.json'
    if load_from_json and os.path.isfile(file_path):
        with open(file_path, 'r', encoding='utf8') as fin:
            print("load poet infos from {}".format(file_path))
            poet_infos = json.load(fin)
            for dynasty, poet_info in poet_infos.items():
                print('{} - {}一共有{}位诗人...'.format(now(), dynasty, len(poet_info)))
    else:
        poet_infos = OrderedDict()
        for url, dynasty in dynasty_result:
            print("{} - 正在爬取{}的诗人信息...".format(now(), dynasty))
            poet_result = get_all_page_poet(scrp, url)
            poet_infos[dynasty] = poet_result
            print("{} - {}的诗人一共有{}位...".format(now(), dynasty, len(poet_result)))
        with open(file_path, 'w', encoding='utf8') as fout:
            json.dump(poet_infos, fout, ensure_ascii=False, indent='\t')
            print("save poet infos to {}".format(file_path))
    return poet_infos

def get_poem_urls_of_one_poet(scrp, url, try_num = 1):
    #print("第{}次尝试获取诗词url信息".format(try_num))
    #print(url)
    html = scrp.open(url)
    pattern = r'<dt><a href="(.+?)" title="(.+?)" target="_blank">(.+?)</a></dt>'
    try:
        res = re.findall(pattern, html)  
    except:
        print("这个页面没有诗词的链接")
        return []
    result = []
    #print(res)
    for suffix, poem1, poem2 in res:
        if poem1 != poem2.strip():
            print("诗人名字冲突")
            print(url)
        url = poem_base_url + suffix
        result.append((url, poem2))
    #print(result)
    #quit()
    next_page_url = get_next_page_url(html)

    if len(result) == 0 and try_num <= 100:
        time.sleep(2)
        try_num += 1
        return get_poem_urls_of_one_poet(scrp, url, try_num)

    if len(result) == 0:
        print(url)
        print('这个页面没找到诗词链接!!!!!!!!!!!!!!!!!!!!!!')
    print('这个页面有{}首诗词'.format(len(result)))
    return result, next_page_url

def get_all_page_poem_urls(scrp, url):

    result = []
    poem_urls, next_page_url = get_poem_urls_of_one_poet(scrp, url)
    #print(next_page_url)
    result.extend(poem_urls)

    while next_page_url != '':
        try:
            next_page = scrp.open(next_page_url)
        except Exception as e:
            print('===========')
            print(next_page_url)
            print('===========')
            print(e)
            quit()
        next_page_result, next_page_url = get_poem_urls_of_one_poet(scrp, next_page_url)
        result.extend(next_page_result)
    return result

def get_all_poem_urls(scrp, poet_infos, load_from_json=False):
    file_path = './result/all_poem_urls.json'
    if load_from_json and os.path.isfile(file_path):
        with open(file_path, 'r', encoding='utf8') as fin:
            print("load all poem urls from {}".format(file_path))
            all_poem_urls = json.load(fin)
            total = 0
            for dynasty, poet_name, poem_urls in all_poem_urls:
                total += len(poem_urls)
            print('{} - 一共有{}首诗...'.format(now(), total))
    else:
        all_poem_urls = []
        for dynasty, poet_info in poet_infos.items():
            for poet_url, poet_name in poet_info:
                poet_search_url = 'http://sc.zdic.net/e/search/?searchget=1&keyboard={}&show=writer&classid=0'.format(scrp.url_encode(poet_name))
                print("{} - 正在爬取{}的诗人{}的诗词url信息...".format(now(), dynasty, poet_name))
                poem_urls = get_all_page_poem_urls(scrp, poet_search_url)
                if len(poem_urls) == 0:
                    print(poet_search_url)
                print(poet_search_url)
                print("{} - {}的诗人{}一共有{}首诗词...".format(now(), dynasty, poet_name, len(poem_urls)))
                all_poem_urls.append((dynasty, poet_name, poem_urls))
        with open(file_path, 'w', encoding='utf8') as fout:
            json.dump(all_poem_urls, fout, ensure_ascii=False, indent='\t')
            print("save poet infos to {}".format(file_path))
    return all_poem_urls

def get_all_poem_urls_single_thread(args):
    thread_name = args['name']
    scrp = args['scrp']
    poet_infos = args['tasks']
    all_poem_urls = []
    n = 0
    total = len(poet_infos)
    for dynasty, poet_name, _ in poet_infos:
        n += 1
        poet_search_url = 'http://sc.zdic.net/e/search/?searchget=1&keyboard={}&show=writer&classid=0'.format(scrp.url_encode(poet_name))
        print("{} - {} - 正在爬取{}的诗人{}的诗词url信息... {}/{}".format(now(), thread_name, dynasty, poet_name, n, total))
        poem_urls = get_all_page_poem_urls(scrp, poet_search_url)
        if len(poem_urls) == 0:
            print(poet_search_url)
        print("{} - {} - {}的诗人{}一共有{}首诗词...".format(now(), thread_name, dynasty, poet_name, len(poem_urls)))
        all_poem_urls.append((dynasty, poet_name, poem_urls))

    return all_poem_urls

def get_all_poem_urls_multi_thread(scrp, poet_infos, load_from_json=False):
    file_path = './result/all_poem_urls.json'
    if load_from_json and os.path.isfile(file_path):
        with open(file_path, 'r', encoding='utf8') as fin:
            print("load all poem urls from {}".format(file_path))
            all_poem_urls = json.load(fin)
            total = 0
            for dynasty, poet_name, poem_urls in all_poem_urls:
                total += len(poem_urls)
            print('{} - 一共有{}首诗...'.format(now(), total))
    else:
        all_tasks = []
        for dynasty, poet_info in poet_infos.items():
            for poet_url, poet_name in poet_info:
                all_tasks.append((dynasty, poet_name, poet_url))
        task_num = len(all_tasks)
        np.random.shuffle(all_tasks)
        thread_num = 4
        batch_num = task_num // thread_num
        threads = []
        for m in range(thread_num):
            if m == thread_num - 1:
                tasks = all_tasks[m*batch_num:]
            else:
                tasks = all_tasks[m*batch_num:(m+1)*batch_num]
            args = {'scrp':scrp,
                    'tasks':tasks}
            t = MyThread(threadID=m, name="Thread-"+str(m), args=args, func=get_all_poem_urls_single_thread)
            t.start()
            threads.append(t)

        all_poem_urls = []
        for thread in threads:
            thread.join() # 这个线程完成之后，才执行下面的代码
            all_poem_urls.extend(thread.results)

        with open(file_path, 'w', encoding='utf8') as fout:
            json.dump(all_poem_urls, fout, ensure_ascii=False, indent='\t')
            print("save all poem urls to {}".format(file_path))
    return all_poem_urls

def get_poems_for_one_poet(scrp, poem_urls):
    poems = []

    for poem_url, poem_name in poem_urls:
        poem = OrderedDict()
        poem['name'] = poem_name
        html = scrp.open(poem_url)
        # 获取诗词信息
        # 包括
        pattern1 = r'<div id="scxx">(.+?)</div>'
        res1 = re.findall(pattern1, html)
        if len(res1) != 1:
            print('诗词信息异常1')
            print(res1)
            print(poem_url)

        pattern2 = r'<strong>(\w+?)</strong>:(\w+?)　'
        res2 = re.findall(pattern2, res1[0])
        if len(res2) == 0:
            print('诗词信息异常2')
            print(poem_url)
        for k, v in res2:
            poem[k] = v

        pattern3 = r'<td id="scnr">(.+?)</td>'
        try:
            res3 = re.findall(pattern3, html, flags=re.S)
            content = res3[0].strip().split('<BR>')
        except:
            print("获取诗词内容失败")
            print(poem_url)
        content = [item for item in content if item != '']
        poem['content'] = content

        pattern4 = r'<div id="cc">出处：<p>(.+?)</p></div>'
        try:
            res4 = re.findall(pattern4, html, flags=re.S)
            cc = res4[0].strip()
            poem['出处'] = cc
        except:
            print("没有出处", file=file_log)
        poems.append(poem)

    return poems

def get_all_poems_single_thread(args):

    thread_name = args['name']
    scrp = args['scrp']
    poet_infos = args['tasks']

    n = 0
    total = len(poet_infos)
    for dynasty, poet_name, poem_urls in poet_infos:
        n += 1
        file_path = './result/poems/{}/{}'.format(dynasty, poet_name)

        poet_search_url = 'http://sc.zdic.net/e/search/?searchget=1&keyboard={}&show=writer&classid=0'.format(scrp.url_encode(poet_name))
        print("{} - {} - 正在爬取{}的诗人{}的所有诗词... {}/{}".format(now(), thread_name, dynasty, poet_name, n, total))
        poems = get_poems_for_one_poet(scrp, poem_urls)

        print("{} - {} - {}的诗人{}一共有{}首诗词...".format(now(), thread_name, dynasty, poet_name, len(poems)))
        with open(file_path, 'w', encoding='utf8') as fout:
            json.dump(poems, fout, ensure_ascii=False)

    return True

def get_all_poems_mutlti_thread():
    time_start = time.time()
    poems_path = "./result/poems"
    if not os.path.exists(poems_path):
        os.mkdir(poems_path)

    scrp = Scraper()

    url = poem_base_url
    html = scrp.open(url)

    dynasty_result = get_dynasty(html)

    # prepare dir
    for url, dynasty in dynasty_result:
        dynasty_dir = os.path.join(poems_path, dynasty)
        if not os.path.exists(dynasty_dir):
            os.mkdir(dynasty_dir)

    poet_infos = get_poet_infos(scrp, dynasty_result, load_from_json=True)

    all_poem_urls = get_all_poem_urls_multi_thread(scrp, poet_infos, load_from_json=True)

    all_tasks = all_poem_urls

    task_num = len(all_tasks)
    np.random.shuffle(all_tasks)
    thread_num = 4
    batch_num = task_num // thread_num
    threads = []
    for m in range(thread_num):
        if m == thread_num - 1:
            tasks = all_tasks[m*batch_num:]
        else:
            tasks = all_tasks[m*batch_num:(m+1)*batch_num]
        args = {'scrp':scrp,
                'tasks':tasks}
        t = MyThread(threadID=m, name="Thread-"+str(m), args=args, func=get_all_poems_single_thread)
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
    file_log.close()


def test_get_poem():
    scrp = Scraper()
    #poem_url = 'http://sc.zdic.net/qin/0607/13/b51fc8fe99e28180eca5bf1e7fb2e639.html'
    poem_url = 'http://sc.zdic.net/tang/0604/20/70111b77ee51e18755f562dba0e295e8.html'
    html = scrp.open(poem_url)

    pattern1 = r'<div id="scxx">(.+?)</div>'
    res1 = re.findall(pattern1, html)
    if len(res1) != 1:
        print('诗词信息异常')
        print(res1)

    pattern2 = r'<strong>(\w+?)</strong>:(\w+?)　'
    res2 = re.findall(pattern2, res1[0])
    print(res2)

    pattern3 = r'<td id="scnr">(.+?)</td>'
    res3 = re.findall(pattern3, html, flags=re.S)

    content = res3[0].strip().split('<BR>')
    content = [item for item in content if item != '']
    print(content)

def main():
    get_all_poems()

if __name__ == '__main__':

    time_start = time.time()
    poems_path = "./result/poems"
    if not os.path.exists(poems_path):
        os.mkdir(poems_path)

    scrp = Scraper()

    url = poem_base_url
    html = scrp.open(url)

    dynasty_result = get_dynasty(html)

    # prepare dir
    for url, dynasty in dynasty_result:
        dynasty_dir = os.path.join(poems_path, dynasty)
        if not os.path.exists(dynasty_dir):
            os.mkdir(dynasty_dir)

    poet_infos = get_poet_infos(scrp, dynasty_result, load_from_json=True)
