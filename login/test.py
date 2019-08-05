import time, re
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import pyautogui

from bs4 import BeautifulSoup

def get_tracks(distance):
    '''
    本质来源于物理学中的加速度算距离： s = vt + 1/2 at^2
                                    v = v_0 + at

    在这里：总距离S= distance+20
            加速度：前3/5S加速度2，后半部分加速度是-3
    https://dataxujing.github.io/my-test-scrapy/
    '''
    v=0
    t=0.2
    tracks=[]

    current=0
    mid=distance*3/5
    while current < distance:
        if current < mid:
            a=2
        else:
            a=-3

        s=v*t+0.5*a*(t**2)
        v=v+a*t
        current+=s
        tracks.append(round(s))

    return tracks

def login(username, password):
    driver_path = "F:/tools/chromedriver_win32/chromedriver.exe"

    chrome_options = Options()
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    driver = webdriver.Chrome(executable_path=driver_path, options=chrome_options)
    # login_url = "https://dmp.taobao.com/login.html"
    login_url = "https://login.taobao.com/member/login.jhtml?style=mini&css_style=mdmp&full_redirect=true&from=mdmp&sub=true&tpl_redirect_url=https://dmp.taobao.com/login.html"
    # login_url = "https://www.baidu.com/"
    driver.maximize_window()  #窗口最大化保证坐标正确
    driver.get(login_url) #打开页面

    # pyautogui.PAUSE=0.5
    # pyautogui.moveTo(630,420)  #移动到切换登录的位置
    # pyautogui.click()  #点击切换按钮
    # pyautogui.typewrite(username)
    # pyautogui.press('tab')
    
def load_html_from_file(filepath):
    with open(filepath, 'r', encoding='utf8') as fin:
        return fin.read()

def get_first_class_tags(html):
    dom = BeautifulSoup(html, 'html.parser')
    tag_dls = dom.select('dl[class*="dmp-newae-kn mb20"]')
    for tag_dl in tag_dls:
        tag_dt = tag_dl.select('dt')[0]
        print('['+tag_dt.text[1:-1]+']')
        for a in tag_dl.select('dd')[0].select('a'):
            print(a.text)

def has_next_page(html):
    dom = BeautifulSoup(html, 'html.parser')
    print(dom)
    tag = dom.select_one('li[class="dmp-newG-fw"][mxa="dmp-newN:i"]').select_one('a')
    print(tag)
    if re.findall(r'mx-click=".*?\(\{page:.*\}\)"', str(tag)):
        print('True')
        return True
    return False

def test_re():
    tag = """<a class="mc-iconfont dmp-newG-fx rotate180" href="#" mx-click="mx_165__cD({})"></a>"""
    res = re.findall(r'mx-click=".*?\(\{page:.*\}\)"', tag)
    print(res)

def test():
    s = """<li mxa="dmp-newN:i" class="dmp-newG-fw"><a class="mc-iconfont dmp-newG-fx rotate180 " href="#" mx-click="mx_13763__cD({page:2})" data-spm-anchor-id="a2e3k.11816884.0.0"></a></li>"""
    dom = BeautifulSoup(s, 'html.parser')
    print(dom.contents[0])

if __name__ == "__main__":
    # username = "graco葛莱旗舰店:钻展1"
    # password = "btw12345678"
    # login(username, password)
    # html = load_html_from_file('tag_index.html')
    html = """<li mxa="dmp-newN:i" class="dmp-newG-fw"><a class="mc-iconfont dmp-newG-fx rotate180 " href="#" mx-click="mx_13763__cD({page:2})" data-spm-anchor-id="a2e3k.11816884.0.0"></a></li>"""
    # get_first_class_tags(html)
    has_next_page(html)
