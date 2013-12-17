'''
Created on 2013-12-06

@author: ivan
'''
import logging
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey, \
    create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker

# Linux has user/pw of root/<blank> while windows is ivan/watershipdown
engine = create_engine("mysql+mysqldb://root:@localhost", echo=True)
engine.execute("CREATE DATABASE IF NOT EXISTS nba_db2")
engine.execute("USE nba_db2")
Base = declarative_base()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

class FantasyLeague(Base):
    __tablename__ = 'FantasyLeague'
    id = Column(Integer, primary_key = True)
    league_name = Column(String(50), nullable=False)
    
    def __repr__(self):
        return "Fantasy League: "  + self.league_name

class FantasyTeam(Base):
    __tablename__ = 'FantasyTeam'
    team_id = Column(Integer, primary_key = True)
    league_id = Column(Integer, ForeignKey('FantasyLeague.id'))
    league = relationship("FantasyLeague")
    player_id = Column(Integer, ForeignKey('Player.id'))
    player = relationship("Player")

    def __repr__(self):
        return "Fantasy Team: " + str(self.league)

class NBATeam(Base):
    __tablename__ = 'NBATeam'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable = False)
    isPlayoffTeam = Column(Boolean)
    
    def __repr__(self):
        return self.name

class Player(Base):
    __tablename__ = 'Player'
    id = Column(Integer, primary_key = True, nullable = False)
    name = Column(String(100), nullable = False)
    # Do we want YahooId to be referencing Yahoo Tables?
    yahooID = Column(Integer)
    positions = Column(String(15), nullable = False)
    # One to many relationship
    #player_stats = relationship("Stats")
    team_id = Column(Integer, ForeignKey("NBATeam.id"))
    team = relationship("NBATeam")
    
    def __repr__(self):
        return "Player: " + self.name

'''
The bread and butter of this class. I envision this to be a flat-table like structure for data, where all player data for each 
game is pulled. This provides the backbone for analysis in statistical deviations.
Identifiers to distinguish data: Year, length of stat (daily, weekly, season), date of game (if applicable), stat type (total, per game, per 48 mins, per 36 mins), 
'''

class Stats(Base):
    __tablename__ = 'NBA_Stats'
    id = Column(Integer, primary_key = True)
    player_id = Column(Integer, ForeignKey("Player.id"))
    player = relationship("Player")
    # Configuration stats first: identify this stats column
    year = Column(Integer, nullable=False) 
    # Daily stat, weekly stat, or season-long stat
    typeLength = Column(Integer, nullable=False)
    # Not necessarily applicable
    gameDate = Column(Date)
    typeStat = Column(Integer, nullable=False)
    
    gp = Column(Float, nullable=False)
    gs = Column(Float, nullable=False)
    mp = Column(Float, nullable=False)
    
    fgm = Column(Float, nullable = False)
    fga = Column(Float, nullable = False)
    fgp = Column(Float, nullable = False)
    fta = Column(Float, nullable = False)
    ftm = Column(Float, nullable = False)
    ftp = Column(Float, nullable = False) 
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
    
Base.metadata.create_all(engine)

class EntityManager:
    def __init__(self):
        Session = sessionmaker(bind=engine)
        self.cur = Session()
    
    def addObjectList(self, objList):
        self.cur.addall(objList)
        self.cur.commit()
    
    def addObject(self, obj):
        self.cur.add(obj)
        self.cur.commit()