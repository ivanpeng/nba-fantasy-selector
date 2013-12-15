'''
Created on 2013-12-06

@author: ivan
'''
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Float, Boolean, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

import logging

# Does engine create a new DB?
engine = create_engine("mysql+mysqldb://ivan:watershipdown@localhost/nba_db2", echo=True)
Base = declarative_base()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

class FantasyLeague(Base):
    __tablename__ = 'FantasyLeague'
    id = Column(Integer, primary_key = True)
    league_name = Column(String, nullable=False)
    
    def __repr__(self):
        return "Fantasy League: "  + self.league_name

class FantasyTeam(Base):
    __tablename__ = 'FantasyTeam'
    team_id = Column(Integer, primary_key = True)
    league_id = Column(Integer, foreign_key = 'FantasyLeague.id')
    league = relationship("FantasyLeague")
    player_id = Column(Integer, foreign_key = 'Player.id')
    player = relationship("Player")

    def __repr__(self):
        return "Fantasy Team: " + str(self.league)

class NBATeam(Base):
    __tablename__ = 'NBATeam'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable = False)
    isPlayoffTeam = Column(Boolean)
    
    def __repr__(self):
        return self.team

class Player(Base):
    __tablename__ = 'Player'
    id = Column(Integer, primary_key = True, nullable = False)
    name = Column(String, nullable = False)
    # Do we want YahooId to be referencing Yahoo Tables?
    yahooID = Column(Integer)
    positions = Column(String, nullable = False)
    # One to many relationship
    player_stats = relationship("Stats")
    team_id = Column(Integer, foreign_key = "NBATeam.id")
    team = relationship("NBATeam")
    
    def __repr__(self):
        return self.name

'''
The bread and butter of this class. I envision this to be a flat-table like structure for data, where all player data for each 
game is pulled. This provides the backbone for analysis in statistical deviations.
Identifiers to distinguish data: Year, length of stat (daily, weekly, season), date of game (if applicable), stat type (total, per game, per 48 mins, per 36 mins), 
'''
class Stats(Base):
    __tablename__ = 'NBA_Stats'
    id = Column(Integer, foreign_key="Player.id")
    player = relationship("Player")
    
    # Configuration stats first: identify this stats column
    year = Column(Integer, nullable=False) 
    # Daily stat, weekly stat, or season-long stat
    typeLength = Column(Integer, nullable=False)
    # Not necessarily applicable
    gameDate = Column(Date)
    typeStat = Column(Integer, nullable=False)
    
    
    fgm = Column(Float, nullable = False)
    fga = Column(Float, nullable = False)
    fgp = Column(Float, nullable = False)    
    fgm3 = Column(Float, nullable = False)
    fga3 = Column(Float, nullable = False)
    fgp3 = Column(Float, nullable = False)
    oreb = Column(Float, nullable = False)
    dreb = Column(Float, nullable = False)
    reb = Column(Float, nullable = False)
    ast = Column(Float, nullable = False)
    stl = Column(Float, nullable = False)
    blk = Column(Float, nullable = False)
    tov = Column(Float, nullable = False)
    pf = Column(Float, nullable = False)
    pts = Column(Float, nullable = False)
    
    # Extra stats here? Efficiency
    
    def __repr__(self):
        return "Stats object for " + str(self.player)