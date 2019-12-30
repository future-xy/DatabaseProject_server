#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Name    : home.py
# Time    : 2019/12/11 9:34
# Author  : Fu Yao
# Mail    : fy38607203@163.com

import logging
import sys

from flask import Flask
from flask import request

import numpy as np

from sql.sillySQL import sillySQL
from utils import *
from settings import *

app = Flask(__name__, static_folder="web", static_url_path="")

if DEBUG:
    level = logging.DEBUG
else:
    level = logging.INFO

# 日志系统配置
file_handler = logging.FileHandler('app.log', encoding='UTF-8')
file_handler.setLevel(level)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setLevel(level)
# 设置日志文件，和字符编码
logging_format = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)d - %(message)s')
file_handler.setFormatter(logging_format)
stream_handler.setFormatter(logging_format)
# app logger
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.DEBUG)
# database logger
db_logger = logging.getLogger('Database')
db_logger.addHandler(file_handler)
db_logger.addHandler(stream_handler)
db_logger.setLevel(level)

database = sillySQL(logger=db_logger)


def newID(table, name):
    id = randID()
    while len(database.SELECTfromWHERE(table, {name: [id]})) > 1:
        app.logger.info("ID conflict!")
        id = randID()
    return id


# home page
@app.route('/')
def home():
    return app.send_static_file('index.html')


# Debug
# login page
@app.route('/signup', methods=['POST'])
def signup():
    keys = ['Uname', 'Pnumber', 'Mail', 'PW']
    if request.method == 'POST':
        try:
            form = request.json['data']
            value = [form[key] for key in keys]
        except KeyError as k:
            app.logger.error("KeyError: {}".format(k.args[0]))
            return STD_ERROR
        else:
            app.logger.debug('Post: {}'.format(value))
            for i in range(1, len(value) - 1):
                data = database.SELECTfromWHERE('USERS', {keys[i]: [value[i]]})
                if len(data) > 1:
                    return {'message': i, 'data': ''}
            uid = newID('USERS', 'UID')
            app.logger.debug('New UID: {}'.format(uid))
            # uid,uname,pw,avatar,mail,pnumber,sex,education,garde
            database.INSERTvalues('USERS', (uid, value[0], value[3], None, value[2], value[1], 'U', None, None))
            return {'message': 0, 'data': uid}


# Debug
@app.route('/signin', methods=['POST'])
def signin():
    types = ['UID', 'Pnumber', 'Mail']
    keys = ['Uname', 'Pnumber', 'Mail', 'UID']
    if request.method == 'POST':
        try:
            form = request.json['data']
            app.logger.debug('Post: {}'.format(form))
            tp = form['type']
            info = form['info']
            pw = form['PW']
        except KeyError as k:
            app.logger.error("KeyError: {}".format(k.args[0]))
            return STD_ERROR
        else:
            data = database.SELECTfromWHERE('USERS', {types[tp]: [info]})
            if len(data) != 2:
                return STD_ERROR
            header = data[0]
            data = data[1]
            if data[header.index('pw')] != pw:
                return STD_ERROR
            if DEBUG:
                app.logger.debug('Header: {}'.format(header))
                app.logger.debug('Select data: {}'.format(data))
            index = [header.index(key.lower()) for key in keys]
            return {'message': 0, 'data': {keys[i]: data[index[i]] for i in range(len(keys))}}


# Debug
# front page
@app.route('/user/<UID>/overview', methods=['GET'])
def hello(UID):
    global REVIEW, LEARN
    review, learn = REVIEW, LEARN
    if request.method == 'GET':
        have_learned = database.SELECTfromWHERE('PLAN', {'UID': [UID], 'Proficiency': [1, 2, 3]})
        not_learned = database.SELECTfromWHERE('PLAN', {'UID': [UID], 'Proficiency': [0]})
        if have_learned is False or not_learned is False or len(have_learned) + len(not_learned) == 2:
            app.logger.error("The user({}) didn't choose any vocabulary!".format(UID))
            return STD_ERROR
        review = min(review, len(have_learned) - 1)
        learn = min(learn, len(not_learned) - 1)
        t_record = database.SELECTfromWHERE('RECORD', {'UID': [UID], 'Dates': [today()]})
        # 如果今天还没由背单词
        if len(t_record) == 1:
            y_record = database.SELECTfromWHERE('RECORD', {'UID': [UID], 'Dates': [today(-1)]})
            # 如果昨天没有背单词
            if len(y_record) == 1:
                cont = 0
            else:
                cont = y_record[1][y_record[0].index('aday')]
        else:
            cont = t_record[1][t_record[0].index('aday')]
        if len(not_learned) > 1:
            tid = not_learned[1][not_learned[0].index('tid')]
        else:
            tid = have_learned[1][have_learned[0].index('tid')]
        data = database.SELECTfromTwoTableWHERE('VOCABULARY', 'TAKES', {'TID': [tid]})
        vname = data[1][data[0].index('vname')]
        return {"message": 0, "data": {
            "Vname": vname,
            "alreadyRecite": len(have_learned) - 1,
            "remained": len(not_learned) - 1,
            "today learn": learn,
            "today review": review,
            "continuous": cont,
        }}


