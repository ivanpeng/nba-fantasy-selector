'''
This class will be responsible for doing the selection for the basketball players.
The Metrics will return a ranking for each stat, and this will do the maximum selection.
Created on 2013-10-08

@author: Ivan
'''
from types import *
from Metrics import DefaultMetrics;
from StatsDao import StatsDao;
from PlayerDao import PlayerDao;

f = open('PercentagesRanking2.txt', 'w')

def mean(l):
    return float(sum(l))/len(l) if len(l) > 0 else float('nan')

"""
This class will be responsible for doing the optimal selection
"""
class DefaultSelector:
    def __init__(self, *args, **kwargs):
        # for initialization, we should load player data and metric system
        self.defaultMetrics = DefaultMetrics(rank = "", position="")
        self.statCategories = kwargs["statCategories"]
        #self.statCategories = [attr for attr in dir(self.defaultMetrics.playerDao.getPlayer(key=0).playerStats) if not callable(attr) and not attr.startswith("__") and attr != "type"]
        print "Stat Categories: " + str(self.statCategories)
        self.positions = ['PG', 'SG', 'SF', 'PF', 'C']
        self.statsDao = StatsDao()
        self.playerDao = PlayerDao()
        self.leagueAverage = self.statsDao.getNbaAverageStat(year = ""); # a StatObj
        #print self.leagueAverage
    
    '''This is the master selection algorithm. '''
    def selectMaster(self, roundNum, fTeamKey=1):
        if (int(roundNum) > 3):
            print "Selecting the Balanced Team"
            rankings = self.selectBalanced(fTeamKey)
        else:
            print "Selecting the Best Player"
            rankings = self.selectBest()
        print rankings[0:49]
    
    '''This is the function that will get overridden for different selection methods'''
    def selectBest(self):
        # This function will select the best player available based on two metrics: best percentage increase, and balance of stats
        playersAvailableList = self.playerDao.getAllAvailablePlayers()
        greatestIncreaseList = {}
        for player in playersAvailableList:
            #f.write(str(player) + ":\n")
            #print str(player) + ":"
            avg = self.calculatePercentage(player)
            #f.write("Overall Average: " + str(avg)  + "\n")
            #print "Overall Average: " + str(avg)  + "\n\n"
            greatestIncreaseList[str(player)] = avg
        return sorted(greatestIncreaseList, key=greatestIncreaseList.get, reverse=True)
        
    def selectBalanced(self,fTeamKey):
        playersAvailableList = self.playerDao.getAllAvailablePlayers()
        balancedStatList = {}
        # Calculate a weighted average of the important stats required
        fTeamStatLine = self.assessTeam(fTeamKey)
        balancedStatList.update(zip(self.statCategories, fTeamStatLine))
        sortedDict = sorted(balancedStatList, key=balancedStatList.get, reverse=True)
        # Now weight the stat category with the index + 1
        weight = dict(zip(sortedDict, [x for x in range(len(self.statCategories))]))
        balancedList = {}
        for player in playersAvailableList:
            avg = self.calculatePercentage(player, weight)
            balancedList[str(player)] = avg
        return sorted(balancedList, key=balancedList.get,reverse=True)
            
        
    def calculatePercentage(self, player, weight = None):
        # Weight sent in will be a dictionary of stat categories vs index weight
        if (weight is None):
            weight = dict(zip(self.statCategories, [1]*len(self.statCategories)))
        playerVsAverageList = []
        for stat in self.statCategories:
            num = (getattr(player.playerStats, stat)*weight[stat]-getattr(self.leagueAverage, stat))/getattr(self.leagueAverage, stat)
            if (stat == "tov"):
                num = num*-1
            playerVsAverageList.append(num)
            #f.write(stat + ": " + str(num) + "\n")
            #print stat + ": " + str(num)
        # Now calculate overall percentage which we will return
        overallAverage = mean(playerVsAverageList)
        return overallAverage
    
    def calculateStatLinePercentages(self, player):
        playerVsAverageList = []
        for stat in self.statCategories:
            num = (getattr(player.playerStats, stat)-getattr(self.leagueAverage, stat))/getattr(self.leagueAverage, stat)
            if (stat == "tov"):
                num = num*-1
            playerVsAverageList.append(num)
        return playerVsAverageList
    
    '''This function will select the next best player at position'''
    def selectBestForPosition(self, position, fTeamKey = 0):
        ids_l1 = set(x.name for x in self.playerDao.getAllAvailablePlayers(fTeamKey))
        l2 = self.playerDao.getPlayersOfPosition(position)
        playersAvailableList = [item for item in l2 if item.name in ids_l1]
        return playersAvailableList
    
    '''This function will take the fantasy team and assess the team based on the stat categories'''
    def assessTeam(self, fTeamKey=1):
        fTeamPlayers = self.playerDao.getFantasyTeam(fTeamKey)
        fTeamStatLine = [(0.0,0.0),(0.0,0.0)] + [0] *(len(self.statCategories)-2) 
        for fTeamPlayer in fTeamPlayers:
            for idx,item in enumerate(self.getStatLine(fTeamPlayer)):
                if (self.statCategories[idx] == 'fgp' or self.statCategories[idx] == 'ftp' or self.statCategories[idx] == 'fgp3'):
                    fTeamStatLine[idx] = (fTeamStatLine[idx][0] + item[0], fTeamStatLine[idx][1] + item[1])
                else:
                    fTeamStatLine[idx] = fTeamStatLine[idx] + item 
            #fTeamStatLine = [x + y for x,y in zip(fTeamStatLine, self.getStatLine(fTeamPlayer)) if isinstance(x, int)]
        # calculate how much above or below average it is against the nba standard
        percentageDifference = self.calculateTeamPercentage(fTeamStatLine, len(fTeamPlayers))
        return percentageDifference
        
    def getStatLine(self, player):
        statLine = [0] * len(self.statCategories)
        for idx,stat in enumerate(self.statCategories):
            if (stat == 'fgp'):
                statLine[idx] = (player.playerStats.fgm, player.playerStats.fga)
            elif (stat == 'ftp'):
                statLine[idx] = (player.playerStats.ftm, player.playerStats.fta)
            elif (stat == 'fgp3'):
                statLine[idx] = (player.playerStats.fg3, player.playerStats.fga3)
            else:
                statLine[idx] = getattr(player.playerStats, stat)
        return statLine

    def calculateTeamPercentage(self, teamStatLine, length):
        teamPercentage = [0] *len(self.statCategories)
        for idx,stat in enumerate(self.statCategories):
            if (stat == 'fgp' or stat == 'ftp' or stat == 'fgp3'):
                if (teamStatLine[idx][1] != 0):
                    perc = teamStatLine[idx][0]/teamStatLine[idx][1]*100
                    num = (perc-getattr(self.leagueAverage,stat))/getattr(self.leagueAverage,stat)
            else:
                num = (teamStatLine[idx]-getattr(self.leagueAverage, stat))/getattr(self.leagueAverage, stat)*length
            if (stat == 'tov'):
                num = num * -1
            teamPercentage[idx] = num
        print "Team Percentage: " + str(teamPercentage)
        return teamPercentage
    
#==================================================================

#statCategories = ["fgp", "ftp", "fgm3", "pts", "trb", "ast", "stl", "blk", "tov"]
#selector = DefaultSelector(statCategories = statCategories)
#bestList = selector.selectBest()
#print bestList[0:49]
#fTeamKey = 1;
#balancedList = selector.selectBalanced(1)
#print balancedList[0:49]

