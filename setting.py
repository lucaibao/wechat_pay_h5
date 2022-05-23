# -*- coding: utf-8 -*-
# @Author: cai bao
# @Time: 2022/5/18
debug = True


class Config(object):
    SQLALCHEMY_COMMENT_ON_TRARDOWN = True
    # 设置是否跟踪数据库的修改情况
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class ProductConfig(Config):
    """生产环境配置"""
    # mysql
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:f8RsJqVkMk6tnK@120.25.250.35:33061/ruihe"
    # mysql慢查询超时时间
    FLASK_SLOW_DB_QUERY_TIME = 0.2

    # redis
    REDIS_URL = "redis://:a6UMuHDm44YAZr@120.25.250.35:6379/12"


class TestConfig(Config):
    """测试环境配置"""
    # mysql
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:kAhkougbUsYeZZDzVcecxB@61.144.250.226:3360/ruihe"
    # 数据库操作时是否显示原始sql语句，后台日志记录用到
    SQLALCHEMY_ECHO = True
    # mysql慢查询超时时间
    FLASK_SLOW_DB_QUERY_TIME = 0.5

    # redis
    REDIS_URL = "redis://:VyWMwW0GYQVpCZP6@61.144.250.226:6379/2"


if debug:
    config = TestConfig()
else:
    config = ProductConfig()