# Debug
@app.route('/user/<UID>/info', methods=['GET', 'POST'])
def userInfo(UID):
    keys = ['Uname', 'Avatar', 'Sex', 'Education', 'Grade']
    if request.method == 'POST':
        try:
            form = request.json['data']
            value = [form[key] for key in keys]
        except KeyError as k:
            app.logger.error("KeyError: {}".format(k.args[0]))
            return STD_ERROR
        else:
            for i in range(len(keys)):
                if not database.UPDATEprecise('USERS', keys[i], value[i], {"UID": [UID]}):
                    app.logger.error("Unable to update USER {}, item={}, value={}".format(UID, keys[i], value[i]))
                    return STD_ERROR
            return STD_OK
    elif request.method == 'GET':
        data = database.SELECTfromWHERE('USERS', {'UID': [UID]})
        if len(data) != 2:
            app.logger.error("UID {} does not exist".format(UID))
            return STD_ERROR
        header = data[0]
        data = data[1]
        value = [data[header.index(key.lower())] for key in keys]
        value = [v if v != None else '' for v in value]
        return {"message": 0, "data": {
            keys[i]: value[i] for i in range(len(keys))
        }}


@app.route('/plan', methods=['GET'])
def plan():
    if request.method == 'GET':
        vocab = database.SELECTfromWHERE('VOCABULARY')
        if vocab is False or len(vocab) < 2:
            app.logger.error("Unable to find any vocabulary")
            return STD_ERROR
        return {"message": 0, "data": vocab[1:]}


# Debug
@app.route('/user/<UID>/plan', methods=['POST'])
def updateUserPlan(UID):
    if request.method == 'POST':
        try:
            vname = request.json['data']['Vname']
        except KeyError as k:
            app.logger.error("KeyError: {}".format(k.args[0]))
            return STD_ERROR
        else:
            vocab = database.SELECTfromWHERE('VOCABULARY', {'Vname': [vname]})
            if vocab is False or len(vocab) != 2:
                app.logger.error("Vocabulary {} does not exist".format(vname))
                return STD_ERROR
            vid = vocab[1][vocab[0].index('vid')]
            if not database.DELETEprecise('PLAN', {'UID': [UID]}):
                app.logger.error("Unable to delete User {} from Plan".format(UID))
                return STD_ERROR
            data = database.SELECTfromWHERE('TAKES', {'VID': [vid]})
            if data is False or len(data) < 2:
                app.logger.error("Unable to find any takes of {}".format(vname))
                return STD_ERROR
            header = data[0]
            words = data[1:]
            for word in words:
                tid = word[header.index('tid')]
                wid = word[header.index('wid')]
                if not database.INSERTvalues('PLAN', (UID, tid, wid, 0)):
                    app.logger.error("Unable to insert ({})".format((UID, tid, wid, 0)))
                    if not database.DELETEprecise('PLAN', {'UID': [UID]}):
                        app.logger.error("Unable to delete User {} from Plan".format(UID))
                    return STD_ERROR
            return STD_OK


