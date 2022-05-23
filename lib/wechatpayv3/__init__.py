import requests

# 网页授权
# 1、以snsapi_base为scope发起的网页授权，是用来获取进入页面的用户的openid的，并且是静默授权并自动跳转到回调页的。用户感知的就是直接进入了回调页（往往是业务页面）
base_url = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx186e63765e9bd457&redirect_uri=https%3A%2F%2Fcoupons.ruiheshenzhen.com%2Fapp%2Fuser%2Foauth_response.json&response_type=code&scope=snsapi_base&state=STATE#wechat_redirect"
# 2、以snsapi_userinfo为scope发起的网页授权，是用来获取用户的基本信息的。但这种授权需要用户手动同意，并且由于用户同意过，所以无须关注，就可在授权后获取该用户的基本信息。
userinfo_url = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx186e63765e9bd457&redirect_uri=https%3A%2F%2Fcoupons.ruiheshenzhen.com%2Fapp%2Fpay_api%2Foauth_response.json&response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect"


# 第二步：通过code换取网页授权access_token
"""
首先请注意，这里通过code换取的是一个特殊的网页授权access_token,与基础支持中的access_token（该access_token用于调用其他接口）不同。公众号可通过下述接口来获取网页授权access_token。如果网页授权的作用域为snsapi_base，则本步骤中获取到网页授权access_token的同时，也获取到了openid，snsapi_base式的网页授权流程即到此为止。

尤其注意：由于公众号的secret和获取到的access_token安全级别都非常高，必须只保存在服务器，不允许传给客户端。后续刷新access_token、通过access_token获取用户信息等步骤，也必须从服务器发起
获取code后，请求以下链接获取access_token： https://api.weixin.qq.com/sns/oauth2/access_token?appid=APPID&secret=SECRET&code=CODE&grant_type=authorization_code
"""
code = "091NRmGa1ipGcD0s8PFa1NyyWp2NRmGf"
# url = "https://api.weixin.qq.com/sns/oauth2/access_token?appid=wx186e63765e9bd457&secret=9d6c1fe531fe51312198be32231ed2d2&code={}&grant_type=authorization_code".format(code)
# res = requests.get(url=url)
# print(res.json())
# # code换取网页授权access_token
# info = {
#     'access_token': '56_6TSPvTwWvwp8sJaVkpC7dNKzY5LcVaBMOvIdo-_pQ8fA6rzFzNbcLC4BmN4JfLk_9AphVNrK75kL9-EEOjYLou6CYis5Dq2VgyDRm5RM0Ng',
#     'expires_in': 7200,
#     'refresh_token': '56_zOYqq-oFZdx5t1wvEorsJp9Fl-YX9t1Xj_RwL7EAphg3wBq6C0_JiocsketdEXZ18xOKgaCkqrJy9__M0Fd3FLLfPUu8KuG1uKxLhiH2Rrc',
#     'openid': 'oYDIhs5EGD9RriDJjtCJpZ8D-bck',
#     'scope': 'snsapi_base'
# }

# params = {
#     "appid": "wx186e63765e9bd457",
#     "secret": "9d6c1fe531fe51312198be32231ed2d2",
#     "code": str(code),
#     "grant_type": "authorization_code"
# }
# response = requests.get(url="https://api.weixin.qq.com/sns/oauth2/access_token", params=params)
# print(response.json())

# userinfo = {
#     'access_token': '56_Q7246NhLI30bsoH73u8RUBinPw1JOm3rZz4ttHyNklma-Mm5XFXh9Ri9Nyenv12uVakqBXe1-goDEujccK5c6PKpEdnecPX9ir7u7d832F0',
#      'expires_in': 7200,
#      'refresh_token': '56_QxYjUJ9SXyQgo4w1wkgBf7XliEqOdBhf61v_BnPLumyL8R9OgPGlh7ObGV6_fTfyZeZj_mAuxxMFnP3pvnR9mx2w23XrBu74KWkNNWF0mv8',
#      'openid': 'oYDIhs5EGD9RriDJjtCJpZ8D-bck',
#      'scope': 'snsapi_userinfo'
#  }


# 第四步：拉取用户信息(需scope为 snsapi_userinfo)
"""
如果网页授权作用域为snsapi_userinfo，则此时开发者可以通过access_token和openid拉取用户信息了。
http：GET（请使用https协议） https://api.weixin.qq.com/sns/userinfo?access_token=ACCESS_TOKEN&openid=OPENID&lang=zh_CN
"""
# openid = "oYDIhs5EGD9RriDJjtCJpZ8D-bck"
# access_token = "56_edXzsfEnDGq_b-9wsUzi7jDjEvt1vAiwLj7f06k8136I53SwuTI_UnkBQndu2ilDT--2fj_5uAlU4AnbNoay556kaBzdjJD90Dj3Ef1lT28"
# url = "https://api.weixin.qq.com/sns/userinfo?access_token={}openid={}&lang=zh_CN".format(access_token, openid)
# res = requests.get(url=url)
# print(res.json())



# 检验授权凭证(access_token)是否有效
"""
http：GET（请使用https协议） https://api.weixin.qq.com/sns/auth?access_token=ACCESS_TOKEN&openid=OPENID
"""
# url = " https://api.weixin.qq.com/sns/auth?access_token=56_6TSPvTwWvwp8sJaVkpC7dNKzY5LcVaBMOvIdo-_pQ8fA6rzFzNbcLC4BmN4JfLk_9AphVNrK75kL9-EEOjYLou6CYis5Dq2VgyDRm5RM0Ng&openid=oYDIhs5EGD9RriDJjtCJpZ8D-bck"
# res = requests.get(url=url)
# print(res.json())


# 获取Access token
"""
https请求方式: GET https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=APPID&secret=APPSECRET
"""

# url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=wx186e63765e9bd457&secret=9d6c1fe531fe51312198be32231ed2d2"
# res = requests.get(url=url)
# print(res.json())
