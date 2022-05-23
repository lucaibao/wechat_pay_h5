# -*- coding: utf-8 -*-
# @Author: cai bao
# @Email: lucaibao@houselai.com
# @Time: 2022/5/17
# @Desc: 微信支付V3 Core
import json

import requests

from lib.wechatpayv3.utils import create_sign_str
from lib.wechatpayv3.type import RequestType


class Core:
    def __init__(self, mch_id, client_private_key, serial_no, user_agent=None):
        self.mch_id = mch_id                            # 商户号
        self.client_private_key = client_private_key    # 商户私钥
        self.serial_no = serial_no                      # 商户证书序列号
        self.hostname = "https://api.mch.weixin.qq.com"
        self.user_agent = user_agent if user_agent else ""
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": self.user_agent,
            "Authorization": ""
        }

    def request(self, method=None, path=None, body=None, params=None):
        """
        :param method 请求方式
        :param path url(除去hostname部分)
        :param body 请求体
        :param params 请求参数
        """
        if method == RequestType.GET:
            req_body = ""
        elif body:
            req_body = json.dumps(body)
        else:
            req_body = ""

        authorization = create_sign_str(self.client_private_key, self.mch_id, self.serial_no, method, path, req_body)

        self.headers.update({"Authorization": authorization})

        if method == RequestType.GET:
            response = requests.get(url=self.hostname + path, params=params, headers=self.headers)
        elif method == RequestType.POST:
            response = requests.post(url=self.hostname + path, json=body, headers=self.headers)
        elif method == RequestType.PATCH:
            response = requests.patch(url=self.hostname + path, json=body, headers=self.headers)
        elif method == RequestType.PUT:
            response = requests.put(url=self.hostname + path, json=body, headers=self.headers)
        elif method == RequestType.DELETE:
            response = requests.delete(url=self.hostname + path, json=body, headers=self.headers)
        else:
            return False, "请求方法错误"

        return True, response.json()
