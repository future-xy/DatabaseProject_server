from sillySQL import sillySQL

db = sillySQL()
db.bind()

# db.UPDATEprecise('VOCABULARY','COUNT',3500,"VID='0001'")
# db.INSERTvalues('VOCABULARY',('0004','BEST',2000,365,'Primary'))
# db.DELETEprecise('VOCABULARY',"vid='0004'")
# print(db.SELECTfromWHERE('VOCABULARY',{'VID':'0003'}))
# print(db.SELECTfromTwoTableWHERE('USERS', 'PLAN', {'Proficiency': [100, 99]}))
print(db.SELECTfromWHERE('feedback'))
db.DELETEprecise('feedback',{'fid':['111','112']})
print(db.SELECTfromWHERE('feedback'))
# tabe=db.SELECTfromTwoTableWHERE('USERS','PLAN')

db.release()
