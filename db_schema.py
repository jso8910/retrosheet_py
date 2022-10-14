from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()


class PlayDB(Base):
    __tablename__ = 'Play'
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey('Event.id'))
    play_text = Column(String())
    runners = Column(String())          # Actually a JSON, just stringified
    # Actually an int, it just gets too big
    batter_play_details = Column(String())
    batter_fielders = Column(String())  # Actually an array/list


class InfoDB(Base):
    __tablename__ = "Info"
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(Integer, ForeignKey('Game.id'))
    date = Column(String())
    home = Column(String())
    away = Column(String())
    night_game = Column(Boolean())
    innings = Column(Integer)
    umps = Column(String())
    game_number = Column(Integer)
    dh = Column(Boolean())
    tiebreaker = Column(Integer)
    pitch_detail = Column(String())
    field_cond = Column(String())
    precip = Column(String())
    sky = Column(String())
    temp = Column(Integer)
    wind_dir = Column(String())
    windspeed = Column(Integer)
    start_time = Column(String())
    game_length = Column(Integer)
    attendance = Column(Integer)
    ballpark = Column(String())
    winning_pitcher = Column(String())
    losing_pitcher = Column(String())
    save = Column(String())


class GameDB(Base):
    __tablename__ = "Game"
    id = Column(Integer, primary_key=True, autoincrement=True)
    # year = Column(Integer)
    game_id = Column(String())
    game = Column(String())     # Actually an array
    info = relationship("InfoDB", uselist=False, backref="game")
    earned_runs = Column(String())  # Actually a dict
    home_lineup = Column(String())  # Actually a dict/array
    away_lineup = Column(String())  # Actually a dict/array
    comments = Column(String())  # Actually a dict/array
    adj = Column(String())   # Actually a dict/array
    plate_appearances = relationship("PA", backref="game")


class PA(Base):
    __tablename__ = "PlateAppearance"
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(Integer, ForeignKey('Game.id'))
    events = relationship("EventDB", backref="pa")


class EventDB(Base):
    __tablename__ = "Event"
    id = Column(Integer, primary_key=True, autoincrement=True)
    pa_id = Column(Integer, ForeignKey('PlateAppearance.id'))
    event_string = Column(String())
    inning = Column(Integer)
    half_is_top = Column(Boolean())
    batter = Column(String())
    count_of_play = Column(String())
    pitches = Column(String())      # Actually an array of ints
    play = relationship("PlayDB", uselist=False, backref="event")
