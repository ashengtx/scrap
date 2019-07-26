from selenium import webdriver as wb
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait as wdw
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import pyautogui
import pyperclip

def __login__(username,password,pathA,pathB):
    pyautogui.PAUSE=0.5  #设置每个动作0.2s太快来不及输入密码
    options=wb.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-automation'])#切换到开发者模式
    browser=wb.Chrome(options=options, executable_path="F:/tools/chromedriver_win32/chromedriver.exe")
    browser.maximize_window()  #窗口最大化保证坐标正确
    browser.get('https://login.taobao.com/member/login.jhtml')
#try:
    #left,top,width,height=pyautogui.locateOnScreen('G:/jupyter project/淘宝/login_switch_blue.PNG')
#except:
    #left,top,width,height=pyautogui.locateOnScreen('G:/jupyter project/淘宝/login_switch.PNG')      获取login_switch位置
    moveToX=1600
    moveToY=380
    pyautogui.moveTo(moveToX,moveToY)  #移动到切换登录的位置
    pyautogui.click()  #点击切换按钮
    pyautogui.typewrite(username)
    pyautogui.press('tab')
    pyautogui.typewrite(password)
    errorType=0
    try:
        left,top,width,height=pyautogui.locateOnScreen(pathA)
        print('识别蓝色')
        moveToX=left+140
        moveToY=top+15
        print(moveToX,moveToY)
        pyautogui.moveTo(moveToX,moveToY)
        pyautogui.mouseDown()
        moveToX=moveToX+300
        pyautogui.moveTo(moveToX,moveToY)
        pyautogui.mouseUp()
        pyautogui.moveTo(moveToX-250,moveToY+60)
        pyautogui.mouseDown()
        pyautogui.mouseUp()
    except:
        errorType=1  #识别不出蓝色
        
    if errorType==1:
        try:
            left,top,width,height=pyautogui.locateOnScreen(pathB)
            moveToX=left+110
            moveToY=top+13
            print('识别绿色')
            print(moveToX,moveToY) #1299 497
            pyautogui.moveTo(moveToX,moveToY)
            pyautogui.mouseDown()
            moveToX=moveToX+300
            pyautogui.moveTo(moveToX,moveToY)
            pyautogui.mouseUp()
            pyautogui.moveTo(moveToX-250,moveToY+60)
            pyautogui.mouseDown()
            pyautogui.mouseUp()
        except:
            errorTye=2  #识别不出绿色
            
    if errorType==2:
        print('没有滑块')
        pyautogui.moveTo(1189,497)
        pyautogui.mouseDown()
        pyautogui.mouseUp()
        
    return browser  #返回浏览器当前的页面

def mylogin(username,password):
    pyautogui.PAUSE=0.5  #设置每个动作0.2s太快来不及输入密码
    options=wb.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-automation'])#切换到开发者模式
    browser=wb.Chrome(options=options, executable_path="F:/tools/chromedriver_win32/chromedriver.exe")
    browser.maximize_window()  #窗口最大化保证坐标正确
    browser.get('https://login.taobao.com/member/login.jhtml')
    # print(browser.get_cookies())

    moveToX=1600
    moveToY=380
    pyautogui.moveTo(moveToX,moveToY)  #移动到切换登录的位置
    pyautogui.click()  #点击切换按钮
    pyperclip.copy(username) # pyautogui无法输入中文，只能用pyperclip复制，pyautogui粘贴
    pyautogui.hotkey('ctrl', 'v')
    # pyautogui.typewrite(username)
    pyautogui.press('tab')
    pyautogui.typewrite(password)

    moveToX=1245
    moveToY=635
    pyautogui.moveTo(moveToX,moveToY) # 滑块
    pyautogui.mouseDown()
    moveToX=moveToX+360
    pyautogui.moveTo(moveToX,moveToY)
    pyautogui.mouseUp()
    moveToX = 1410
    moveToY = 710
    pyautogui.moveTo(moveToX,moveToY)
    pyautogui.mouseDown()
    pyautogui.mouseUp()

    return browser

if __name__=='__main__':
    # browser=__login__('graco葛莱旗舰店:钻展1','btw12345678','G:/jupyter project/淘宝/block_blue.PNG','G:/jupyter project/淘宝/block_green.PNG')
    browser=mylogin('graco葛莱旗舰店:钻展1','btw12345678')
    print(browser.get_cookies())