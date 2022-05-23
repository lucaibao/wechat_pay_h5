# -*- coding: utf-8 -*-
# @Author: cai bao
# @Email: lucaibao@houselai.com
# @Time: 2022/5/17
from flask import Flask
from flask_cors import CORS
from util.log_ import Logger
from app.hooks import load_hook


def create_app():
    app = Flask(__name__)

    # 配置管理
    app.config.from_object("setting.config")

    # 解决跨域
    CORS(app, resources=r'/*')

    # 创建日志对象
    app.logger = Logger().get_logger("server.log")

    # 创建数据库对象
    from util.mysql_ import db
    db.init_app(app)

    # 创建redis对象
    from util.redis_ import redis_client
    redis_client.init_app(app)

    # 注册蓝图
    from app.view import init_app
    app = init_app(app)

    # 加载请求钩子
    app = load_hook(app)

    return app
