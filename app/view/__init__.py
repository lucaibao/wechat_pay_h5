# -*- coding: utf-8 -*-
# @Author: cai bao
# @Email: lucaibao@houselai.com
# @Time: 2022/5/17


def init_app(app):
    # 注册蓝图
    from .pay_view import pay_api
    app.register_blueprint(pay_api, url_prefix="/app/pay")

    from .domain_verify import verify_api
    app.register_blueprint(verify_api, url_prefix="")

    from .user_view import user_api
    app.register_blueprint(user_api, url_prefix="/app/user")

    return app
