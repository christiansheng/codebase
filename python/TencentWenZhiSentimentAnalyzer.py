import hmac
import json
import base64
import random
import urllib
import hashlib
import requests
import datetime

from pprint import pprint


class TencentSentimentAnalyzer:
    def __init__(self, secret_id='AKIDBnyNJpzUgUNO2BItgv0Uhd9SueY43C1b', secret_key='tG9Km2uA8rrSyLDC89LLPjrvTVsNmasg'):
        self.fixed_public_params = {
            'Region': 'sh',
            'Action': 'TextSentiment',
            'SecretId': secret_id,
        }
        self.secret_key = secret_key
        self.api_url = 'wenzhi.api.qcloud.com/v2/index.php'

    def create_signature(self, string_to_sign):
        ske = self.secret_key.encode('utf-8')
        string_to_sign = string_to_sign.encode('utf-8')
        h = hmac.new(ske, string_to_sign, hashlib.sha1).digest()
        return base64.b64encode(h).decode()

    def analyze(self, content):
        p = self.fixed_public_params
        p.update({
            'Nonce': int(random.random() * 10000),
            'Timestamp': int(datetime.datetime.now().timestamp()),
            'content': content
        })
        sts = "GET{}?Action={}&Nonce={}&Region={}&SecretId={}&Timestamp={}&content={}".format(
            self.api_url,
            p['Action'],
            p['Nonce'],
            p['Region'],
            p['SecretId'],
            p['Timestamp'],
            p['content']
        )
        p['Signature'] = self.create_signature(string_to_sign=sts)
        api_url_with_params = "https://{}?{}".format(self.api_url, urllib.parse.urlencode(p))
        r = requests.get(url=api_url_with_params)
        return json.loads(r.text)

if __name__ == "__main__":
    tsa = TencentSentimentAnalyzer()
    r = tsa.analyze("经过一周尝试，已经顺利进入 职位发布页面，正在和Jack一起解决js操作问题")
    pprint(r)
