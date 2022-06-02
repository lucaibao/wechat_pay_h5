# -*- coding: utf-8 -*-
# @Author: cai bao
# @Email: lucaibao@houselai.com
# @Time: 2022/5/25
import traceback
from io import BytesIO
from urllib.parse import quote

from flask import request, Blueprint, current_app, send_file

from common.json_data import return_pack
from common.status_code import Code
from config.download_info import ExcelInfo
from util.tool_ import Tool
from app.model.download_model import get_download_data


download_api = Blueprint("download_api", __name__)
download_api.__doc__ = "支付信息统计--文件下载"


@download_api.route("/download.json", methods=["GET"])
def download():
    """统计支付用户信息并下载"""
    try:
        try:
            start_time = str(request.values.get("start_time", ""))  # 统计日期--开始时间
            end_time = str(request.values.get("end_time", ""))  # 统计日期--结束时间
        except ValueError:
            return return_pack(code=Code.HSL_PARAMS_ERROR, msg="参数类型错误")
        if not start_time:
            return return_pack(code=Code.HSL_PARAMS_MISS, msg="请输入需要统计的开始时间")

        if not end_time:
            return return_pack(code=Code.HSL_PARAMS_MISS, msg="请输入需要统计的结束时间")

        if start_time > end_time:
            return return_pack(code=Code.HSL_PARAMS_ERROR, msg="开始时间要小于结束时间")

        # 格式调整，保证和数据库中success_time字段格式统一
        s_time = start_time + "T00:00:00+08:00"
        e_time = end_time + "T23:59:59+08:00"
        data = get_download_data(start_time=s_time, end_time=e_time)

        sio = BytesIO()
        workbook = Tool.excel(header=ExcelInfo.header, title=ExcelInfo.title, data=data)
        workbook.save(sio)
        sio.seek(0)

        start_time = start_time.replace("-", ".")
        end_time = end_time.replace("-", ".")
        filename = quote(ExcelInfo.header) + "(" + start_time + "-" + end_time + ")"
        response = send_file(sio, as_attachment=True, attachment_filename='{}.xsl'.format(filename))
        response.headers['Content-Type'] = 'application/x-xls'
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['Content-Disposition'] = 'attachment; filename={}.xls'.format(filename)

        return response
    except Exception as e:
        current_app.logger.error(f"error:{e}, traceback:{traceback.format_exc()}")
        return return_pack(code=Code.HSL_ERROR, msg="服务器处理异常")
