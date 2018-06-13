import os, re
import time

from collections import OrderedDict

from scraper import Scraper

poem_base_url = 'http://sc.zdic.net'

next_page_url = 'http://sc.zdic.net/shiren/tang/index_2.html'

pattern = r'<a href=(.+?)>下一页</a>'

