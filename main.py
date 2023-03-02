"""
Pull everything together
"""
from itertools import groupby
import os
import argparse
from download import download_games
from build_db import DB
from process_game import Game
import tqdm


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-download', dest="download",
                        action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--start-year", type=int, default=0, required=False)
    parser.add_argument("--end-year", type=int, default=10000, required=False)
    args = parser.parse_args()
    if args.download:
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
        elif int(file[:4]) not in range(args.start_year, args.end_year + 1):
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
    db.close()
    print("We made it to the end")


main()
