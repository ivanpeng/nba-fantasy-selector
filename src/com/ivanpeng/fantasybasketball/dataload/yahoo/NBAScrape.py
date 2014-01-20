'''
Created on 2013-12-06

@author: ivan
'''
from datetime import date, timedelta
import datetime
import logging

from OrmModules import EntityManager, Player, Stats, NBATeam
from YahooOauth import YahooOAuth
from com.ivanpeng.fantasybasketball.dataload.yahoo.OrmModules import \
    LENGTH_CHOICES, STAT_CHOICES
import xml.etree.ElementTree as ET


key_prefix = "{http://fantasysports.yahooapis.com/fantasy/v2/base.rng}"

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
    special_statkey_map ={
                      "9004003":"fgm/fga",
                      "9007006":"ftm/fta"
                      }
    
    percentages_stats = ["fgp", "ftp", "fgp3"]
    
    def __init__(self, push_to_db = False):
        # Have checks on session to see if the request was successful.
        if not self.session:
            self.session = YahooOAuth().session
        self.getLeagueKey()
        self.entityManager = EntityManager()
        self.getTeams()
        #self.getPlayers()
        self.push_to_db = push_to_db
    
    def getGameKey(self, year=2013):
        year_str = str(year)
        return self.game_years_map[year_str];
    
    def getLeagueKey(self):
        # Remember to format this.
        league_key_url = "http://fantasysports.yahooapis.com/fantasy/v2/users;use_login=1/games;game_keys=322/leagues"
        self.league_key_url = self.session.get(league_key_url.format(self.getGameKey()))
        
    def getTeams(self):
        self.nba_teams = self.entityManager.cur.query(NBATeam).all()
        
    def getPlayers(self):
        self.players = self.entityManager.cur.query(Player).all()
    
    
