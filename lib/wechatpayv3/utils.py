# -*- coding: utf-8 -*-
# @Author: cai bao
# @Email: lucaibao@houselai.com
# @Time: 2022/5/17
import time
import random
import rsa
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric.padding import MGF1, OAEP
from cryptography.hazmat.primitives.hashes import SHA1
from util.tool_ import Tool


def calculate_sign(client_private_key, data):
    """
    签名; 使用商户私钥对待签名串进行SHA256 with RSA签名，并对签名结果进行Base64编码得到签名值
    :param client_private_key: 商户私钥
    :param data: 待签名数据
    :return :加签后的数据
    """
    with open(client_private_key, "r") as f:
        pri_key = f.read()
    private_key = rsa.PrivateKey.load_pkcs1(pri_key.encode('utf-8'))
    sign_result = rsa.sign(data.encode('utf-8'), private_key, "SHA-256")
    content = base64.b64encode(sign_result)
    return content.decode('utf-8')


def verify_sign(wx_pubkey, data, signature):
    """
    验签；使用微信支付平台公钥对验签名串和签名进行SHA256 with RSA签名验证
    :param wx_pubkey: 微信支付平台公钥
    :param data: 待验证的数据
    :param signature: 签名后的数据
    :return : True/False
    """
    with open(wx_pubkey, "r") as f:
        pub_key = f.read()
    pub_key = rsa.PublicKey.load_pkcs1(pub_key.encode('utf-8'))
    try:
        verify_result = rsa.verify(data.encode('utf-8'), base64.b64decode(signature), pub_key)
        print(verify_result)  # 验证成功后会返回加密方式(eg:SHA-256)，失败则报错raise VerificationError('Verification failed')
        return True
    except Exception as e:
        print(e)
        return False


def rsa_encrypt(text, certificate):
    """
    敏感信息加密
    """
    data = text.encode('UTF-8')
    public_key = certificate.public_key()
    cipher_byte = public_key.encrypt(
        plaintext=data,
        padding=OAEP(mgf=MGF1(algorithm=SHA1()), algorithm=SHA1(), label=None)
    )
    return base64.b64encode(cipher_byte).decode('UTF-8')


def aes_decrypt(api_v3_key, nonce, ciphertext, associated_data):
    """
    回调信息解密
    :param api_v3_key: API V3秘钥
    :param nonce: 加密使用的随机串初始化向量
    :param ciphertext: Base64编码后的密文
    :param associated_data: 附加数据包（可能为空）
    :return :解密后的数据
    """
    key_bytes = str.encode(api_v3_key)
    nonce_bytes = str.encode(nonce)
    ad_bytes = str.encode(associated_data)
    data = base64.b64decode(ciphertext)

    aes_gcm = AESGCM(key_bytes)
    return aes_gcm.decrypt(nonce_bytes, data, ad_bytes).decode('utf-8')


def create_sign_str(client_private_key, mch_id, serial_no, method, url, body, timestamp=None, randoms=None):
    """
    构造签名串
    1、微信支付API v3通过验证签名来保证请求的真实性和数据的完整性。
    2、商户需要使用自身的私钥对API URL、消息体等关键数据的组合进行SHA-256 with RSA签名
    3、请求的签名信息通过HTTP头Authorization 传递
    4、签名生成指南：https://pay.weixin.qq.com/wiki/doc/apiv3/wechatpay/wechatpay4_0.shtml
    :param client_private_key: 商户私钥
    :param mch_id: 商户号
    :param serial_no: 商户证书序列号
    :param method: 请求方式
    :param url: 请求url,去除域名部分得到参与签名的url,如果请求中有查询参数,url末尾应附加有'?'和对应的查询字符串
    :param body: 请求体
    :param timestamp: 时间戳
    :param randoms: 随机字符串
    :return : authorization
    """
    if not timestamp:
        timestamp = str(int(time.time()))

    if not randoms:
        randoms = Tool.random_str()

    sign_list = [method, url, timestamp, randoms, body]
    sign_str = "\n".join(sign_list) + "\n"

    signature = calculate_sign(client_private_key, sign_str)
    authorization = 'WECHATPAY2-SHA256-RSA2048  ' \
                    'mchid="{0}",' \
                    'nonce_str="{1}",' \
                    'signature="{2}",' \
                    'timestamp="{3}",' \
                    'serial_no="{4}"'.\
                    format(mch_id, randoms, signature, timestamp, serial_no)
    return authorization


def create_trade_no(phone=""):
    """
    构建商户订单号
    :param phone: 用户手机号
    :return : 返回16位长度的字符串
    """
    if len(phone):
        return str(phone) + "H" + str(int(time.time()*1000)) + random_str(3)
    else:
        return random_str(11) + "H" + str(int(time.time()*1000)) + random_str(3)


def random_str(length=32):
    """
    生成32位随机字符串
    :return :32位随机字符串
    """
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    rand = random.Random()
    return "".join([chars[rand.randint(0, len(chars) - 1)] for i in range(length)])
