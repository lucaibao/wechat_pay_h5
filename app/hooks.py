# -*- coding: utf-8 -*-
# @Author: cai bao
# @Email: lucaibao@houselai.com
# @Time: 2022/5/17
# @Desc: Flask钩子函数
from common.json_data import return_pack
from common.status_code import Code
from flask_sqlalchemy import get_debug_queries
from flask import current_app


def load_hook(app):
    @app.errorhandler(Exception)
    def handler_not_found(e):
        """
        异常处理；发生一些异常时，如404/500等，或抛出异常之类的就会自动调用
        """
        app.logger.warning(f"系统处理异常: {e.__str__()}")
        return return_pack(code=Code.HSL_SERVER_ERROR, msg=e.__str__())

    @app.after_request
    def slow_db_query(response):
        """
        将运行缓慢的sql写入日志
        """
        for query in get_debug_queries():
            if query.duration >= current_app.config['FLASK_SLOW_DB_QUERY_TIME']:
                current_app.logger.warning(f"slow query:{query.statement}, params:{query.parameters}, "
                                           f"duration:{query.duration}, context:{query.context}")
        return response

    return app
