'''
This module will be responsible for the testing of an XML file. A mock class of scraping will be executed.
Created on 2013-12-17

@author: ivan
'''
import unittest
import xml.etree.ElementTree as ET

from ..NBAScrape import NBAPeriodicScrape

key_prefix = "{http://fantasysports.yahooapis.com/fantasy/v2/base.rng}"

#TODO: Need to fix dependencies; the functionality of this class is too much, and we shouldn't keep it so tightly dependent
class MockRetrieveXml(NBAPeriodicScrape):
    
    def __init__(self):
        self.parseData()
        
    def parseData(self):
        self.players = []
        self.stats = []
        self.nba_teams = []
        self.entityManager = MockEntityManager()
        root = ET.parse("playerXmlTest.xml").getroot()
        player_list_xml = root[0][7]
        self.players = self.getPlayerData(player_list_xml)
        # Send in same template for programming aesthetics
        # eventually, you want to set this to be broad, and then override this with different stats parameters
        self.stats = self.getPlayerStats(player_list_xml)
        
class MockEntityManager(object):
    
    def addObject(self, object):
        pass

class TestNBAScraping(unittest.TestCase):
    def setUp(self):
        #self.mock_xml_retriever = MockRetrieveXml()
        self.retriever = MockRetrieveXml()
        
    def test(self):
        #mock = Mock()
        #mock(self.mock_xml_retriever)
        self.retriever.parseData()
        player = self.retriever.players[0]
        playerstat = self.retriever.stats[0]
        self.assertEqual(player.name, 'Kevin Durant')
        self.assertEqual(str(playerstat), 'Stats object for Player: Kevin Durant')
        
        print playerstat.id, playerstat.player_id
        # Assert playerstat has objects
        
        # TODO: test wrong parsing information - what can go wrong? what values can be null?       
        
        
            
            