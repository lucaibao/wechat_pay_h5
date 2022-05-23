# -*- coding: utf-8 -*-
# @Author: cai bao
# @Email: lucaibao@houselai.com
# @Time: 2022/5/17
# @Desc: 微信支付V3
from lib.wechatpayv3.core import Core


class WechatPay(object):
    """
    JSAPI支付
    https://pay.weixin.qq.com/wiki/doc/apiv3/open/pay/chapter2_1.shtml
    """
    def __init__(self, appid, mch_id, notify_url, client_private_key, serial_no, pay_desc, user_agent=None):
        self.appid = appid                              # APPID
        self.mch_id = mch_id                            # 商户号
        self.notify_url = notify_url                    # 支付结果回调接口
        self.client_private_key = client_private_key    # 商户私钥
        self.pay_desc = pay_desc                        # 商品描述
        self.core = Core(mch_id, client_private_key, serial_no, user_agent)

    def jsapi(self, params: dict):
        """
        JSAPI下单
        https://pay.weixin.qq.com/wiki/doc/apiv3/apis/chapter3_1_1.shtml
        JSAPI网页支付，即日常所说的公众号支付，可在微信公众号、朋友圈、聊天会话中点击页面链接，或者用微信“扫一扫”扫描页面地址二维码在微信中打开商户HTML5页面，在页面内下单完成支付。
        """
        path = "/v3/pay/transactions/jsapi"
        body = {
            "appid": self.appid,
            "mchid": self.mch_id,
            "description": self.pay_desc,   # 商品描述
            "out_trade_no": params.get("out_trade_no"),       # 商户订单号
            "notify_url": self.notify_url,  # 通知地址
            "amount": {
                "total":  params.get("amount"),
                "currency": "CNY"
                },    # 订单总金额和货币类型{"total": 100, "currency": "CNY"}
            "payer": {
                "openid": params.get("openid")  # 支付者信息
                }
            }

        if params.get("time_expire"):
            body["time_expire"] = params.get("time_expire")

        if params.get("attach"):
            body["attach"] = params.get("attach")

        if params.get("goods_tag"):
            body["goods_tag"] = params.get("goods_tag")

        if params.get("detail"):
            body["detail"] = params.get("detail")

        if params.get("scene_info"):
            body["scene_info"] = params.get("scene_info")

        if params.get("settle_info"):
            body["settle_info"] = params.get("settle_info")

        return self.core.request("POST", path, body, {})

    def pay_query(self, order_no, wx=False):
        """
        查询订单
        https://pay.weixin.qq.com/wiki/doc/apiv3/apis/chapter3_1_2.shtml
        1、查询订单状态可通过微信支付订单号或商户订单号两种方式查询
        :param order_no: 微信支付订单号或商户订单号
        :param wx:
        """
        if wx:
            # 微信支付订单号查询
            path = "/v3/pay/transactions/id/" + order_no + "?mchid=" + self.mch_id
        else:
            # 商户订单号查询
            path = "/v3/pay/transactions/out-trade-no/" + order_no + "?mchid=" + self.mch_id

        params = {
            "mchid": self.mch_id
        }

        return self.core.request(method="GET", path=path, body="", params=params)

    def pay_close(self, out_trade_no):
        """
        关闭订单
        https://pay.weixin.qq.com/wiki/doc/apiv3/apis/chapter3_1_3.shtml
        1、商户订单支付失败需要生成新单号重新发起支付，要对原订单号调用关单，避免重复支付；
        2、系统下单后，用户支付超时，系统退出不再受理，避免用户继续，请调用关单接口。
        :param out_trade_no: 商户订单号
        """
        path = "/v3/pay/transactions/out-trade-no/{}/close".format(out_trade_no)

        body = {
            "mchid": self.mch_id
        }

        return self.core.request(method="POST", path=path, body=body, params={})


# if __name__ == "__main__":
    # openid = "oCeYT5FJuXJzSZRqyKwJvHkvLHi4"
    # openid, msg = weixinPayV3.getOpenid("0236wYkl2uqIv74yi6ll2mDoog16wYkt")
    # print(openid)
    # print(msg)
    # trade_no = "17726646955H1628592789597624"
    # data = weixinPayV3.payquery(trade_no)
    # print(data)
