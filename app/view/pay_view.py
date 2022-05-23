# -*- coding: utf-8 -*-
# @Author: cai bao
# @Email: lucaibao@houselai.com
# @Time: 2022/5/17
import traceback
import json

from flask import request, Blueprint, current_app, Response

from common.json_data import return_pack
from common.status_code import Code
from util.tool_ import Tool
from config.wechat_info import ItemType
from app.model.pay_model import get_jsapi_data, dispose_pay_callback, pay_advice_dispose, get_wx_config_data

pay_api = Blueprint("pay_api", __name__)
pay_api.__doc__ = "H5支付"


@pay_api.route("/wx_config.json", methods=["POST"])
def wx_config():
    """接口注入权限验证配置"""
    try:
        params = request.get_json()

        try:
            url = str(params.get("url", ""))  # 当前网页的URL，不包含#及其后面部分
        except ValueError:
            return return_pack(code=Code.HSL_PARAMS_ERROR, msg="参数类型错误")

        if not url:
            return return_pack(code=Code.HSL_PARAMS_MISS, msg="请携带当前网页的url")

        data = get_wx_config_data(url=url)

        return data
    except Exception as e:
        current_app.logger.error(f"error:{e}, traceback:{traceback.format_exc()}")
        return return_pack(code=Code.HSL_ERROR, msg="服务器处理异常")


@pay_api.route("/jsapi.json", methods=["POST"])
def jsapi():
    """微信统一下单(预下单)，调用微信支付api，返回预支付交易会话标识"""
    try:
        params = request.get_json()

        try:
            name = str(params.get("name", ""))  # 用户姓名
            phone = str(params.get("phone", ""))  # 手机号
            amount = int(params.get("amount", 0))  # 付款金额
            item_type = int(params.get("item_type", 0))  # 项目类型（1常规核酸检测、2快速核酸检测、3其他项目）
            openid = str(params.get("openid", ""))  # 用户openid
        except ValueError:
            return return_pack(code=Code.HSL_PARAMS_ERROR, msg="参数类型错误")

        if item_type not in ([ItemType.COMMON, ItemType.QUICK, ItemType.OTHER]):
            return return_pack(code=Code.HSL_PARAMS_MISS, msg="付款项目类型错误")

        if item_type != ItemType.OTHER and not name:
            return return_pack(code=Code.HSL_PARAMS_MISS, msg="请填写姓名")

        if not name:
            name = "-"

        if item_type != ItemType.OTHER and (not phone or not Tool.verify_phone(phone=phone)):
            return return_pack(code=Code.HSL_PARAMS_MISS, msg="请填写正确的手机号")

        if not amount:
            return return_pack(code=Code.HSL_PARAMS_MISS, msg="缺少付款金额")

        if not openid:
            return return_pack(code=Code.HSL_PARAMS_MISS, msg="缺少用户openid")

        data = get_jsapi_data(name, phone, amount, item_type, openid)

        return data
    except Exception as e:
        current_app.logger.error(f"error:{e}, traceback:{traceback.format_exc()}")
        return return_pack(code=Code.HSL_ERROR, msg="服务器处理异常")


@pay_api.route("/pay_advice.json", methods=["POST"])
def pay_advice():
    """
    JSAPI调起支付结果反馈
    """
    try:
        params = request.get_json()

        try:
            out_trade_no = str(params.get("out_trade_no", ""))  # 商户订单号(商户系统内部订单号,同一个商户保证里面的订单号唯一)
            status = int(params.get("status", 0))  # 支付状态  2取消支付，3支付成功(待确认)，5支付失败
        except ValueError:
            return return_pack(code=Code.HSL_PARAMS_ERROR, msg="参数类型错误")

        current_app.logger.info(f"JSAPI调起支付结果反馈; out_trade_no:{out_trade_no}, status:{status}")
        if not out_trade_no:
            return return_pack(code=Code.HSL_PARAMS_MISS, msg="商户订单号不能为空")

        if not status:
            return return_pack(code=Code.HSL_PARAMS_MISS, msg="缺少支付状态")

        data = pay_advice_dispose(out_trade_no=out_trade_no, status=status)

        return data
    except Exception as e:
        current_app.logger.error(f"error:{e}, traceback:{traceback.format_exc()}")
        return return_pack(code=Code.HSL_ERROR, msg="商户处理异常")


@pay_api.route("/callback.json", methods=["GET", "POST"])
def callback():
    """
    微信支付通知回调接口
    """
    try:
        params = request.get_json()
        # 日志记录
        current_app.logger.info(f"微信支付通知回调返回数据: {params}")

        data = dispose_pay_callback(params=params)

        return data
    except Exception as e:
        current_app.logger.error(f"error:{e}, traceback:{traceback.format_exc()}")
        return Response(json.dumps({"code": "FAIL", "message": "商户处理异常"}), status=500, content_type="application/json")