# test page
@app.route('/plan/<UID>/<seed>', methods=['GET'])
def getTest(UID, seed):
    random.seed(seed)
    global REVIEW, LEARN
    review, learn = REVIEW, LEARN
    if request.method == 'GET':
        have_learned = database.SELECTfromWHERE('PLAN', {'UID': [UID], 'Proficiency': [1, 2, 3]})
        not_learned = database.SELECTfromWHERE('PLAN', {'UID': [UID], 'Proficiency': [0]})
        if have_learned is False or not_learned is False or len(have_learned) + len(not_learned) == 2:
            app.logger.error("The user({}) didn't choose any vocabulary!".format(UID))
            return STD_ERROR
        header = have_learned[0]
        have_learned = have_learned[1:]
        not_learned = not_learned[1:]
        review = min(review, len(have_learned))
        learn = max(learn, len(not_learned))
        review_item = random.sample(have_learned, review)
        learn_item = random.sample(not_learned, learn)
        today_learn = []
        for item in learn_item:
            ops = random.sample(have_learned + not_learned, 3)
            if item in ops:
                ops.append(random.choice(have_learned))
            else:
                ops.append(item)
            options = [op[header.index('wid')] for op in ops]
            random.shuffle(options)
            today_learn.append((item[header.index('tid')],
                                item[header.index('wid')],
                                item[header.index('proficiency')],
                                options
                                ))
        today_review = []
        for item in review_item:
            ops = random.sample(have_learned + not_learned, 3)
            if item in ops:
                ops.append(random.choice(not_learned))
            else:
                ops.append(item)
            options = [op[header.index('wid')] for op in ops]
            random.shuffle(options)
            today_review.append((item[header.index('tid')],
                                 item[header.index('wid')],
                                 item[header.index('proficiency')],
                                 options
                                 ))
        return {"message": 0, "data": {
            "todayLearn": today_learn,
            "todayReview": today_review
        }}


# Debug
@app.route('/plan/<UID>', methods=['GET', 'POST'])
def updatePlan(UID):
    if request.method == 'GET':
        user_plan = database.SELECTfromTwoTableWHERE('PLAN', 'DICTIONARY', {"UID": [UID]})
        if user_plan is False or len(user_plan) == 1:
            app.logger.error("The user({}) didn't choose any vocabulary!".format(UID))
            return STD_ERROR
        header = user_plan[0]
        data = user_plan[1:]
        plan = []
        for item in data:
            plan.append((
                item[header.index('tid')],
                item[header.index('wid')],
                item[header.index('english')],
                item[header.index('chinese')],
                item[header.index('proficiency')]
            ))
        return {"message": 0, "data": plan}
    elif request.method == 'POST':
        try:
            res = request.json['data']['result']
        except KeyError as k:
            app.logger.error("KeyError: {}".format(k.args[0]))
            return STD_ERROR
        else:
            for tid, wid, p in res:
                if not database.UPDATEprecise('PLAN', 'Proficiency', p, {'UID': [UID], 'TID': [tid], 'WID': [wid]}):
                    app.logger.error("Unable to update Plan UID: {} TID: {} WID: {}".format(UID, tid, wid))
                    return STD_ERROR
            return STD_OK


# Debug
@app.route('/word/<WID>', methods=['GET'])
def getWord(WID):
    if request.method == 'GET':
        keys = ['English', 'Chinese', 'Psymbol']
        data = database.SELECTfromWHERE('DICTIONARY', {'WID': [WID]})
        if data is False or len(data) != 2:
            app.logger.error("Word {} not found.".format(WID))
            return STD_ERROR
        header = data[0]
        data = data[1]
        return {"message": 0, "data": {
            key: data[header.index(key.lower())] for key in keys
        }}
    else:
        app.logger.warning("Not supported method: {}".format(request.method))


