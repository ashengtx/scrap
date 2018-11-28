### python代理设置

1 开启ss全局代理模式

2 设置代理

```python
proxies_ss = {
    'https': 'https://127.0.0.1:1080',
    'http': 'http://127.0.0.1:1080'
}
```

默认端口1080

3 设置header

```python
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
}

```

让服务器以为你是浏览器

4 requests.get访问最方便

```python
import requests
url = 'https://www.google.com/'
response = requests.get(url, proxies=proxies_ss, verify=False, headers=headers)
print(response.text)
```