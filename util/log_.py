# -*- coding: utf-8 -*-
# @Author: cai bao
# @Email: lucaibao@houselai.com
# @Time: 2022/5/17
# @Desc: 日志对象
import os
import logging
from logging.handlers import TimedRotatingFileHandler


class Logger(object):
    _instance = None
    _logger = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self):
        self.log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "logs")
        if not os.path.isdir(self.log_dir):
            os.mkdir(self.log_dir)

    def create_logger(self, file):
        if Logger._logger is None:
            log_file = os.path.join(self.log_dir, file)
            formatter = logging.Formatter('%(asctime)s %(pathname)s [line: %(lineno)d] %(levelname)s %(message)s')
            Logger._logger = logging.getLogger('server-log')
            Logger._logger.setLevel(logging.INFO)
            filehandle = TimedRotatingFileHandler(log_file, when='D')
            filehandle.setLevel(logging.INFO)
            filehandle.setFormatter(formatter)

            Logger._logger.addHandler(filehandle)
        return Logger._logger

    def get_logger(self, file):
        self.create_logger(file)
        return Logger._logger
