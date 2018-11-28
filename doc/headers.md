## 有些网站需要在headers带上一些特定属性

比如[michaelkors](https://www.michaelkors.com/)，需要带上`Accept-Language`

```python
import requests

proxies = {
    'https': 'https://127.0.0.1:1080',
    'http': 'http://127.0.0.1:1080'
}

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}

url = 'https://www.michaelkors.com/'
response = requests.get(url, proxies=proxies, verify=False, headers=headers)
print(response.text)
```