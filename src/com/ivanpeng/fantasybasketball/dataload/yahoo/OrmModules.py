'''
Created on 2013-12-06

@author: ivan
'''
import logging
import datetime

from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey, \
    create_engine, types
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker


# Linux has user/pw of root/<blank> while windows is ivan/watershipdown
#engine = create_engine("mysql+mysqldb://root:@localhost", echo=True)
engine = create_engine("mysql+mysqldb://ivan:watershipdown@localhost", echo=True)
#engine.execute("drop database if exists nba_db2")
engine.execute("CREATE DATABASE IF NOT EXISTS nba_db2")
engine.execute("USE nba_db2")
Base = declarative_base()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Season, monthly, or weekly, or daily
LENGTH_CHOICES = (('S', 'SEASON'),
                  ('M', 'MONTHLY'),
                  ('W', 'WEEKLY'),
                  ('D', 'DAILY'))
STAT_CHOICES = (('TOT','TOTAL'),
                ('PG','PERGAME'),
                ('P48','PER48'),
                ('P36','PER36'))

class ChoiceType(types.TypeDecorator):
    impl = types.String(3)

    def __init__(self, choices, **kw):
        self.choices = dict(choices)
        super(ChoiceType, self).__init__(**kw)

    def process_bind_param(self, value, dialect):
        return [k for k, v in self.choices.iteritems() if v == value][0]

    def process_result_value(self, value, dialect):
        return self.choices[value]



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
    player_id = Column(Integer, ForeignKey('Player.yahooID'))
    player = relationship("Player")

    def __repr__(self):
        return "Fantasy Team: " + str(self.league)

class NBATeam(Base):
    __tablename__ = 'NBATeam'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable = False)
    isPlayoffTeam = Column(Boolean, default= False)
    
    def __repr__(self):
        return self.name

class Player(Base):
    __tablename__ = 'Player'
    yahooID = Column(Integer, primary_key = True, nullable=False)
    name = Column(String(100), nullable = False)
    # Do we want YahooId to be referencing Yahoo Tables?
    positions = Column(String(15), nullable = False)
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
    player_id = Column(Integer, ForeignKey("Player.yahooID"))
    player = relationship("Player")
    # Configuration stats first: identify this stats column
    year = Column(Integer, nullable=False) 
    # Daily stat, weekly stat, or season-long stat
    # TODO: For daily and weekly stat lines, we will need to scrawl yahoo data on our own because their data is shit.
    # TODO: We can grab the season data so far with each player, we can see how that changes per day.
    # Other suggestions include figuring out URLs in league context.
    typeLength = Column(ChoiceType(LENGTH_CHOICES), nullable=False)
    # Not necessarily applicable
    gameDate = Column(Date)
    typeStat = Column(ChoiceType(STAT_CHOICES), nullable=False)
    
    gp = Column(Float)
    gs = Column(Float)
    mp = Column(Float)
    
    fgm = Column(Float, nullable = False)
    fga = Column(Float, nullable = False)
    fgp = Column(Float, nullable = False)
    fta = Column(Float, nullable = False)
    ftm = Column(Float, nullable = False)
    ftp = Column(Float, nullable = False) 
    fgm3 = Column(Float, nullable = False)
    fga3 = Column(Float)
    fgp3 = Column(Float)
    oreb = Column(Float)
    dreb = Column(Float)
    reb = Column(Float, nullable = False)
    ast = Column(Float, nullable = False)
    stl = Column(Float, nullable = False)
    blk = Column(Float, nullable = False)
    tov = Column(Float, nullable = False)
    pf = Column(Float)
    pts = Column(Float, nullable = False)
    
    entered_on = Column(DateTime, default=datetime.datetime.now());
    
    # Extra stats here? Efficiency
    
    def __repr__(self):
        return "Stats object for " + str(self.player)
    
Base.metadata.create_all(engine)

class EntityManager:
    def __init__(self):
        Session = sessionmaker(bind=engine)
        self.cur = Session()
    
    def addObjectList(self, objList):
        self.cur.add_all(objList)
        self.cur.commit()
    
    def addObject(self, obj):
        self.cur.add(obj)
        self.cur.commit()
    
    def addObjectIfNotExisting(self, obj):
        self.cur.merge(obj)
        self.cur.commit()
    
    def addObjectListIfNotExisting(self, objList, isObjListUnique = True):
        for obj in objList:
            if isObjListUnique is False:
                self.addObjectIfNotExisting(obj)
                pass
            else:
                self.cur.merge(obj)
        self.cur.commit()
        