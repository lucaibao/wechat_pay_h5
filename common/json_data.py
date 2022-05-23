# -*- coding: utf-8 -*-
# @Author: cai bao
# @Email: lucaibao@houselai.com
# @Time: 2022/5/17
from flask import jsonify


def return_pack(code=0, msg='', status=False, info=None):
    """
    拼接请求返回的信息
    @param code : 返回的状态码
    @param msg : 返回状态码描述
    @param status : 处理结果(True/False)
    @param info: 返回的数据
    """
    data = {"code": code, "msg": msg, "status": status}

    if info is not None:
        data["data"] = info
    else:
        data["data"] = {}

    return jsonify(data)
