# -*- coding: utf-8 -*-

import re
import os
import sys
import json
import uuid
import time
import hashlib
import requests

from urllib.parse import quote
from urllib.parse import unquote


class UUApi:
    def __init__(self):
        self.soft_id = '105466'
        self.soft_key = '4672dc87149e42da9a072c202c24b686'
        self.hash = Common.md5(self.soft_id + self.soft_key.upper())
        self.user = '' # to fill in
        self.password = '' # to fill in
        self.mac = '00e021ac7d'
        self.version = '1.1.0.1'
        self.agent = Common.md5(self.soft_key.upper() + self.user.upper()) + self.mac
        self.user_key = ''
        self.uid = '100'
        self.soft_content_key = ''
        self.gkey = self.agent
        self.login()

    def login(self):
        url = UUApi.get_url('service') + '/Upload/Login.aspx?U={}&P={}&R={}'\
            .format(self.user, Common.md5(self.password), time.time())
        res = self.my_get(url)

        self.user_key = res.content.decode()
        self.uid = res.content.decode().split('_')[0]
        self.soft_content_key = Common.md5('{}{}{}'.format(self.user_key, self.soft_id, self.soft_key).lower())
        self.gkey = self.agent
        return self.uid

    # 余额
    def get_point(self):
        url = UUApi.get_url('service') + '/Upload/GetScore.aspx?U={}&P={}&R={}&random={}'\
            .format(self.user, Common.md5(self.password), time.time(), Common.md5(self.user + self.soft_id))
        res = self.my_get(url)
        return res.content.decode()

    # 获取码
    def get_code(self, path, code_type="1005"):
        url = UUApi.get_url('upload') + '/Upload/Processing.aspx?R={}'.format(time.time())
        res = self.my_upload(url, path, code_type)
        ret = res.text.split('|')

        if len(ret) > 1:
            return ret[1]
        else:
            return self.get_result(res.text)

    def get_result(self, code_id):
        url = UUApi.get_url('code') + '/Upload/GetResult.aspx?KEY={}&ID={}&Random={}'\
            .format(self.user_key, code_id, time.time())
        ret = '-3'
        timer = 0
        while ret == '-3' and timer < 20:
            res = self.my_get(url)
            ret = res.text
            timer += 1
            time.sleep(1)
        return ret

    match = None

    @staticmethod
    def get_url(key):
        if not UUApi.match:
            url = "http://common.taskok.com:9000/Service/ServerConfig.aspx"
            res = requests.get(url)
            match = re.findall(r',(.*)?:101,(.*)?:102,(.*)?:103', res.text)
            if not match:
                return '-1001'
            UUApi.match = match

        type_map = {
            'service': 0,
            'upload': 1,
            'code': 2,
        }
        value = type_map[key]
        return 'http://' + UUApi.match[0][value]

    def my_get(self, url):
        headers = {
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Language': 'zh-CN',
            'Connection': 'Keep-Alive',
            'Cache-Control': 'no-cache',
            'SID': self.soft_id,
            'HASH': self.hash,
            'UUVersion': self.version,
            'UID': self.uid,
            'User-Agent': self.agent,
            'KEY': self.gkey,
        }
        return requests.get(url, headers=headers)

    def my_upload(self, url, file, code_type="1005"):
        data = {
            'key': self.user_key,
            'sid': self.soft_id,
            'skey': self.soft_content_key,
            'TimeOut': 60000,
            'Type': code_type,
            "Version": 100
        }

        files = {'file': open(file, 'rb')}
        return requests.post(url, files=files, data=data)


class Common:
    def __init__(self):
        pass

    @staticmethod
    def get_ints(some_str):
        match = re.findall(r'\d+', some_str)
        if not match:
            return [0]
        return match

    @staticmethod
    def data_form(data):
        data_cols = [col.split('=') for col in data.split('&')]
        data_form = {col[0]: unquote(col[1]) for col in data_cols}
        return data_form

    @staticmethod
    def form_data(form):
        s = ['{}={}'.format(k, quote(str(v))) for k, v in form.items()]
        return '&'.join(s)

    @staticmethod
    def md5(data):
        if type(data) is not str:
            data = json.dumps(data)

        md5 = hashlib.md5()
        md5.update(data.encode("utf8"))
        # md5.update(data)
        ret = md5.hexdigest()
        return ret

    @staticmethod
    def unique_id():
        id_str = str(uuid.uuid4())
        return Common.md5(id_str)

    @staticmethod
    def tmp_dir():
        if os.name == 'nt':
            return 'd:/tmp'
        else:
            return '/tmp'


if __name__ == '__main__':
    uu_api = UUApi()
    # print(len(sys.argv))
    if len(sys.argv) == 1:
        file_name = "verify.png"
    else:
        file_name = sys.argv[1]
    # print(file_name)
    code = uu_api.get_code(file_name)
    print(code, end='')

