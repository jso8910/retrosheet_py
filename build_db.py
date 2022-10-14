"""
Create a class which creates a database, initializes it with stuff like a lookup table for team names and ids (so FLO gets an id of something like 27 or whatever and MIA also gets 27 or whatever)
Should also have a function where you pass a dictionary or something of a game (whatever format i decide to make it in) and it puts it into the DB with all relevant info
Maybe also create player stats or something based on this game data, but that might be a bit complex

Probably use a file to create all the schemas
Use mysql probably
Also put all player ids along with their names here, https://www.retrosheet.org/BIOFILE.TXT

Also init any enums I use
"""
# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false
from itertools import groupby
from db_schema import PA, Base, EventDB, GameDB, InfoDB, PlayDB
import sqlalchemy as db
from sqlalchemy.orm import Session
import os
from process_game import Game

engine = db.create_engine(
    f'sqlite:///retrosheet.sqlite')
connection = engine.connect()
session = Session(engine)
metadata = db.MetaData()


def create_tables():
    if os.path.exists("retrosheet.sqlite"):
        os.utime("retrosheet.sqlite", None)
    else:
        open("retrosheet.sqlite", 'a').close()

    Base.metadata.create_all(engine)


def create_game(game: Game):
    info = game.info
    info_obj = InfoDB(date=info.date, home=info.home, away=info.away, night_game=info.night_game,
                      innings=info.innings, umps=str(info.umps), game_number=info.game_number,
                      dh=info.dh, tiebreaker=info.tiebreaker, pitch_detail=info.pitch_detail,
                      field_cond=info.field_cond, precip=info.precip, sky=info.sky, temp=info.temp,
                      wind_dir=info.wind_dir, windspeed=info.windspeed, start_time=info.start_time,
                      game_length=info.game_length, attendance=info.attendance, ballpark=info.ballpark,
                      winning_pitcher=info.winning_pitcher, losing_pitcher=info.losing_pitcher)
    game_obj = GameDB(game_id=game.id, info=info_obj, game=str(game.game), earned_runs=str(game.earned_runs),
                      home_lineup=str(game.home_lineup), away_lineup=str(game.away_lineup),
                      comments=str(game.comments), adj=str(game.adj))

    for pa in game.plate_appearances:
        pa_obj = PA()
        for event in pa:
            play = event.play
            play_obj = None
            if play:
                play_runners_ints = {}
                for runner_key, runner_val in play.runners.items():
                    play_runners_ints[runner_key] = runner_val
                    for key, val in play_runners_ints[runner_key].items():
                        if issubclass(type(val), int):
                            play_runners_ints[runner_key][key] = int(val)
                        elif issubclass(type(val), list):
                            for i, v in enumerate(val):
                                val[i] = int(v)
                            play_runners_ints[runner_key][key] = val
                        else:
                            play_runners_ints[runner_key][key] = val
                play_obj = PlayDB(play_text=play.play_text, runners=str(play_runners_ints),
                                  batter_play_details=str(
                                      int(play.batter_play_details)),
                                  batter_fielders=str(
                                      [int(fielder) for fielder in play.batter_fielders]))
            event_obj = EventDB(event_string=event.event_string, inning=event.inning, half_is_top=event.half_is_top,
                                batter=event.batter, count_of_play=str(event.count_of_play), pitches=str([int(pitch) for pitch in event.pitches]), play=play_obj)
            pa_obj.events.append(event_obj)
            session.add(event_obj)
            session.add(play_obj)
        game_obj.plate_appearances.append(pa_obj)
        session.add(pa_obj)
    session.add(info_obj)
    session.add(game_obj)
    session.commit()


with open("2021CHN.EVN", "r") as f:
    # Use this code in process_season.py
    file = [line.rstrip() for line in f.readlines()]
    i = (list(group)
         for _, group in groupby(file, lambda x: x.startswith("id,")))
    season = [a + b for a, b in zip(i, i)]
    game = Game(season[0])
    game.process_game()
    create_tables()
    create_game(game)
    # print([g for g in game.plate_appearances[:5]])
    # __import__('pprint').pprint([[vars(g) for g in p] for p in game.plate_appearances[:5]])
    # __import__('pprint').pprint(game.comments)
    # __import__('pprint').pprint(vars(game.plate_appearances[20][0]))
    # __import__('pprint').pprint(game.home_lineup)
    # __import__('pprint').pprint(game.away_lineup)
    # __import__('pprint').pprint(vars(game.info))
