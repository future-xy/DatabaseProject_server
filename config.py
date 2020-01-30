#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Name    : config.py
# Time    : 2019/12/27 16:40
# Author  : Fu Yao
# Mail    : fy38607203@163.com

import string
import os
from pathlib import Path

from app.util.mail import Mail

WEB_PATH = 'html'
LOG_PATH = './logs/'

DEBUG = True
ID_LEN = 10
ID_SPACE = string.ascii_letters + string.digits

LEARN = 10
REVIEW = 15

DAY_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%Y-%m-%d-%H-%M-%S"


class Config:
    # APP
    APP_NAME = os.getenv('APP_NAME')

    # Basic path
    BASE_DIR = Path(os.path.abspath('.'))
    # WEB_ROOT = BASE_DIR / ''

    # Database settings
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # SECRET KEY
    SECRET_KEY = b'1234567890'

    # Mail settings
    MAIL_ADDRESS = os.getenv('MAIL_ADDRESS')
    MAIL_PWD = os.getenv('MAIL_PWD')
    MAIL_SERVER = os.getenv('MAIL_SERVER')

    MAIL = Mail(MAIL_SERVER, MAIL_ADDRESS, MAIL_PWD, APP_NAME)


class DevelopmentConfig(Config):
    def __init__(self):
        super().__init__()

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:sysu_sdcs_db2019@111.231.250.160:5432/database0'


class ProductionConfig(Config):
    def __init__(self):
        super().__init__()

    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:sysu_sdcs_db2019@111.231.250.160:5432/database0'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
