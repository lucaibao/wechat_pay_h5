# -*- coding: utf-8 -*-
# @Author: cai bao
# @Email: lucaibao@houselai.com
# @Time: 2022/5/17
import os

from flask import current_app, Blueprint, send_from_directory

from common.json_data import return_pack
from common.status_code import Code

verify_api = Blueprint("verify_api", __name__)
verify_api.__doc__ = "域名验证"


@verify_api.route("/<path:name>", methods=["GET"])
def verify(name):
    """
    获取文件(域名安全校验)
    """
    try:
        file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))), "doc")
        file = os.path.join(file_path, name)
        if not file:
            return return_pack(code=Code.HSL_DATA_NOT_EXIST, msg="文件不存在")

        return send_from_directory(file_path, name)
    except Exception as e:
        current_app.logger.error(e)
        return return_pack(code=Code.HSL_ERROR, msg="服务器处理异常")
