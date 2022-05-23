# -*- coding: utf-8 -*-
# @Author: cai bao
# @Email: lucaibao@houselai.com
# @Time: 2022/5/17
# @Desc: 数据库模型类
from util.mysql_ import db


class PaymentRecord(db.Model):
    """收款H5-微信支付记录"""
    __tablename__ = "payment_record"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    openid = db.Column(db.String(255), nullable=False, default="", comment="用户openid")
    appid = db.Column(db.String(255), nullable=False, default="", index=True, comment="应用id")
    mch_id = db.Column(db.String(255), nullable=False, default="", comment="商户号")
    out_trade_no = db.Column(db.String(255), nullable=False, default="", unique=True, comment="商户订单号")
    desc = db.Column(db.Text, comment="商品描述")
    amount = db.Column(db.Integer, nullable=False, comment="订单金额(用户支付金额")
    item_type = db.Column(db.SmallInteger, nullable=False, comment="项目类型（1常规核酸检测、2快速核酸检测、3其他项目等等）")
    name = db.Column(db.String(255), nullable=False, default="", comment="付款人姓名")
    phone = db.Column(db.String(255), nullable=False, default="", comment="手机号")
    wx_id = db.Column(db.String(255), nullable=False, default="", comment="微信支付通知id")
    notice_time = db.Column(db.String(255), nullable=False, default="", comment="微信支付反馈时间")
    transaction_id = db.Column(db.String(255), nullable=False, default="", comment="微信支付订单号")
    trade_type = db.Column(db.String(255), nullable=False, default="", comment="交易类型(JSAPI(公众号支付),NATIVE(扫码支付),"
                                                                               "APP(APP支付),MICROPAY(付款码支付),"
                                                                               "MWEB(H5支付),FACEPAY(刷脸支付)")
    trade_state = db.Column(db.String(255), nullable=False, default="", comment="SUCCESS：支付成功,REFUND：转入退款,"
                                                                                "NOTPAY：未支付,CLOSED：已关闭,"
                                                                                "REVOKED：已撤销（付款码支付）,"
                                                                                "USERPAYING：用户支付中（付款码支付）,"
                                                                                "PAYERROR：支付失败(其他原因，如银行返回失败)")
    trade_state_desc = db.Column(db.String(255), nullable=False, default="", comment="交易状态描述")
    bank_type = db.Column(db.String(255), nullable=False, default="", comment="付款银行")
    success_time = db.Column(db.String(255), nullable=False, default="", comment="支付完成时间")
    total = db.Column(db.Integer, nullable=False, comment="订单总金额，单位为分")
    payer_total = db.Column(db.Integer, nullable=False, comment="用户支付金额，单位为分")
    currency = db.Column(db.String(255), nullable=False, default="", comment="货币类型")
    payer_currency = db.Column(db.String(255), nullable=False, default="", comment="用户支付币种")
    pay_status = db.Column(db.SmallInteger, nullable=False, default=0, comment="支付状态(1待支付，2取消支付，3待确认，4已确认，"
                                                                               "5支付失败)")
    note = db.Column(db.String(255), nullable=False, default="", comment="备注")
    create_time = db.Column(db.DateTime, comment="创建时间")
    modify_time = db.Column(db.DateTime, comment="编辑时间")

    def __init__(self, openid, appid, mch_id, out_trade_no, desc, amount, item_type, name, phone, wx_id, notice_time,
                 transaction_id, trade_type, trade_state, trade_state_desc, bank_type, success_time, total, payer_total,
                 currency, payer_currency, pay_status, note, create_time, modify_time):
        self.openid = openid
        self.appid = appid
        self.mch_id = mch_id
        self.out_trade_no = out_trade_no
        self.desc = desc
        self.amount = amount
        self.item_type = item_type
        self.name = name
        self.phone = phone
        self.wx_id = wx_id
        self.notice_time = notice_time
        self.transaction_id = transaction_id
        self.trade_type = trade_type
        self.trade_state = trade_state
        self.trade_state_desc = trade_state_desc
        self.bank_type = bank_type
        self.success_time = success_time
        self.total = total
        self.payer_total = payer_total
        self.currency = currency
        self.payer_currency = payer_currency
        self.pay_status = pay_status
        self.note = note
        self.create_time = create_time
        self.modify_time = modify_time
