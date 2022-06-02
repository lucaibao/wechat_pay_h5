# -*- coding: utf-8 -*-
# @Author: Cai bao
# -*- coding: utf-8 -*-
# @Author: cai bao
# @Email: lucaibao@houselai.com
# @Time: 2022/5/17
import os


class WeiXinInfo:
    """
    公众平台
    https://mp.weixin.qq.com/cgi-bin/loginpage?t=wxm2-login&lang=zh_CN
    商户平台
    https://pay.weixin.qq.com/index.php/core/home/login?return_url=%2Fpublic%2Fwxpay%2Fapply_guidee
    商户平台绑定AppID  在 “商户平台--产品中心--AppID账号管理” 关联AppID
    网页获取openid  需在 "开发 - 接口权限 - 网页服务 - 网页帐号 - 网页授权获取用户基本信息" 的配置选项中，修改授权回调域名
    前端接入JS-SDK(前端唤起支付组件) 需在 "微信公众平台--公众号设置--功能设置" 里填写JS接口安全域名
    证书相关： https://pay.weixin.qq.com/wiki/doc/apiv3/wechatpay/wechatpay3_1.shtml
    """
    # 由于微信支付的产品体系全部搭载于微信的社交体系之上，所以直连商户或服务商接入微信支付之前，都需要有一个微信社交载体，该载体对应的ID即为APPID。对于直连商户，该社交载体可以是公众号，小程序或APP
    appid = ""
    # 开发者密码(AppSecret);  在 "微信公众平台--开发--基本配置--公众号开发信息" 中获取
    app_secret = ""
    # 商户号;  需在 "商户平台--账户中心--商户信息" 中查看
    mch_id = ""
    # 商户名称; 在 "商户平台--账户中心--商户信息" 中查看
    mch_name = ""
    # API v3秘钥; 在 "商户平台--账户中心--API安全--设置APIv3秘钥"
    api_v3_key = ""
    # 支付通知回调地址; 在 "商户平台—>产品中心—>H5支付—>申请开通"
    redirect_uri = ""
    # 商户证书序列号; 在 "商户平台--API安全--申请API证书--管理证书" 中查看
    cert_serial_no = ""
    # 作废  27AACF03C3EC4635EA366FA83BF4C18E760A9481
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # 商户证书  商户可登录微信商户平台，在【账户中心】->【API安全】目录下载证书
    client_cert = os.path.join(base_dir, 'cert', 'apiclient_cert.pem')
    # 商户秘钥(PKCS#8格式化后的密钥格式)
    client_key = os.path.join(base_dir, 'cert', 'apiclient_key.pem')
    # 原始商户秘钥(python可用商户秘钥需为原始商户秘钥，可通过openssl rsa -in apiclient_key.pem -out ./client_key.pem进行转换)
    client_private_key = os.path.join(base_dir, 'cert', 'client_key.pem')
    # 微信平台证书
    wxp_cert = os.path.join(base_dir, 'cert', 'wxp_cert.pem')
    # 签名方式
    sign_type = "RSA"

    # 微信支付结果通知回调地址
    notify_url = "https://xxx.com/app/pay/callback.json"
    # 微信支付付款描述
    pay_desc = "检测项目"

    # 获取code后重定向到前端页面
    redirect = "https://xxxxx.com/"


class WeiXinUri:
    # code换取网页授权access_token
    access_token_uri = "https://api.weixin.qq.com/sns/oauth2/access_token"
    # 刷新access_token
    refresh_token_uri = "https://api.weixin.qq.com/sns/oauth2/refresh_token"
    # 获取access token
    get_token_uri = "https://api.weixin.qq.com/cgi-bin/token"
    # 获取jsapi_ticket
    get_ticket_uri = "https://api.weixin.qq.com/cgi-bin/ticket/getticket"


class PayStatus:
    UNPAID = 1  # 待支付
    CANCEL = 2  # 取消支付
    UNCONFIRMED = 3  # 待确认
    CONFIRMED = 4  # 已确认
    FAIL = 5  # 支付失败


class ItemType:
    COMMON = 1  # 常规
    QUICK = 2  # 快速
    OTHER = 3  # 其他


class CacheInfo:
    access_token_flag = "ACCESS_TOKEN_FLAG_"
    jsapi_ticket_flag = "JSAPI_TICKET_FLAG_"
