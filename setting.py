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
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://"
    # mysql慢查询超时时间
    FLASK_SLOW_DB_QUERY_TIME = 0.2

    # redis
    REDIS_URL = "redis://:2"


class TestConfig(Config):
    """测试环境配置"""
    # mysql
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql:/"
    # 数据库操作时是否显示原始sql语句，后台日志记录用到
    SQLALCHEMY_ECHO = True
    # mysql慢查询超时时间
    FLASK_SLOW_DB_QUERY_TIME = 0.5

    # redis
    REDIS_URL = "redis://:"


if debug:
    config = TestConfig()
else:
    config = ProductConfig()
