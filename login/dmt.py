"""
这篇可行
https://zhuanlan.zhihu.com/p/64157136
"""
from selenium import webdriver as wb
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait as wdw
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import pyautogui
import pyperclip
import requests

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

    return browser

def crawl():
    browser = mylogin('graco葛莱旗舰店:钻展1','btw12345678')
    cookies = browser.get_cookies()

    req = requests.Session()
    for cookie in cookies:
        req.cookies.set(cookie['name'],cookie['value'])

    url = "https://dmp.taobao.com/index_new.html#!/tag-markets/index"
    html = req.get(url).content.decode('utf8')
    with open("tmp.html", "w", encoding="utf8") as fout:
        fout.write(html)
    return browser

def select_crawl():
    browser = mylogin('graco葛莱旗舰店:钻展1','btw12345678')
    windows = browser.window_handles
    browser.switch_to.window(windows[-1])
    print("---------------------------windows-------------------")
    print(windows)
    with open("tag_index.html", "w", encoding="utf8") as fout:
        fout.write(browser.page_source)
    
    # 获取右边的属性table
    table = browser.find_element_by_css_selector('table.table')
    trs = table.find_elements(By.TAG_NAME, 'tr')
    for tr in trs:
        # 点开属性值弹窗
        print(tr.text)
        a = tr.find_element_by_xpath("//td[1]/a")
        a.click()
        # 获取弹窗内容
        time.sleep(2)
        # div = browser.find_element_by_css_selector('div.dmp-newk-bC')
        # print(div.text)
        ul = browser.find_element_by_css_selector('ul.dmp-newa_-iY')
        print(ul.text)

        time.sleep(1)
        pyautogui.press('esc')


    return browser


def test():
    # import reqeusts
    pass

if __name__=='__main__':
    # test()
    # browser = crawl()
    browser = select_crawl()
    # browser = mylogin('graco葛莱旗舰店:钻展1','btw12345678')