# -*- coding: utf-8 -*-
# @Author: cai bao
# @Email: lucaibao@houselai.com
# @Time: 2022/5/17
import time
import ast
import json
from datetime import datetime
import traceback
import requests

from flask import current_app, jsonify, Response
import hashlib

from common.json_data import return_pack
from common.status_code import Code
from config.wechat_info import WeiXinInfo, PayStatus, WeiXinUri, CacheInfo
from util.mysql_ import db
from util.redis_ import redis_client
from util.tool_ import Tool
from app.models import PaymentRecord
from lib.wechatpayv3.wechat_pay import WechatPay
from lib.wechatpayv3.utils import create_trade_no, calculate_sign, aes_decrypt


def get_access_token():
    """
    获取access_token（有效期7200秒，开发者必须在自己的服务全局缓存access_token）
    https://developers.weixin.qq.com/doc/offiaccount/Basic_Information/Get_access_token.html
    """
    try:
        cache_flag = CacheInfo.access_token_flag + WeiXinInfo.appid
        # 查看redis缓存中是否有access_token值，有则直接用，无则调接口获取并缓存
        access_token = redis_client.get(cache_flag)
        if access_token:
            return True, access_token.decode()

        params = {
            "grant_type": "client_credential",
            "appid": WeiXinInfo.appid,
            "secret": WeiXinInfo.app_secret
        }
        token_response = requests.get(url=WeiXinUri.get_token_uri, params=params).json()
        if token_response.get("errcode"):
            current_app.logger.error(f"获取access_token失败 return:{token_response}")
            return False, token_response

        # 调接口获取到数据，中间网络传输会有一点时间损耗，为保证缓存中的值绝对处于有效期内，缓存时将过期时间设置的低于官方给的过期时间
        redis_client.setex(cache_flag, token_response.get("expires_in")-10, token_response.get("access_token"))
        return True, token_response.get("access_token")
    except Exception as e:
        current_app.logger.error(f"获取access_token异常，error:{e}")
        return False, str(traceback.format_exc())


def get_jsapi_ticket():
    """
    用第一步拿到的access_token 采用http GET方式请求获得jsapi_ticket（有效期7200秒，开发者必须在自己的服务全局缓存jsapi_ticket）
    https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=ACCESS_TOKEN&type=jsapi
    """
    try:
        cache_flag = CacheInfo.jsapi_ticket_flag + WeiXinInfo.appid
        # 查看redis缓存中是否有jsapi_ticket值，有则直接用，无则调接口获取并缓存
        jsapi_ticket = redis_client.get(cache_flag)
        if jsapi_ticket:
            return True, jsapi_ticket.decode()

        status, content = get_access_token()
        if not status:
            return False, f"获取access_token失败, {content}"

        params = {
            "access_token": content,
            "type": "jsapi"
        }
        ticket_response = requests.get(url=WeiXinUri.get_ticket_uri, params=params).json()
        if int(ticket_response.get("errcode")) != 0:
            current_app.logger.error(f"获取jsapi_ticket失败 return:{ticket_response}")
            return False, f"获取jsapi_ticket失败, {ticket_response}"

        # 调接口获取到数据，中间网络传输会有一点时间损耗，为保证缓存中的值绝对处于有效期内，缓存时将过期时间设置的低于官方给的过期时间
        redis_client.setex(cache_flag, ticket_response.get("expires_in")-10, ticket_response.get("ticket"))
        return True, ticket_response.get("ticket")
    except Exception as e:
        current_app.logger.error(f"获取access_token异常，error:{e}")
        return False, f"获取jsapi_ticket异常, error:{str(traceback.format_exc())}"


def get_wx_config_data(url=""):
    """
    :param url: 当前网页的URL，不包含#及其后面部分
    JS-SDK使用权限签名算法
    https://developers.weixin.qq.com/doc/offiaccount/OA_Web_Apps/JS-SDK.html#62
    """
    try:
        # 获取jsapi_ticket
        status, content = get_jsapi_ticket()
        if not status:
            return return_pack(code=Code.HSL_DATA_ERROR, msg=content)

        # 步骤1. 对所有待签名参数按照字段名的ASCII 码从小到大排序（字典序）后，使用URL键值对的格式（即key1=value1&key2=value2…）拼接成字符串string
        timestamp = str(int(time.time()))
        nonce_str = Tool.random_str(32)
        params = {
            "noncestr": nonce_str,
            "timestamp": timestamp,
            "jsapi_ticket": content,
            "url": url
        }
        string = "&".join(['%s=%s' % (key, params[key]) for key in sorted(params)])

        # 步骤2. 对string进行sha1签名，得到signature：
        sign = hashlib.sha1()
        sign.update(string.encode())
        signature = sign.hexdigest()

        data = {
            "appId": WeiXinInfo.appid,
            "timestamp": timestamp,
            "nonceStr": nonce_str,
            "signature": signature
        }

        return return_pack(code=Code.HSL_OK, msg="ok", status=True, info=data)
    except Exception as e:
        current_app.logger.error(f"error:{e}, traceback:{traceback.format_exc()}")
        return return_pack(code=Code.HSL_ERROR, msg="接口注入权限验证配置")


