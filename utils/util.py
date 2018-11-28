import pprint

def params2dict(s):
    """
    :param s:
    :return:
    >>> s = 'typeId=0&timestamp=1542941455874&rankSort=100'
    >>> print(params2dict(s))
    >>> {'rankSort': '100', 'timestamp': '1542941455874', 'typeId': '0'}
    """
    d = {}
    for kv in s.split('&'):
        k, v = kv.split('=')
        d[k]=v
    return d

if __name__ == '__main__':
    s = 'timestamp=1542948634847&goodsId=2855554&sign=0f085d831aa0c901faa88e9b7fb279a1'
    pprint.pprint(params2dict(s))
    data = {"data":{"batch":[{"widget":{"rfkid":"pdp1"}},{"widget":{"rfkid":"pdp2"}},{"widget":{"rfkid":"pdp_edt"}}],"context":{"page":{"uri":"/mott-mini-color-block-pebbled-leather-crossbody/_/R-US_32T8GF5C0T","sku":["287715253"],"locale_country":"us","locale_language":"en"},"user":{"uuid":"263221008-g8-98-49-1p-1kf2o6t0xm95gyszm47y-1543291843925"}},"n_item":12,"content":{},"appearance":{}}}
    pprint.pprint(data)