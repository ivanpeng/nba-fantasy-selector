'''
Created on 2013-10-09

@author: Ivan
'''
import csv
from PlayerDao import PlayerDao
import MySQLdb

def getDbConnection():
    db = MySQLdb.connect(host="localhost", user="ivan", passwd="watershipdown", db="nba_db")
    return db

with open("dataload/ESPN_Master.csv") as csvplayers:
    reader2 = csv.reader(csvplayers)
    dao = PlayerDao()
    playerList = dao.getAllPlayersByKey()
    indArr = []
    positionArr = []
    i = 0
    for row in reader2:        
        row[1] = row[1].replace("'", "''")
        # split by | delimiter
        elems = row[1].split("|")
        j = 0
        for elem in elems:
            elems[j] = elem.replace('\xa0', ' ')
            j = j+1
        if (elems[0] in str(playerList)):
            # First add the index to it
            ind = dao.getPlayerKeyByName(elems[0])
            indArr.append(ind)
            positionData = ""
            if (len(elems) > 2):
                temp = elems[-2].split(" ")
                positionData = elems[-1].strip() + "-" + temp[-1].strip()
            else:
                positionData = elems[-1].strip().split(" ")[-1]
            positionArr.append(positionData)

# Now insert into DB
db = getDbConnection()
cur = db.cursor()
db.autocommit(False)
for idx, item in enumerate(positionArr):
    s = "update Player set Position = '" + item + "' where Player_Key = " + str(indArr[idx])
    cur.execute(s)
    print s
db.commit()
db.close()
