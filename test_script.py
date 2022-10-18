# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnusedImport=false
# pyright: reportGeneralTypeIssues=false, reportOptionalSubscript=false
from db_schema import PA, Base, EventDB, GameDB, InfoDB, PlayDB, Player
import sqlalchemy as db
from sqlalchemy import select
from sqlalchemy.orm import Session


engine = db.create_engine(
    f'sqlite:///retrosheet.sqlite')
connection = engine.connect()
session = Session(engine)

with session.no_autoflush:
    res = session.query(GameDB).all()

    obj: GameDB = res[-1]
    print(obj, obj.game_id)
    print(type(obj.game))
    obj.to_correct_types()
    print(type(obj.game))
    obj.plate_appearances[0].events[0].to_correct_types()
    print(obj.plate_appearances[0].events[0].count_of_play)