# Defines the class for executing periodic scraping
class NBAPeriodicScrape(NBAScrapeBase):
    
    LIMIT = 400
    
    def __init__(self, push_to_db = False, **kwargs):
        super(NBAPeriodicScrape,self).__init__()
        # Format URL first
        self.getHistoricalData()
        # Scrape all player data for now 
        self.parseData()
        self.calculateTimeDiff()
        if push_to_db:
            print "Pushing to DB..."
            self.addData()
    
    def formatURL(self, **kwargs):
        # This will format the urls based on incoming data
        # Return will be null, and we will pull the player_list_url with only formatting on the start for counts
        pass
    
    def getHistoricalData(self, time = datetime.datetime.now()):
        # Grab the date, do date subtraction
        d = time.date()-timedelta(days=2)
        # Query
        self.yesterday_stats = self.entityManager.cur.query(Stats).filter_by(gameDate = d).all()
        # Get player set in data in case there are new players added
        self.yesterday_players = self.entityManager.cur.query(Player).filter(Player.yahooID.in_([x.player_id for x in self.yesterday_stats])).all()
        
        logging.info("Historical data. Players from yesterday: " + str(len(self.yesterday_players)))
        
    def calculateTimeDiff(self, doCalculate = True):
        self.difference_list = []
        # This function matches up the player ids, and the dates, and does subtraction if necessary
        for yesterday_player in self.yesterday_players:
            # Find if there is set intersection between today's players and yesterday's players
            if str(yesterday_player.yahooID) in [x.yahooID for x in self.players]:
                # Find stat ids in both lists, and compare dates. If difference is 1, then do difference stat
                yesterday_stat = next(x for x in self.yesterday_stats if x.player_id == yesterday_player.yahooID)
                today_stat = next(x for x in self.stats if x.player_id == str(yesterday_player.yahooID))
                print "Yesterday: " + str(yesterday_stat) + ", Today: " + str(today_stat)
                isDifferent, difference = self.diffStats(yesterday_stat, today_stat)
                if isDifferent:
                    # True! Add difference to a list, for input into data
                    self.difference_list.append(difference);
                
    
    def diffStats(self, yesterday, today):
        # Find the difference betweeen the stats, and then return a tuple checking for if different, and the stat object of difference
        var_values = self.statkey_var_map.values()
        isDifferent = False;
        statMap = {}
        statMap['player_id'] = yesterday.player_id
        statMap['year'] = yesterday.year
        statMap['typeLength'] = 'DAILY'
        statMap['gameDate'] = today.gameDate
        statMap['typeStat'] = 'TOTAL'
        statMap['entered_on'] = datetime.datetime.now()
        
        print "Calculating differing stats for " + str(yesterday)
        if int(today.gp) - int(yesterday.gp) != 0:
            isDifferent = True
        if isDifferent == True:
            for var in var_values:
                if var not in self.percentages_stats:
                    val = float(getattr(today, var)) - float(getattr(yesterday, var))
                elif var == "fgp":
                    if (int(today.fga)- int(yesterday.fga) > 0):
                        val = (float(today.fgm)-float(yesterday.fgm))/(float(today.fga)-float(yesterday.fga))
                    else:
                        val = 0;
                elif var == "ftp":
                    if (int(today.fta)- int(yesterday.fta) > 0):
                        val = (float(today.ftm)-float(yesterday.ftm))/(float(today.fta)-float(yesterday.fta))
                    else:
                        val = 0;
                elif var == "fgp3":
                    if (int(today.fga3)- int(yesterday.fga3) > 0):
                        val = (float(today.fgm3)-float(yesterday.fgm3))/(float(today.fga3)-float(yesterday.fga3))
                    else:
                        val = 0;
                statMap[var] = val
            statObj = Stats(**statMap)
            return isDifferent,statObj
        else:
            return isDifferent, None
    
    def parseData(self):
        # Parse the data, and send xml common to both player and stats
        player_list_url = "http://fantasysports.yahooapis.com/fantasy/v2/game/{0}/players;out=stats;sort=OR;start={1}"
        self.players = []
        self.stats = []
        for i in xrange(0,self.LIMIT, 25):
            r = self.session.get(player_list_url.format(str(self.getGameKey()), str(i)))
            root = ET.fromstring(r.text)
            player_list_xml = root[0][7]
            
            self.players.extend(self.getPlayerData(player_list_xml))
            # Send in same template for programming aesthetics
            # eventually, you want to set this to be broad, and then override this with different stats parameters
            self.stats.extend(self.getPlayerStats(player_list_xml))

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
            
            playerTeamName = player.find(key_prefix+"editorial_team_full_name").text
            # Get or create team name with playerTeamName
            playerTeam = self.get_or_create_team(playerTeamName)
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
            
            statMap = {'player_id': player[0].yahooID}
            
            statMap['year'] = season
            #statMap['gameDate'] = datetime.date()-timedelta(days=1)
            #statMap['gameDate'] = datetime.date.today()
            statMap['entered_on'] = str(datetime.datetime.now())
            if coverageType == 'season':
                statMap['typeLength'] = 'SEASON' # season
                statMap['typeStat'] = 'TOTAL' # Totals
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
    
    def get_or_create_team(self, team_name, is_playoff_team = False):
        # Here, check if team name exists in list, otherwise add to current list
        for team in self.nba_teams:
            if team.name == team_name:
                return team
        
        # Not found in the list; add it to self.nba_teams and then return that object
        new_team = NBATeam(name = team_name, isPlayoffTeam = is_playoff_team)
        self.nba_teams.append(new_team)
        self.entityManager.addObject(new_team)
        return new_team
        
    def addData(self):
        # Add players (if existing), and stats (if existing?)
        self.entityManager.addObjectListIfNotExisting(self.players)
        self.entityManager.addObjectList(self.stats)
        self.entityManager.addObjectList(self.difference_list)


retriever = NBAPeriodicScrape(push_to_db=True)
