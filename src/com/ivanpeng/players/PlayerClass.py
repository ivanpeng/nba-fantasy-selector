'''
This is a player class to contain all information loaded from DB.

Created on 2013-10-07

@author: Ivan
'''
from StatsDao import *

class Player:
    def __init__(self, *args, **kwargs):
        
        self.key = kwargs.get("key", None)
        self.name = kwargs.get("name", "NULL")
        self.team = kwargs.get("team", "NULL")
        self.fTeam = kwargs.get("fTeam", -1)
        self.position = kwargs.get("positions", "")
        # How to implement stats object? With DAO object!
        self.playerStats = self.get_stats()
        
    def get_stats(self):
        if (self.key is not None):
            # call DAO to grab 
            return StatsDao().getPlayerStat(self, key=self.key)
    

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name
            