def get_jsapi_data(name=None, phone=None, amount=None, item_type=None, openid=None):
    """
    JSAPI下单; 商户系统先调用该接口在微信支付服务后台生成预支付交易单，返回正确的预支付交易会话标识
    :param name: 付款人姓名
    :param phone: 手机号
    :param amount: 订单总金额，单位为分。
    :param item_type: #项目类型（1常规核酸检测、2快速核酸检测、3其他项目等等）
    :param openid: 用户openid
    """
    try:
        wx_pay = WechatPay(appid=WeiXinInfo.appid, mch_id=WeiXinInfo.mch_id, notify_url=WeiXinInfo.notify_url,
                           client_private_key=WeiXinInfo.client_private_key, serial_no=WeiXinInfo.cert_serial_no,
                           pay_desc=WeiXinInfo.pay_desc)

        # 商户订单号
        out_trade_no = create_trade_no(phone=phone)
        # JSAPI下单请求参数
        params = {
            "openid": openid,
            "out_trade_no": out_trade_no,
            "amount": amount
        }

        # jsapi下单获取到发起支付的必要参数prepay_id
        status, response = wx_pay.jsapi(params=params)
        current_app.logger.info(f"jsapi下单获取支付参数prepay_id:{response}")
        if not status or response.get("errcode"):
            return return_pack(code=Code.HSL_DATA_ERROR, msg=f"jsapi下单失败, return:{response}")
        prepay_id = response.get("prepay_id")

        # 用户支付信息入库
        pay_obj = PaymentRecord(openid=openid, appid=WeiXinInfo.appid, mch_id=WeiXinInfo.mch_id,
                                out_trade_no=out_trade_no, desc=WeiXinInfo.pay_desc, amount=amount, item_type=item_type,
                                name=name, phone=phone, wx_id="", notice_time="", transaction_id="",
                                trade_type="", trade_state="", trade_state_desc="", bank_type="", success_time="",
                                total=0, payer_total=0, currency="", payer_currency="", pay_status=PayStatus.UNPAID,
                                note="用户下单", create_time=datetime.now(), modify_time=datetime.now())
        try:
            db.session.add(pay_obj)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f'处理预下单异常-用户支付信息入库失败, error:{e}')
            return return_pack(code=Code.HSL_SQL_ERROR, msg="用户支付信息入库失败")

        # jsapi调起支付API
        timestamp = str(int(time.time()))
        nonce_str = Tool.random_str(32)
        package = "prepay_id=" + str(prepay_id)
        sign_str = "\n".join([WeiXinInfo.appid, timestamp, nonce_str, package]) + "\n"
        data = {
            "appId": WeiXinInfo.appid,  # 应用ID
            "timeStamp": timestamp,  # 时间戳
            "nonceStr": nonce_str,  # 随机字符串
            "package": package,  # 订单详情扩展字符串
            "signType": WeiXinInfo.sign_type,  # 签名方式
            "paySign": calculate_sign(WeiXinInfo.client_private_key, sign_str),  # 签名
            "out_trade_no": out_trade_no  # 商户订单号
        }
        current_app.logger.info(f"jsapi调起支付API, 返回数据: {data}")
        return return_pack(code=Code.HSL_OK, msg="ok", status=True, info=data)
    except Exception as e:
        current_app.logger.error(f"error:{e}, traceback:{traceback.format_exc()}")
        return return_pack(code=Code.HSL_ERROR, msg="处理预下单异常")


def pay_advice_dispose(out_trade_no: str, status: int):
    """
    用户支付结果通知
    :param out_trade_no: 商户订单号
    :param status: 支付状态(1待支付，2取消支付，3支付成功(待确认)，4已确认，5支付失败)
    """
    try:
        # 查询微信支付记录
        pay_obj = db.session.query(PaymentRecord).filter(PaymentRecord.out_trade_no == out_trade_no).first()
        if not pay_obj:
            current_app.logger.error(
                f"更新支付状态失败,out_trade_no:{out_trade_no}, status:{status}, pay_obj:{pay_obj}"
            )
            return return_pack(code=Code.HSL_DATA_NOT_EXIST, msg="未查找到用户下单记录")

        # 查看是否收到微信支付回调，收到微信回调且显示支付成功则直接返回
        data = {}
        trade_state = pay_obj.trade_state
        if trade_state == "SUCCESS":
            data = {
                "pay_time": pay_obj.create_time.__str__()
            }
            return return_pack(code=Code.HSL_OK, msg="ok", status=True, info=data)

        # 如果还未收到微信回调，则根据JS调起支付反馈的结果更新订单状态
        pay_obj.pay_status = status
        if status == 2:
            pay_obj.note = "取消支付"
        elif status == 3:
            pay_obj.note = "支付成功(待确认)"
        elif status == 5:
            pay_obj.note = "支付失败"
            # 关闭订单
            """
            https://pay.weixin.qq.com/wiki/doc/apiv3/apis/chapter3_1_3.shtml
            以下情况需要调用关单接口：
            1、商户订单支付失败需要生成新单号重新发起支付，要对原订单号调用关单，避免重复支付；
            2、系统下单后，用户支付超时，系统退出不再受理，避免用户继续，请调用关单接口。
            """
            current_app.logger.info(f"用户支付失败，关闭订单；out_trade_no:{out_trade_no}")
            wx_pay = WechatPay(appid=WeiXinInfo.appid, mch_id=WeiXinInfo.mch_id, notify_url=WeiXinInfo.notify_url,
                               client_private_key=WeiXinInfo.client_private_key, serial_no=WeiXinInfo.cert_serial_no,
                               pay_desc=WeiXinInfo.pay_desc)
            wx_pay.pay_close(out_trade_no=out_trade_no)
        pay_obj.modify_time = datetime.now()

        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"更新用户支付状态失败 out_trade_no:{out_trade_no}, status:{status}, error:{e}")
            return return_pack(code=Code.HSL_ERROR, msg="更新用户支付状态失败")

        return return_pack(code=Code.HSL_OK, msg="ok", status=True, info=data)
    except Exception as e:
        current_app.logger.error(f"error:{e}, traceback:{traceback.format_exc()}")
        return return_pack(code=Code.HSL_ERROR, msg="更新用户支付状态异常")


