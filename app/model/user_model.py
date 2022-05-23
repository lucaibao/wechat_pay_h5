# -*- coding: utf-8 -*-
# @Author: cai bao
# @Email: lucaibao@houselai.com
# @Time: 2022/5/17
import traceback
import requests

from flask import current_app, redirect

from common.json_data import return_pack
from common.status_code import Code
from config.wechat_info import WeiXinUri, WeiXinInfo
from util.mysql_ import db
from app.models import PaymentRecord


def get_user_info(code=None):
    """
    获取用户openid
    :param code: 授权code
    """
    try:
        params = {
            "appid": WeiXinInfo.appid,
            "secret": WeiXinInfo.app_secret,
            "code": str(code),
            "grant_type": "authorization_code"
        }
        response = requests.get(url=WeiXinUri.access_token_uri, params=params)

        data = response.json()
        if data.get("errcode"):
            return redirect(WeiXinInfo.redirect + "?openid=''", code=302)

        return redirect(WeiXinInfo.redirect + "?openid=" + data.get("openid"), code=302)
    except Exception as e:
        current_app.logger.error(f"error:{e}, traceback:{traceback.format_exc()}")
        return redirect(WeiXinInfo.redirect + "?openid=''", code=302)


def get_order_record(openid=None):
    """
    获取用户订单记录
    :param openid: 用户openid
    """
    try:
        data = []
        order_obj_list = db.session.query(PaymentRecord.name, PaymentRecord.amount, PaymentRecord.item_type,
                                          PaymentRecord.create_time, PaymentRecord.pay_status
                                          ).filter(PaymentRecord.openid == openid,
                                                   PaymentRecord.trade_state == "SUCCESS"
                                                   ).order_by(db.desc(PaymentRecord.create_time)).all()
        if not order_obj_list:
            return return_pack(code=Code.HSL_OK, msg="ok", status=True, info=data)

        for order_obj in order_obj_list:
            data.append({
                "name": order_obj.name,
                "amount": order_obj.amount,
                "item_type": order_obj.item_type,
                # "status": order_obj.status,  # (1待支付，2取消支付，3支付成功(待确认)，4已确认，5支付失败)
                "pay_time": order_obj.create_time.__str__()
            })

        return return_pack(code=Code.HSL_OK, msg="ok", status=True, info=data)
    except Exception as e:
        current_app.logger.error(f"error:{e}, traceback:{traceback.format_exc()}")
        return return_pack(code=Code.HSL_ERROR, msg="获取用户信息异常")
