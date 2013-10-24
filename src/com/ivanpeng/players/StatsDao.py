'''
Data Access object for NBA Stats
Created on 2013-10-08

@author: Ivan
'''
from springpython.database.core import *
from springpython.database.factory import *
from NBAStats import NBAStats

connectionFactory = MySQLConnectionFactory(username="ivan", password="watershipdown", hostname="localhost", db="nba_db")
dt = DatabaseTemplate(connectionFactory)

class StatsDao:
    def getPlayerStat(self, *args, **kwargs):
        # 2 ways of doing this; can either get by player name or key
        if (kwargs["key"] is not None):
            s = "select FGM, FGA, FGP, 3FGM, 3FGA, 3FGP, FTM, FTA, FTP, OREB, DREB, REB, AST, STL, BLK, TOV, PF, PTS from total_stats where PLayer_Key = " + str(int(kwargs["key"]))
            statObj = dt.query(s,None, rowhandler=StatsMapper())
            return self.convertToPerDay(statObj[0], kwargs["key"])
        else:
            s = "select FGM, FGA, FGP, 3FGM, 3FGA, 3FGP, FTM, FTA, FTP, OREB, DREB, REB, AST, STL, BLK, TOV, PF, PTS from total_stats where Player_Key in (select Player_key from Player where Player_Name = " + str(kwargs["name"]) + ")"
            statObj = dt.query(s,None, StatsMapper())
        return statObj[0]
    
    def getNbaAverageStat(self, *args, **kwargs):
        # This will be called via the selector algorithm
        s = "select FGM, FGA, FGP, 3FGM, 3FGA, 3FGP, FTM, FTA, FTP, ORB, DREB, TRB, AST, STL, BLK, TOV, PF, PTS from league_avg_pergame where YR = %s"
        if (kwargs["year"] != ""):
            statObj = dt.query(s, (kwargs["year"],), StatsMapper())
        else:
            # get the most recent year.
            statObj = dt.query(s, ("2012-13",), StatsMapper())
        return statObj[0]
    
    def convertToPerDay(self, statObj, key):
        # Need key to get the number of games
        s = "select GP from total_stats where Player_Key = " + str(key)
        numGames = int(dt.query_for_object(s, None, types.LongType))
        # Make an empty NBAStats object first
        perGameStat = NBAStats([], type="PerGame")
        attr = [attr for attr in dir(statObj) if not callable(attr) and not attr.startswith("__") and attr != "type"]
        # loop through the list and append to row the divided number of games
        for a in attr:
            if (a != 'fgp' and a != 'ftp' and a != 'fgp3'):
                tempvar = getattr(statObj, a)
                setattr(perGameStat, a, float(tempvar/numGames))
            else:
                setattr(perGameStat, a, getattr(statObj, a))
        return perGameStat
    
class StatsMapper(RowMapper):
    def map_row(self, row, metadata=None, type=""):
        statObj = NBAStats(*row, type=type)
        return statObj