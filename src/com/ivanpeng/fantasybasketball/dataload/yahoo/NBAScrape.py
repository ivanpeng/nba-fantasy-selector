'''
Created on 2013-12-06

@author: ivan
'''
from YahooOauth import YahooOAuth
from OrmModules import Player, FantasyLeague, FantasyTeam, NBATeam, Stats
import xml.etree.ElementTree as ET

# Base class for scraping data off Yahoo Fantasy Basketball API
class NBAScrapeBase:
    session = YahooOAuth().session
    game_years_map = {"2001":16, "2002": 67, "2003": 95, "2004":112, "2005":131,
                      "2006":165, "2007": 187, "2008": 211, "2009":234, "2010":249,
                      "2011":265, "2012": 304, "2013":322
                      }
    
    def __init__(self):
        # Have checks on session to see if the request was successful.
        if not self.session:
            self.session = YahooOAuth().session
        self.getLeagueKey()
    
    # Receives the XML data from the scraping, and returns the necessary data given the lookup key in the xml file. 
    def parseXml(self, data, key):
        pass
    # Catching the error for parse xml would be root Element having error tag.
    
    def getGameKey(self, year=2013):
        year_str = str(year)
        return self.game_year_map[year_str];
    
    def getLeagueKey(self):
        # Remember to format this.
        league_key_url = "http://fantasysports.yahooapis.com/fantasy/v2/users;use_login=1/games;game_keys={0}/leagues"
        self.league_key_url = self.session.get(league_key_url.format(self.getGameKey()))
        # ATM, no current need for leagues
        pass
    
    
# Defines the class for executing periodic scraping
class NBAPeriodicScrape(NBAScrapeBase):
    
    def __init__(self):
        super.__init__()
        # Scrape all player data for now 
    
    
    def getPlayerData(self):
        # Generate URL first
        player_list_url = "http://fantasysports.yahooapis.com/fantasy/v2/game/nba/players;out=stats;sort=OR"
        # TODO: append to list where we are going to start. Otherwise we're going to be grabbing first 25 forever
        r = self.session.get(player_list_url)
        root = ET.fromstring(r.text)
        player_list = root[0][7]
        for player in player_list:
            # Get player elements here, and create Player object
            p = Player(name = player.find('name'), yahooID = player.find('player_id'), name = player.find('name').find('full'),
                       stats = player.find('stats').find('stat'))
            pass
    