'''
This module is responsible for loading data into tables. This needs to be run only once.
Created on 2013-10-05

@author: Ivan
'''
import csv
import MySQLdb


def getReader(filename):
    with open(filename, 'rb') as csvfile:
        reader = csv.reader(csvfile)
    return reader;
            
def getDbConnection():
    db = MySQLdb.connect(host="localhost", user="ivan", passwd="watershipdown", db="nba_db")
    return db

def loadTable(db, data, tablename):
    # this function assumes that data entered into DB fills every column
    # data is a configuration 
    cur = db.cursor()
    # first set autocommit off
    db.autocommit(False);
    for row in data:
        s = "insert into " + tablename + " values (" + row + ")"
        cur.execute(s)
    db.commit()
    
# ==================================================================================
# Main function
# This file only needs to be run once, but the functions need to be called 3 times.

db = getDbConnection()
#reader1 = getReader("2012-2013_Totals.csv")
filename = "2012-2013_Totals.csv"
with open(filename, 'rb') as csvfile:
    reader1 = csv.reader(csvfile)
    # now process data from reader; need to enter into player table first
    i = 0
    playerArr = []
    statArr = []
    for row in reader1:
        # Player data first; must do some parsing to name; remove everything after parentheses
        playerName = row[1][:row[1].find("(")-1]
        playerName = playerName.replace("'", "''")
        playerData = str(i) + ", '" + playerName  + "'," + str(0)
        playerArr.append(playerData)
        
        statData = str(i) + "," + ",".join(row[2:])
        statData = statData.replace("'", "")
        statData = statData.replace("%", "")
        statArr.append(statData)
        i += 1

#loadTable (db, playerArr, "Player")
#loadTable (db, statArr, "Total_Stats")

"""with open("NBA_League_Averages.csv") as csvaverages:
    reader2 = csv.reader(csvaverages)
    avgArr = []
    for row in reader2:
        row[0] = "'" + row[0] + "'"
        avgData = ",".join(row)
        avgArr.append(avgData);
        
loadTable(db, avgArr, "League_Avg_PerGame")
"""

#loadTable(db, positionArr, "Player")
db.close()