"""
这篇可行
https://zhuanlan.zhihu.com/p/64157136
"""
from selenium import webdriver as wb
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait as wdw
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re
import time
import json
import pyautogui
import pyperclip
import requests
import pickle
from collections import OrderedDict

def pyclick(x, y, timesleep=0):
    time.sleep(timesleep)
    pyautogui.moveTo(x,y)
    pyautogui.mouseDown()
    pyautogui.mouseUp()

def get_tracks(start, to):

    distance = to - start
    v=0
    t=0.3
    a=20
    tracks=[]

    current=start
    mid=start+distance*3/5
    while current < to:
        v=v+a*t
        s=v*t+0.5*a*(t**2)
        current+=s
        print(current)
        tracks.append(round(current))

    return tracks

def slide(start, to, y):
    pyautogui.PAUSE=0.1

    pyautogui.moveTo(start,y)
    pyautogui.mouseDown()

    tracks = get_tracks(start, to)
    for x in tracks:
        pyautogui.moveTo(x,y)
    pyautogui.mouseUp()
    pyautogui.PAUSE=0.5

def save_cookie(browser):
    # with open('cookie.json', 'w', encoding='utf8') as fout:
    #     cookie = browser.get_cookies()
    #     json.dump(cookie, fout, indent='\t')
    pickle.dump(browser.get_cookies() , open("cookies.pkl","wb"))

def mylogin(username,password):
    pyautogui.PAUSE=0.5  #设置每个动作0.2s太快来不及输入密码
    options=wb.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-automation'])#切换到开发者模式
    browser=wb.Chrome(options=options, executable_path="F:/tools/chromedriver_win32/chromedriver.exe")
    browser.maximize_window()  #窗口最大化保证坐标正确
    #login_url = "https://login.taobao.com/member/login.jhtml?style=mini&css_style=mdmp&full_redirect=true&from=mdmp&sub=true&tpl_redirect_url=https://dmp.taobao.com/login.html"
    login_url = "https://dmp.taobao.com/login.html"
    browser.get(login_url)
    
    time.sleep(2)

    moveToX=1230
    moveToY=430
    pyautogui.moveTo(moveToX,moveToY)  #移动到切换登录的位置
    pyautogui.click()  #点击切换按钮
    pyperclip.copy(username) # pyautogui无法输入中文，只能用pyperclip复制，pyautogui粘贴
    pyautogui.hotkey('ctrl', 'v')
    # pyautogui.typewrite(username)
    pyautogui.press('tab')
    pyautogui.typewrite(password)

    time.sleep(5)
    # 滑块验证
    # 这个地方被淘宝识别出来了，暂时用手动
    # moveToX=1230
    # moveToY=560
    # pyautogui.moveTo(moveToX,moveToY) # 滑块
    # pyautogui.mouseDown()
    # moveToX=1520
    # pyautogui.moveTo(moveToX,moveToY)
    # pyautogui.mouseUp()
    # slide(start=1230, to=1520, y=560)

    # 点登陆
    moveToX = 1350
    moveToY = 630
    pyautogui.moveTo(moveToX,moveToY)
    pyautogui.mouseDown()
    pyautogui.mouseUp()

    pyclick(1360,520,2)
    pyclick(400,120,2)

    save_cookie(browser)
    return browser

def crawl():
    browser = mylogin('graco葛莱旗舰店:钻展1','btw12345678')
    browser.get('https://dmp.taobao.com/index_new.html#!/tag-markets/index')
    print(browser.page_source)
    # cookies = browser.get_cookies()

    # req = requests.Session()
    # for cookie in cookies:
    #     req.cookies.set(cookie['name'],cookie['value'])

    # url = "https://dmp.taobao.com/index_new.html#!/tag-markets/index"
    # html = req.get(url).content.decode('utf8')
    # with open("tmp.html", "w", encoding="utf8") as fout:
    #     fout.write(html)
    return browser

def get_next_page(browser):
    tag = browser.find_element_by_css_selector('li[class="dmp-newG-fw"][mxa="dmp-newN:i"]').find_element(By.TAG_NAME, 'a')
    if re.findall(r'mx-click=".*?\(\{page:.*\}\)"', str(tag)):
        return tag
    else:
        print(tag.get_attribute('innerHTML'))
        return None

def save_result(obj):
    with open('tag_result.json', 'w', encoding='utf8') as fout:
        json.dump(obj, fout, indent='\t', ensure_ascii=False)

