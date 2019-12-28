from sillySQL import sillySQL

import sys
import logging

# 日志系统配置
handler = logging.FileHandler('app.log', encoding='UTF-8')
# 设置日志文件，和字符编码
logging_format = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
handler.setFormatter(logging_format)
# app logger
# app.logger.addHandler(handler)
# database logger
db_logger = logging.getLogger('Database')
db_logger.addHandler(handler)
shandler = logging.StreamHandler(sys.stderr)
shandler.setFormatter(logging_format)
shandler.setLevel(logging.DEBUG)
db_logger.addHandler(shandler)
db_logger.setLevel(logging.DEBUG)
db_logger.info('123')
# database = sillySQL(logger=db_logger)

db = sillySQL(logger=db_logger)
db.bind()

# db.UPDATEprecise('VOCABULARY', 'COUNT', 3500, {"VID": ['0001']})
# db.INSERTvalues('VOCABULARY',('0004','BEST',2000,365,'Primary'))
# db.DELETEprecise('VOCABULARY', {"vid": ['0004']})
# print(db.SELECTfromWHERE('VOCABULARY',{'VID':['0003']}))
# print(db.SELECTfromTwoTableWHERE('USERS', 'PLAN', {'Proficiency': [100, 99]}))

# db.INSERTvalues('feedback', ('1', '2', '2019-01-01', " I' m wrong"))
# print(db.SELECTfromWHERE('feedbac'))

# tabe=db.SELECTfromTwoTableWHERE('USERS','PLAN')

# db.release()
