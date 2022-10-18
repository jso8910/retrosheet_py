"""
Pull everything together
"""
from itertools import groupby
import os
from download import download_games
from build_db import DB
from process_game import Game
import tqdm


def main():
    download_games()
    db = DB()
    db.create_tables()
    db.create_players()
    files = sorted(os.listdir("downloads"))
    filtered_files: list[str] = []
    for file in files:
        if file.endswith(".ROS"):
            continue
        elif not "." in file:
            continue
        filtered_files.append(file)

    for filename in tqdm.tqdm(filtered_files, desc=" Files", position=0):
        if filename.endswith(".ROS"):
            continue
        elif not "." in filename:
            continue
        postseason = filename.endswith(".EVE")
        deduced = ".ED" in filename
        with open(f"downloads/{filename}", "r") as f:
            file = [line.rstrip() for line in f.readlines()]
            i = (list(group)
                 for _, group in groupby(file, lambda x: x.startswith("id,")))
            season = [a + b for a, b in zip(i, i)]
            for g in tqdm.tqdm(season, desc=" Games", position=1, leave=False):
                game = Game(g, fname=filename,
                            deduced=deduced, postseason=postseason)
                game.process_game()
                db.create_game(game)
        # if idx % 5 == 0:
        #     pass
            # db.session_commit()
    # db.add_events_to_players()
    db.close()
    print("We made it to the end")
    # db.commit_players()
    # db.session_commit()


main()