# Debug
@app.route('/record/<UID>', methods=['POST', 'GET'])
def record(UID):
    if request.method == 'POST':
        try:
            form = request.json['data']
            count = form['count']
            start = form['start']
            end = form['end']
        except KeyError as k:
            app.logger.error("KeyError: {}".format(k.args[0]))
            return STD_ERROR
        else:
            start_day = datetime.datetime.strptime(start, TIME_FORMAT)
            now_day = start_day.replace(minute=0, second=0)
            end_day = datetime.datetime.strptime(end, TIME_FORMAT)
            while now_day <= end_day:
                this_day = now_day.strftime(DAY_FORMAT)
                today_record = database.SELECTfromWHERE('RECORD', {'Dates': [this_day], 'UID': [UID]})
                if today_record is False or len(today_record) < 2:
                    last_record = database.SELECTfromWHERE('RECORD', {
                        'Dates': [(now_day - datetime.timedelta(days=1)).strftime(DAY_FORMAT)],
                        'UID': [UID]})
                    if last_record is False or len(last_record) == 1:
                        aday = 0
                    else:
                        aday = last_record[1][last_record[0].index('aday')] + 1
                    p = [0, 0, 0, 0]
                    ahour = np.zeros(24).astype(np.float)
                    for i in range(len(p)):
                        data = database.SELECTfromWHERE('PLAN', {'UID': [UID], 'Proficiency': [i]})
                        if data is False:
                            app.logger.error("Unable to find Plan for User {}".format(UID))
                            return STD_ERROR
                        p[i] = len(data) - 1
                    database.INSERTvalues('RECORD', (
                        newID('RECORD', 'SID'), UID, this_day, count, 0, p, ahour.tolist(), aday))

                else:
                    ahour = np.array(today_record[1][today_record[0].index('ahour')])
                ahour[now_day.hour] = ahour[now_day.hour] + 60
                database.UPDATEprecise('RECORD', 'Ahour', ahour.tolist(), {'UID': [UID], 'Dates': [this_day]})
                now_day = now_day + datetime.timedelta(hours=1)
            this_day = start_day.strftime(DAY_FORMAT)
            start_record = database.SELECTfromWHERE('RECORD', {'Dates': [this_day], 'UID': [UID]})
            header = start_record[0]
            ahour = start_record[1][header.index('ahour')]
            ahour[start_day.hour] -= start_day.minute
            database.UPDATEprecise('RECORD', 'Ahour', ahour, {'UID': [UID], 'Dates': [this_day]})
            this_day = end_day.strftime(DAY_FORMAT)
            end_record = database.SELECTfromWHERE('RECORD', {'Dates': [this_day], 'UID': [UID]})
            ahour = end_record[1][header.index('ahour')]
            ahour[end_day.hour] -= (60 - end_day.minute)
            database.UPDATEprecise('RECORD', 'Ahour', ahour, {'UID': [UID], 'Dates': [this_day]})
            return STD_OK
    elif request.method == 'GET':
        data = database.SELECTfromWHERE('RECORD', {'UID': [UID]})
        if data is False or len(data) < 2:
            app.logger.error("Unable to find any record of User {}".format(UID))
            return STD_ERROR
        header = data[0]
        data = data[1:]
        data.sort(key=lambda x: sort_by_time(x, header.index('dates'), DAY_FORMAT))
        records = {sort_by_time(item, header.index('dates'), DAY_FORMAT): item for item in data}
        days = 0
        last_day = datetime.datetime.strptime(today(-6), DAY_FORMAT).timestamp()
        for d in records:
            if d <= last_day:
                days = d
        app.logger.debug(data)
        for line in data:
            print(line)
        info = []
        ahour = np.zeros(24)
        if days == 0:
            info.append((0, 0, 0, 0))
        elif days == last_day:
            info.append(records[days][header.index('proficiency')][1:] +
                        [float(sum(records[days][header.index('ahour')]))])
            ahour += np.array(records[days][header.index('ahour')]).astype(np.float)
        else:
            info.append(records[days][header.index('proficiency')][1:] + [0])
        for i in range(-5, 1):
            days = datetime.datetime.strptime(today(i), DAY_FORMAT).timestamp()
            if days in records:
                info.append(records[days][header.index('proficiency')][1:] +
                            [float(sum(records[days][header.index('ahour')]))])
                ahour += np.array(records[days][header.index('ahour')]).astype(np.float)
            else:
                t = info[-1].copy()
                t[3] = 0
                info.append(t)
        ahour /= 7
        return {'message': 0, 'data': {
            'info': info,
            'Ahour': ahour.tolist()
        }}


# Debug
@app.route('/feedback', methods=['POST'])
def feedback():
    if request.method == 'POST':
        try:
            form = request.json['data']
            uid = form['UID']
            info = form['Info']
        except KeyError as k:
            app.logger.error("KeyError: {}".format(k.args[0]))
            return STD_ERROR
        else:
            fid = newID('FEEDBACK', 'FID')
            app.logger.debug('New FID: {}'.format(fid))
            app.logger.debug('Feedback: {} from {}'.format(info, uid))
            database.INSERTvalues('FEEDBACK', (fid, uid, timestamp(), info))
        return STD_OK


# @app.route('/post/<int:post_id>')
# def show_post(post_id):
#     return 'Post {}'.format(post_id)
#
#
# @app.route('/path/<path:subpath>')
# def show_subpath(subpath):
#     return 'Subpath {}'.format(subpath)
#
#
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         return "USERNAME:" + request.form['username'] + "    " + "PASSWORD:" + request.form['password']
#     else:
#         print(request.args.get('name'))
#         return str(dir(request))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9102, debug=True)
