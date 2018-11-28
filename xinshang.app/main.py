import os, json, time
import pprint

from core.scraper import Scraper
scrp = Scraper()

URL_USERZONE = 'http://api.91xinshang.com/v3/merchant/userzone'
URL_GOOD_DETAIL = 'https://api.91xinshang.com/xz/detail'

params = {'pageIndex': '1',
        'rankSort': '100',
        'requestModeType': '0',
        'sellerId': '20245100',
        # 'sign': '105614d45b95761ffbcf93db5abbeb9a',
        'timestamp': '1542941455874',
        'typeId': '0'}

good_detail_params = {'goodsId': '2855554',
                     # 'sign': '0f085d831aa0c901faa88e9b7fb279a1',
                     'timestamp': '1542948634847'}

def get_timestamp():
    return round(time.time()*1000)

def get_goodsId_onepage(url=URL_USERZONE, pageIndex=1):
    pageIndex = str(pageIndex)
    cur_params = params.copy()
    cur_params['pageIndex'] = pageIndex
    cur_params['timestamp'] = str(get_timestamp())
    params_encoded = scrp.url_encode(cur_params)

    res = scrp.open(url, params_encoded)

    res_json = json.loads(res)
    pprint.pprint((res_json))
    goodsId = [good['goodsId'] for good in res_json['data']['result']]
    return goodsId

def get_all_goodsid():
    all_goodsid = []
    for i in range(1, 50):
        try:
            goodsid = get_goodsId_onepage(url=URL_USERZONE, pageIndex=i)
            print("scrap {} goods".format(len(goodsid)))
            print(goodsid)
            all_goodsid.extend(goodsid)
            time.sleep(2)
        except Exception as e:
            print(e)

    unique_goodsid = set(all_goodsid)
    print(len(all_goodsid))
    print(len(unique_goodsid))
    with open('goodsid.txt', 'w', encoding='utf8') as fout:
        for i in unique_goodsid:
            print(i, file=fout)
    return unique_goodsid

def get_good_detail(url=URL_GOOD_DETAIL, goodid=2308170):
    detail = {}
    cur_params = good_detail_params.copy()
    cur_params['goodsId'] = str(goodid)
    cur_params['timestamp'] = str(get_timestamp())
    print(cur_params)
    params_encoded = scrp.url_encode(cur_params)
    res = scrp.open(url, params_encoded)

    res_json = json.loads(res)
    # pprint.pprint((res_json))
    detail['goods_detail'] = res_json['data']['goods']
    detail['seller_brief'] = res_json['data']['sellerBrief']['attrValueName']
    detail['attrs'] = res_json['data']['attrs']

    return detail

def get_all_good_detail():
    with open('goodsid.txt', 'r', encoding='utf8') as fin:
        for line in fin:
            goodid = line.strip()
            detail = get_good_detail(goodid=goodid)
            pprint.pprint(detail)
            with open(os.path.join('./goods_detail', goodid), 'w', encoding='utf8') as fout:
                json.dump(detail, fout, ensure_ascii=False, indent='\t')
            time.sleep(0.5)

if __name__ == "__main__":
    get_all_good_detail()