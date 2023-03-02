from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
import ast

from play_enums import Pitch, PlayFlags

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
    state = Column(String())

    def to_correct_types(self):
        d = self.__dict__
        self.runners = ast.literal_eval(d['runners'])
        for key, val in self.runners.items():
            if isinstance(val, int):
                self.runners[key] = PlayFlags(val)
            elif isinstance(val, list):
                for idx, item in enumerate(val):    # type: ignore
                    if isinstance(val, int):
                        self.runners[key][idx] = PlayFlags(item)

        self.batter_play_details = PlayFlags(int(d['batter_play_details']))
        self.batter_fielders = ast.literal_eval(d['batter_fielders'])
        self.state = ast.literal_eval(d['state'])
        for idx, item in enumerate(self.batter_fielders):
            self.batter_fielders[idx] = PlayFlags(item)


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

    def to_correct_types(self):
        return


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
    postseason = Column(Boolean())
    deduced = Column(Boolean())
    fname = Column(String())

    def to_correct_types(self):
        d = self.__dict__
        self.game = ast.literal_eval(d['game'])
        self.earned_runs = ast.literal_eval(d['earned_runs'])
        self.home_lineup = ast.literal_eval(d['home_lineup'])
        self.away_lineup = ast.literal_eval(d['away_lineup'])
        self.comments = ast.literal_eval(d['comments'])
        self.adj = ast.literal_eval(d['adj'])


class PA(Base):
    __tablename__ = "PlateAppearance"
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(Integer, ForeignKey('Game.id'))
    events = relationship("EventDB", backref="pa")

    def to_correct_types(self):
        return


class EventDB(Base):
    __tablename__ = "Event"
    id = Column(Integer, primary_key=True, autoincrement=True)
    pa_id = Column(Integer, ForeignKey('PlateAppearance.id'))
    event_string = Column(String())
    inning = Column(Integer)
    half_is_top = Column(Boolean())
    batter_id = Column(String(), ForeignKey("Player.player_id"))
    count_of_play = Column(String())
    # Actually an array of ints which should be converted into Pitch
    pitches = Column(String())
    play = relationship("PlayDB", uselist=False, backref="event")

    def to_correct_types(self):
        d = self.__dict__
        self.pitches = ast.literal_eval(d['pitches'])
        for idx, pitch in enumerate(self.pitches):
            self.pitches[idx] = Pitch(pitch)

        self.count_of_play = ast.literal_eval(d['count_of_play'])


class Player(Base):
    __tablename__ = "Player"
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(String())
    # events = relationship("EventDB", backref="batter")
    first_name = Column(String())
    last_name = Column(String())
    nickname = Column(String())

    def to_correct_types(self):
        return
