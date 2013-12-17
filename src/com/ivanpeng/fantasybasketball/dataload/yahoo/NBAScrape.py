'''
Created on 2013-12-06

@author: ivan
'''
from OrmModules import Player, Stats
from OrmModules import EntityManager
from YahooOauth import YahooOAuth
import xml.etree.ElementTree as ET

key_prefix = "{http://fantasysports.yahooapis.com/fantasy/v2/base.rng}"

def getNBAData():
    nbascrape = NBAPeriodicScrape()

# Base class for scraping data off Yahoo Fantasy Basketball API
class NBAScrapeBase(object):
    session = None
    game_years_map = {"2001":16, "2002": 67, "2003": 95, "2004":112, "2005":131,
                      "2006":165, "2007": 187, "2008": 211, "2009":234, "2010":249,
                      "2011":265, "2012": 304, "2013":322
                      }
    statkey_var_map ={"0":"gp",
                      "1":"gs",
                      "2":"mp",
                      "3":"fga",
                      "4":"fgm",
                      "5":"fgp",
                      "6":"fta",
                      "7":"ftm",
                      "8":"ftp",
                      "9":"fga3",
                      "10":"fgm3",
                      "11":"fgp3",
                      "12":"pts",
                      "13":"oreb",
                      "14":"dreb",
                      "15":"reb",
                      "16":"ast",
                      "17":"stl",
                      "18":"blk",
                      "19":"tov",
                      "21":"pf"
                      }
    
    
    def __init__(self):
        # Have checks on session to see if the request was successful.
        if not self.session:
            self.session = YahooOAuth().session
        self.getLeagueKey()
        self.entityManager = EntityManager()
    
    # Receives the XML data from the scraping, and returns the necessary data given the lookup key in the xml file. 
    def parseXml(self, data, key):
        pass
    # Catching the error for parse xml would be root Element having error tag.
    
    def getGameKey(self, year=2013):
        year_str = str(year)
        return self.game_years_map[year_str];
    
    def getLeagueKey(self):
        # Remember to format this.
        league_key_url = "http://fantasysports.yahooapis.com/fantasy/v2/users;use_login=1/games;game_keys={0}/leagues"
        self.league_key_url = self.session.get(league_key_url.format(self.getGameKey()))
    
    
# Defines the class for executing periodic scraping
class NBAPeriodicScrape(NBAScrapeBase):
    
    def __init__(self):
        super(NBAPeriodicScrape,self).__init__()
        # Scrape all player data for now 
        self.parseData()
    
    def parseData(self):
        # Parse the data, and send xml common to both player and stats
        player_list_url = "http://fantasysports.yahooapis.com/fantasy/v2/game/nba/players;out=stats;sort=OR;start={0}"
        # TODO: append to list where we are going to start. Otherwise we're going to be grabbing first 25 forever
        LIMIT = 26
        self.players = []
        self.stats = []
        for i in xrange(0,LIMIT, 25):
            r = self.session.get(player_list_url.format(str(i)))
            root = ET.fromstring(r.text)
            player_list_xml = root[0][7]
            
            self.players.extend(self.getPlayerData(player_list_xml))
            # Send in same template for programming aesthetics
            # eventually, you want to set this to be broad, and then override this with different stats parameters
            self.stats.extend(self.getPlayerStats(player_list_xml))
        print self.players[:75]
        print self.stats[:75]
    
    def getPlayerData(self, playerListXml):        
        # Player data
        playerObjList = []
        # Yahoo ids are prefixed with this; append to every search
        for player in playerListXml:
            # Get player elements here, and create Player object
            playerName = player.find(key_prefix+"name").find(key_prefix+"full").text
            playerYahooID = player.find(key_prefix+"player_id").text
            playerPositions = [x.text for x in player.find(key_prefix+"eligible_positions").findall(key_prefix+"position")]
            # Possibly need to join playerpositions to string
            playerPositionsStr = ",".join(playerPositions)
            
            playerTeam = player.find(key_prefix+"editorial_team_full_name").text
            # Declare object now
            p = Player(name = playerName,
                       yahooID = playerYahooID,
                       positions = playerPositionsStr,
                       team = playerTeam)
            playerObjList.append(p)
        return playerObjList
    
    def getPlayerStats(self,playerListXml):
        statObjList = []
        for playerXml in playerListXml:
            # get player id foreign key relationship
            player = [x for x in self.players if x.name == playerXml.find(key_prefix+"name").find(key_prefix+"full").text]
            # Preliminary identifier information            
            statsXml = playerXml.find(key_prefix+"player_stats")
            season = statsXml.find(key_prefix+"season").text
            coverageType = statsXml.find(key_prefix+"coverage_type").text
            
            statMap = {'player': player[0]}
            statMap['year'] = season
            if coverageType == 'season':
                statMap['typeLength'] = 0 # season
                statMap['typeStat'] = 0 # Totals
            # Need else here
            
            # Now traverse into stat array, and then loop
            statsXml = statsXml.find(key_prefix+"stats").findall(key_prefix+"stat")
            # There is a mapper; each stat is identified by the stat category
            
            for statXml in statsXml:
                # We have a custom mapping on stats; loop through all of them, see if the id exists in our map, and then grab it
                statId = statXml.find(key_prefix+"stat_id").text
                statValue = statXml.find(key_prefix+"value").text
                if (str(statId) in self.statkey_var_map):
                    # Get var name, and put it in dict with statId value
                    varName = self.statkey_var_map[statId]
                    if (statValue is not None and statValue != '-'):
                        statMap[varName] = statValue
                    else:
                        statMap[varName] = "0"
            statObj = Stats(**statMap)
            statObjList.append(statObj)
        # Now we return the stat object
        return statObjList

