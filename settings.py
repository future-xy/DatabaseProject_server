#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Name    : settings.py
# Time    : 2019/12/27 16:40
# Author  : Fu Yao
# Mail    : fy38607203@163.com

import string

DEBUG = True
ID_LEN = 10
ID_SPACE = string.ascii_letters + string.digits

STD_ERROR = {"message": 1, "data": ""}
STD_OK = {"message": 0, "data": ""}

LEARN = 100
REVIEW = 150
