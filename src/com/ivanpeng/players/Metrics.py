'''
This metrics class is a base template for scoring players for selection
Created on 2013-10-08

@author: Ivan
'''
from PlayerDao import PlayerDao

class DefaultMetrics:
    def __init__(self, *args, **kwargs):
        # Here, are there any variables that we will need?
        # rank is what metric we rank by
        self.rank = kwargs["rank"]
        self.position = kwargs["position"]
        self.playerDao = PlayerDao()
        self.playerList = self.playerDao.getAllPlayersByKey()
        if (self.rank == ""):
            self.ranking = self.playerList
        else:
            self.rankList()
    
    def rankList(self):
        # This will rank the list based on the position sent in, and by the metric
        self.ranking = self.playerDao.getPlayersOfPosition(self.position)
        self.ranking.sort(key=lambda x: getattr(x.playerStats, self.rank), reverse=True)
        

    def printList(self):
        print self.rank + ": " + str(self.ranking)
    
#=================================================================
"""
# initialization and call
metrics = DefaultMetrics(rank = "", position="")
metrics.printList();

statsPlaceHolder = [attr for attr in dir(metrics.playerDao.getPlayer(key=0).playerStats) if not callable(attr) and not attr.startswith("__") and attr != "type"]
print statsPlaceHolder

positions = ['PG', 'SG', 'SF', 'PF', 'C']

# set up file for writing.
f = open('per_day_rankings_by_stat_and_position.txt', 'w')

for position in positions:
    f.write("The position is " + position + "\n")
    metrics.position = position
    # Should have a printing or better data storage method here
    for statComp in statsPlaceHolder:
        #print "StatLine: " + statComp
        metrics.rank = statComp
        metrics.rankList()
        f.write(metrics.rank + ": " + str(metrics.ranking) + "\n")
    f.write("\n")
f.close()
print f
"""