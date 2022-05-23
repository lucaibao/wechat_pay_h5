# 签名、验签、加密、解密的内部实现

## 微信网页授权

如果用户在微信客户端中访问第三方网页，公众号可以通过微信网页授权机制，来获取用户基本信息，进而实现业务逻辑。[网页授权](https://developers.weixin.qq.com/doc/offiaccount/OA_Web_Apps/Wechat_webpage_authorization.html)
> 说明: 在微信公众号请求用户网页授权之前，开发者需要先到公众平台官网中的“开发 - 接口权限 - 网页服务 - 网页帐号 - 网页授权获取用户基本信息”的配置选项中，修改授权回调域名。请注意，这里填写的是域名（是一个字符串），而不是URL，因此请勿加 http:// 等协议头；
### 第一步:获取code
```angular2html
参考链接(请在微信客户端中打开此链接体验)
静默授权:
https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx520c15f417810387&redirect_uri=https%3A%2F%2Fchong.qq.com%2Fphp%2Findex.php%3Fd%3D%26c%3DwxAdapter%26m%3DmobileDeal%26showwxpaytitle%3D1%26vb2ctag%3D4_2030_5_1194_60&response_type=code&scope=snsapi_base&state=123#wechat_redirect

弹窗授权:
https://open.weixin.qq.com/connect/oauth2/authorize?appid=wxf0e81c3bee622d60&redirect_uri=http%3A%2F%2Fnba.bluewebgame.com%2Foauth_response.php&response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect

用户同意授权后，页面将跳转至 redirect_uri/?code=CODE&state=STATE
```
### 第二步:通过coe换取网页授权access_token
```angular2html
获取 code 后，请求以下链接获取access_token 
https://api.weixin.qq.com/sns/oauth2/access_token?appid=APPID&secret=SECRET&code=CODE&grant_type=authorization_code
```



## 构造签名串

对应v3版微信支付api文档的[构造签名串](https://pay.weixin.qq.com/wiki/doc/apiv3/wechatpay/wechatpay4_0.shtml)部分。

```python
def create_sign_str(client_private_key, mch_id, serial_no, method, url, body, timestamp=None, randoms=None):
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
```

## 签名

对应v3版微信支付api文档的[计算签名值](https://pay.weixin.qq.com/wiki/doc/apiv3/wechatpay/wechatpay4_0.shtml)部分。

```angular2html
def calculate_sign(client_private_key, data):
    """
    使用商户私钥对待签名串进行SHA256 with RSA签名，并对签名结果进行Base64编码得到签名值
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
```


## 验证签名

对应v3版微信支付api文档的[签名验证](https://pay.weixin.qq.com/wiki/doc/apiv3/wechatpay/wechatpay4_1.shtml)部分。

```python
def verify_sign(wx_pubkey, data, signature):
    """
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
```


## 回调信息解密

对应v3版微信支付api文档的[证书和回调报文解密](https://pay.weixin.qq.com/wiki/doc/apiv3/wechatpay/wechatpay4_2.shtml)部分。

```python
def aes_decrypt(api_v3_key, nonce, ciphertext, associated_data):
    """
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
```


## 敏感信息加密

对应v3版微信支付api文档的[敏感信息加解密](https://pay.weixin.qq.com/wiki/doc/apiv3/wechatpay/wechatpay4_3.shtml)的加密部分。

```python
def rsa_encrypt(text, certificate):
    data = text.encode('UTF-8')
    public_key = certificate.public_key()
    cipherbyte = public_key.encrypt(
        plaintext=data,
        padding=OAEP(mgf=MGF1(algorithm=SHA1()), algorithm=SHA1(), label=None)
    )
    return b64encode(cipherbyte).decode('UTF-8')
```


## 敏感信息解密

对应v3版微信支付api文档的[敏感信息加解密](https://pay.weixin.qq.com/wiki/doc/apiv3/wechatpay/wechatpay4_3.shtml)的解密部分。

```python
def rsa_encrypt(text, certificate):
    data = text.encode('UTF-8')
    public_key = certificate.public_key()
    cipher_byte = public_key.encrypt(
        plaintext=data,
        padding=OAEP(mgf=MGF1(algorithm=SHA1()), algorithm=SHA1(), label=None)
    )
    return base64.b64encode(cipher_byte).decode('UTF-8')
```


## 注意事项

以上涉及到的几项签名如果计划抽出来单独使用，需要引入[cryptography](https://pypi.org/project/cryptography/)包。