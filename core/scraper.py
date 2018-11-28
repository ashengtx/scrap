import http.cookiejar
from urllib import parse, request
from bs4 import BeautifulSoup

class Scraper(object):

    def __init__(self, cookie_file='cookie'):

        # 建立LWPCookieJar实例，可以存Set-Cookie3类型的文件。
        # 而MozillaCookieJar类是存为'/.txt'格式的文件
        cookie = http.cookiejar.LWPCookieJar(cookie_file)
        # 若本地有cookie则不用再post数据了
        try:
            cookie.load(ignore_discard=True)
        except IOError:
            print('Cookie未加载！')

        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36'}

        opener = request.build_opener(request.HTTPCookieProcessor(cookie))
        # 给openner添加headers, addheaders方法接受元组而非字典
        opener.addheaders = [(key, value) for key, value in headers.items()]

        self._opener = opener

    def html2dom(self, html):
        return BeautifulSoup(html, 'html.parser')

    def md5_encode(self, string):
        """
        md5 编码
        """
        m = hashlib.md5()
        m.update(string.encode('utf8'))
        v=m.hexdigest()
        return v

    def open(self, url, post_data=None, encoding='utf8'):
        if post_data is not None:
            return self._opener.open(url, post_data).read().decode(encoding)
        else:
            return self._opener.open(url).read().decode(encoding)

    def safe_open(self, url, post_data=None, encoding='utf8', try_num=5):
        """
        有时候网络原因my_open会连不上而抛出异常，my_safe_open，多尝试几次
        """

        while (try_num > 0):
            try:
                html = self.open(url, post_data)
                return html
            except:
                print("retry connecting to {} for time {}".format(url, 6-try_num))
                return self.safe_open(url, post_data, try_num=try_num-1)
        return False

    
    def update_headers(self, new_headers):
        self._opener.addheaders = [(key, value) for key, value in new_headers.items()]

    def add_headers(self, tobeadd):
        addheaders = dict(self._opener.addheaders)
        for k, v in tobeadd.items():
            if k not in addheaders:
                self._opener.addheaders.append((k, v))
        return True

    def url_encode(self, data):
        if type(data) is str:
            return parse.quote_plus(data)
        elif type(data) is dict:
            return parse.urlencode(data).encode('utf8')

