"""
Each game from each team, process that lol

This should be called directly from main.py and idk, maybe main.py loops over each game and uses the function to add a game in build_db.py
"""
from process_game import Game


def process_season(file_name: str) -> list[Game]:
    with open("2021CHN.EVN", "r") as f:
        file = [line.rstrip() for line in f.readlines()]
        season_text: list[list[str]] = []
        for line in file:
            if line.startswith('id,'):
                season_text.append([line])
            else:
                season_text[-1].append(line)

        season: list[Game] = []
        for game in season_text:
            season.append(Game(game))

        for game in season:
            game.process_game()

        return season
