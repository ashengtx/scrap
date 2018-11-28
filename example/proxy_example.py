import requests

proxies_ss = {
    'https': 'https://127.0.0.1:1080',
    'http': 'http://127.0.0.1:1080'
}

proxies_fiddler = {
    'https': 'https://127.0.0.1:9999',
    'http': 'http://127.0.0.1:9999'
}

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
}

google_url = 'https://www.google.com/'

proxies = proxies_ss
# proxies = proxies_fiddler
# url = google_url

response = requests.get(url, proxies=proxies, verify=False, headers=headers)
print(response.text)


