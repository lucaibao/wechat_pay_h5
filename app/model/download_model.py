# -*- coding: utf-8 -*-
# @Author: cai bao
# @Email: lucaibao@houselai.com
# @Time: 2022/5/17
from flask import current_app
from util.mysql_ import db
from app.models import PaymentRecord


def get_download_data(start_time=None, end_time=None):
    """
    统计支付用户信息并下载
    :param start_time: 开始时间
    :param end_time: 结束时间
    """
    data = []
    try:
        pay_obj_list = db.session.query(PaymentRecord.name, PaymentRecord.phone, PaymentRecord.trade_state,
                                        PaymentRecord.trade_state_desc, PaymentRecord.total, PaymentRecord.success_time,
                                        PaymentRecord.out_trade_no, PaymentRecord.transaction_id
                                        ).filter(PaymentRecord.success_time > start_time,
                                                 PaymentRecord.success_time < end_time).all()
        if not pay_obj_list:
            return data

        for pay_obj in pay_obj_list:
            # 支付时间格式调整；原格式：2022-05-20T16:54:20+08:00  调整后：2022-05-20 16:54:20
            pay_time = pay_obj.success_time.split("+")[0].replace("T", " ")
            # 支付金额转成元
            total = int(pay_obj.total) / 100
            data.append([pay_obj.name, pay_obj.phone, total, pay_obj.out_trade_no, pay_obj.transaction_id, pay_time,
                         pay_obj.trade_state, pay_obj.trade_state_desc])

        return data
    except Exception as e:
        current_app.logger.error(f"获取支付统计信息异常，error:{e}")
        return data