def dispose_pay_callback(params: dict):
    """
    用户支付结果通知
    :param params: 支付结果通知
    回调示例：
    {
        "id":"EV-2018022511223320873",              # 通知ID
        "create_time":"2015-05-20T13:29:35+08:00",  # 通知创建时间
        "resource_type":"encrypt-resource",         # 通知数据类型
        "event_type":"TRANSACTION.SUCCESS",         # 通知类型
        "resource":{                                # 通知资源数据json格式
            "algorithm":"AEAD_AES_256_GCM",         # 加密算法类型
            "ciphertext":"...",                     # 数据密文
            "nonce":"...",                          # 随机串
            "original_type":"transaction",          # 原始类型
            "associated_data":""                    # 附加数据
        },
        "summary":"支付成功"                         # 回调摘要
    }
    通知应答
    接收成功：HTTP应答状态码需返回200或204，无需返回应答报文。
    接收失败：HTTP应答状态码需返回5XX或4XX，同时需返回应答报文，格式如下：
    {
    "code": "FAIL",
    "message": "失败"
    }
    """
    try:
        resource = params.get("resource", {})  # 通知资源数据json格式

        # 参数解密  官方文档： https://pay.weixin.qq.com/wiki/doc/apiv3/apis/chapter3_1_5.shtml
        decrypt_data = aes_decrypt(api_v3_key=WeiXinInfo.api_v3_key, associated_data=resource.get("associated_data"),
                                   ciphertext=resource.get("ciphertext"), nonce=resource.get("nonce"))
        try:
            resource = json.loads(decrypt_data)
        except TypeError:
            resource = ast.literal_eval(decrypt_data)

        # 查询微信支付记录
        pay_obj = db.session.query(PaymentRecord).filter(PaymentRecord.out_trade_no == resource.get("out_trade_no")
                                                         ).first()
        if not pay_obj:
            current_app.logger.error(
                f"更近商户订单号查找支付记录失败,pay_obj:{pay_obj}, 回调数据为:{params}, 解密数据为:{decrypt_data}"
            )
            return Response(json.dumps({"code": "FAIL", "message": "根据商户号查找用户下单记录失败"}), status=500,
                            content_type="application/json")
        pay_obj.wx_id = params.get("id")
        pay_obj.notice_time = params.get("create_time")  # 通知创建时间
        pay_obj.transaction_id = resource.get("transaction_id")  # 微信支付系统生成的订单号
        pay_obj.trade_type = resource.get("trade_type")  # 交易类型
        pay_obj.trade_state = resource.get("trade_state")  # 交易状态
        pay_obj.trade_state_desc = resource.get("trade_state_desc")  # 交易状态描述
        pay_obj.bank_type = resource.get("bank_type")  # 银行类型
        pay_obj.success_time = resource.get("success_time")  # 支付完成时间
        pay_obj.total = resource.get("amount").get("total")  # 订单总金额，单位为分。
        pay_obj.payer_total = resource.get("amount").get("payer_total")  # 用户支付金额，单位为分。
        pay_obj.currency = resource.get("amount").get("currency")  # 货币类型
        pay_obj.payer_currency = resource.get("amount").get("payer_currency")  # 用户支付币种
        pay_obj.pay_status = PayStatus.CONFIRMED
        pay_obj.modify_time = datetime.now()

        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"支付回调处理用户支付状态失败 params:{params}, error:{e}")
            return Response(json.dumps({"code": "FAIL", "message": "支付回调更新用户支付状态失败"}), status=500,
                            content_type="application/json")

        return jsonify({"code": "SUCCESS", "message": "成功"})
    except Exception as e:
        current_app.logger.error(f"error:{e}, traceback:{traceback.format_exc()}")
        return Response(json.dumps({"code": "FAIL", "message": "处理回调数据异常"}), status=500,
                        content_type="application/json")
