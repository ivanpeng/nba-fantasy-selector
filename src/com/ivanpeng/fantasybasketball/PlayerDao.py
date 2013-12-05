'''
Data Access Object for populating player class. Encapsulating database access here.
Created on 2013-10-08

@author: Ivan
'''
from springpython.database.core import *
from springpython.database.factory import *
from PlayerClass import Player

connectionFactory = MySQLConnectionFactory(username="ivan", password="watershipdown", hostname="localhost", db="nba_db")
dt = DatabaseTemplate(connectionFactory)

class PlayerDao:
    
    def __init__(self):
        self.playerList = []
        self.keyList = []
    
    def getPlayer(self, *args, **kwargs):
        # going to pull from kwargs, either name or key
        if (kwargs["key"] is not None):
            player = dt.query("select Player_Key,Player_Name, Team_Name, Selected_Flag2, Position from Player where Player_Key = " + str(kwargs["key"]),None, rowhandler=PlayerMapper())
        else:
            player = dt.query("select Player_Key,Player_Name, Team_Name, Selected_Flag2, Position from Player where Player_Name = "+ str(kwargs["name"]),None , PlayerMapper())
        return player[0]
            
    def getAllPlayersByKey(self):
        # return a list of players
        #keyList = dt.query(, PlayerMapper())
        self.keyList = dt.query_for_list("select Player_Key from Player")
        
        for playerKey in self.keyList:
            player = self.getPlayer(self, key=int(playerKey[0]))
            self.playerList.append(player)
        return self.playerList
    
    def getPlayersOfPosition(self, position):
        # This method returns a list of players which fit the category
        s = "select Player_Key from Player where Position like '%" + position + "%' "
        players = []
        positionList = dt.query_for_list(s)
        for playerKey in positionList:
            player = self.getPlayer(self, key=int(playerKey[0]))
            players.append(player)
        return players
    
    def getPlayerByName(self, name):
        for idx, item in enumerate(self.playerList):
            if (name == str(item)):
                return self.playerList[idx]
        return Player()
    
    def getPlayerKeyByName(self, name):
        for idx, item in enumerate(self.playerList):
            if(name == str(item)):
                return idx
        return -1 # if not found
    
    def getAllAvailablePlayers(self, fTeamKey = 0):
        s = "select Player_Key,Player_Name, Team_Name, Selected_Flag2, Position from Player where Selected_Flag2 = " + str(fTeamKey)
        availablePlayers = dt.query(s, None, rowhandler=PlayerMapper())
        return availablePlayers
    
    def getFantasyTeam(self, fTeamKey=1):
        s = "select Player_Key,Player_Name, Team_Name, Selected_Flag2, Position from Player where Selected_Flag2 = " + str(fTeamKey)
        fTeamPlayers = dt.query(s, None, rowhandler=PlayerMapper())
        return fTeamPlayers

class PlayerMapper(RowMapper):
    def map_row(self, row, metadata = None):
        player = Player(key=row[0], name = row[1], team = row[2], fTeam = row[3], positions = row[4])
        return player
    