def select_crawl(restart=False):
    recrawl = []
    if not restart:
        with open("tag_result.json", 'r', encoding='utf8') as fin:
            result = json.load(fin)
    else:
        result = OrderedDict()

    browser = mylogin('graco葛莱旗舰店:钻展1','btw12345678')
    windows = browser.window_handles
    browser.switch_to.window(windows[-1])
    print("---------------------------windows-------------------")
    print(windows)
    with open("tag_index.html", "w", encoding="utf8") as fout:
        fout.write(browser.page_source)
    
    tag_dls = browser.find_elements_by_css_selector('dl[class*="dmp-newae-kn mb20"]')
    for tag_dl in tag_dls:
        tag_dt = tag_dl.find_elements(By.TAG_NAME, 'dt')[0]
        # 标签组名字
        tag_group_key = tag_dt.text[1:-1]
        if not result.get(tag_group_key):
            tag_group = OrderedDict()
            result[tag_group_key] = tag_group
        else:
            tag_group = result[tag_group_key]

        for a in tag_dl.find_elements(By.TAG_NAME, 'dd')[0].find_elements(By.TAG_NAME, 'a'):
            
            first_class_tag_key = a.text
            print(first_class_tag_key)
            if first_class_tag_key in result[tag_group_key] and (first_class_tag_key not in recrawl):
                continue
            time.sleep(1)
            a.click()
            time.sleep(2)
            # if first_class_tag_key not in recrawl:
            #     continue
            first_class_tag = OrderedDict()
            tag_group[first_class_tag_key] = first_class_tag

            # 是否有下一页
            has_next_page = True
            while has_next_page:
                # 获取右边的属性table
                # table = browser.find_element_by_css_selector('table.table')
                try:
                    trs = browser.find_elements(By.XPATH, "//table[contains(@class, 'table')]/tbody/tr")
                    if len(trs) == 1:
                        a = trs[0].find_element(By.CSS_SELECTOR, "td:nth-child(1)").find_element(By.TAG_NAME, "a")
                        if '暂无结果' in a.text:
                            has_next_page = False
                            break
                except:
                    has_next_page = False
                    break
                for tr in trs:
                    # 点开属性值弹窗
                    print(tr.text)
                    print(tr.text.split('\n'))
                    a = tr.find_element(By.CSS_SELECTOR, "td:nth-child(1)").find_element(By.TAG_NAME, "a")

                    # 二级标签属性 & clean
                    second_class_tag_key = tr.find_element(By.CSS_SELECTOR, "td:nth-child(1)").text
                    second_class_tag_key = second_class_tag_key.replace(a.text, '')
                    try:
                        i = tr.find_element(By.CSS_SELECTOR, "td:nth-child(1)").find_element(By.TAG_NAME, "i")
                        second_class_tag_key = second_class_tag_key.replace(i.text, '')
                    except:
                        pass
                    # 这个标签有问题，跳过
                    if second_class_tag_key in ['车险偏好人群']:
                        first_class_tag[second_class_tag_key.strip()] = []
                        continue

                    second_class_tag = []
                    a.click()
                    # 获取弹窗内容
                    time.sleep(2)
                    # div = browser.find_element_by_css_selector('div.dmp-newk-bC')
                    # print(div.text)
                    try:
                        lis = browser.find_elements(By.XPATH, '//ul[@class="dmp-newa_-iY"]/li')
                        for li in lis:
                            second_class_tag.append(li.text)
                    except:
                        second_class_tag = []

                    time.sleep(1)
                    first_class_tag[second_class_tag_key.strip()] = second_class_tag
                    save_result(result)
                    pyautogui.press('esc')

                # 判断有没下一页
                next_page = get_next_page(browser)
                if next_page:
                    next_page.click()
                    time.sleep(1)
                else:
                    has_next_page = False
    save_result(result)
    return browser


def test():
    # import reqeusts
    pass

def test_cookie():
    cookies = pickle.load(open("cookies.pkl", "rb"))
    options=wb.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-automation'])#切换到开发者模式
    browser=wb.Chrome(options=options, executable_path="F:/tools/chromedriver_win32/chromedriver.exe")
    browser.maximize_window()  #窗口最大化保证坐标正确
    #login_url = "https://login.taobao.com/member/login.jhtml?style=mini&css_style=mdmp&full_redirect=true&from=mdmp&sub=true&tpl_redirect_url=https://dmp.taobao.com/login.html"
    # login_url = "https://dmp.taobao.com/login.html"
    login_url = "https://dmp.taobao.com/"
    browser.get(login_url)
    for cookie in cookies:
        browser.add_cookie(cookie)

    return browser

if __name__=='__main__':
    # test()
    # browser = crawl()
    browser = select_crawl()
    # browser = mylogin('graco葛莱旗舰店:钻展1','btw12345678')
    # browser = test_cookie()