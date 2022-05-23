# -*- coding: utf-8 -*-
# @Author: cai bao
# @Email: lucaibao@houselai.com
# @Time: 2022/5/17
# @Desc: 微信支付V3
import os

from lib.wechatpayv3.utils import aes_decrypt
from lib.wechatpayv3.core import Core


class WechatApi(object):
    """
    公众号通过微信网页授权机制，来获取用户基本信息
    https://developers.weixin.qq.com/doc/offiaccount/OA_Web_Apps/Wechat_webpage_authorization.html#0
    """
    def __init__(self, appid, mch_id, secret, apikey, notify_url, client_private_key, serial_no, user_agent=None):
        self.appid = appid                              # APPID
        self.mch_id = mch_id                            # 商户号
        self.secret = secret                            # 小程序AppSecret(开发者密码；在公众平台--开发--基本配置--开发者密码)
        self.apikey = apikey                            # API v3秘钥
        self.notify_url = notify_url                    # 支付结果回调接口
        self.serial_no = serial_no                      # 商户证书序列号
        self.client_private_key = client_private_key
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": ""
        }
        self.core = Core(mch_id, client_private_key, serial_no, user_agent)

    def get_cert(self, base_dir):
        """
        获取微信支付平台证书列表
        https://pay.weixin.qq.com/wiki/doc/apiv3/apis/wechatpay5_1.shtml
        :param base_dir :指定生成证书的存放路径
        """
        # url = "https://api.mch.weixin.qq.com/v3/certificates"
        path = "/v3/certificates"

        status, res_body = self.core.request(method="GET", path=path, body="", params={})

        for i in range(0, len(res_body.get("data"))):
            nonce = res_body["data"][i]["encrypt_certificate"]["nonce"]
            ciphertext = res_body["data"][i]["encrypt_certificate"]["ciphertext"]
            associated_data = res_body["data"][i]["encrypt_certificate"]["associated_data"]
            data = aes_decrypt(self.apikey, nonce, ciphertext, associated_data)

            wx_cert_dir = os.path.join(base_dir, "cert")
            if not os.path.isdir(wx_cert_dir):
                os.mkdir(wx_cert_dir)
            wx_cert_file = os.path.join(wx_cert_dir, "wxp_cert.pem")
            with open(wx_cert_file, "w") as f:
                f.write(data)
        return True


if __name__ == "__main__":
    s = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx186e63765e9bd457&redirect_uri=https%3A%2F%2Fcoupons.ruiheshenzhen.com%2Fapp%2Fpay_api%2Foauth_response.json&response_type=code&scope=snsapi_base&state=STATE#wechat_redirect"
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    appid = "wx186e63765e9bd457"
    app_secret = "9d6c1fe531fe51312198be32231ed2d2"
    mch_id = "1569929711"
    mch_name = "深圳市瑞合健康管理科技有限公司"
    api_v3_key = "Wz55Lj5vJ5xWNB9nNaLCQVQChrwMKYb4"
    redirect_uri = "https://coupons.ruiheshenzhen.com/"
    cert_serial_no = "3A3B3CB58BDD62891AE8C8663D7F3A0F6C77A9DD"
    client_private_key = os.path.join(base_dir, 'cert', 'client_key.pem')
    wx_api = WechatApi(appid, mch_id, app_secret, api_v3_key, redirect_uri, client_private_key, cert_serial_no, "")

    # 获取平台证书
    wx_api.get_cert(base_dir)
