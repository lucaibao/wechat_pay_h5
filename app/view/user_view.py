# -*- coding: utf-8 -*-
# @Author: cai bao
# @Email: lucaibao@houselai.com
# @Time: 2022/5/17
import traceback

from flask import request, Blueprint, current_app, redirect

from common.json_data import return_pack
from common.status_code import Code
from config.wechat_info import WeiXinInfo
from app.model.user_model import get_user_info, get_order_record

user_api = Blueprint("user_api", __name__)
user_api.__doc__ = "用户相关"


@user_api.route("/oauth_response.json", methods=["GET", "POST"])
def get_code():
    """
    code换取openid
    微信中打开此链接
    https://open.weixin.qq.com/connect/oauth2/authorize?
    appid=wx520c15f417810387
    &redirect_uri=https%3A%2F%2Fcoupons.ruiheshenzhen.com%2Fapp%2Fuser%2Foauth_response.json
    &response_type=code
    &scope=snsapi_base
    &state=123#wechat_redirect

    其中redirect_uri 为授权后重定向的回调链接地址， 需使用 urlEncode 对链接进行处理
    """
    try:
        try:
            code = str(request.values.get("code", ""))
            state = str(request.values.get("state", ""))
        except ValueError:
            return redirect(WeiXinInfo.redirect + "?openid=''", code=302)
        current_app.logger.info(f"code:{code}, state:{state}")

        data = get_user_info(code)

        return data
    except Exception as e:
        current_app.logger.error(f"error:{e}, traceback:{traceback.format_exc()}")
        return redirect(WeiXinInfo.redirect+"?openid=''", code=302)


@user_api.route("/order_record.json", methods=["POST"])
def order_record():
    """用户订单记录"""
    try:
        params = request.get_json()

        try:
            openid = str(params.get("openid", ""))  # 用户openid
        except ValueError:
            return return_pack(code=Code.HSL_PARAMS_ERROR, msg="参数类型错误")

        if not openid:
            return return_pack(code=Code.HSL_PARAMS_MISS, msg="缺少用户openid")

        data = get_order_record(openid)

        return data
    except Exception as e:
        current_app.logger.error(f"error:{e}, traceback:{traceback.format_exc()}")
        return_pack(code=Code.HSL_ERROR, msg="服务器处理异常")
