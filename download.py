"""
Download and extract all the retrosheet zips including CurrentNames.csv (maybe I should prepackage that, idk)

https://www.retrosheet.org/Nickname.htm
https://www.retrosheet.org/BIOFILE.TXT
https://www.retrosheet.org/game.htm#Regular%20Season%20Games
Maybe also add postseason but have a different part of the DB for postseason or some boolean that you set for postseason games
"""
from io import BytesIO
import os
import zipfile
import tqdm
import requests


def download_games():
    os.makedirs("downloads", exist_ok=True)
    decade_zips = [
        "https://www.retrosheet.org/events/1910seve.zip",
        "https://www.retrosheet.org/events/1920seve.zip",
        "https://www.retrosheet.org/events/1930seve.zip",
        "https://www.retrosheet.org/events/1940seve.zip",
        "https://www.retrosheet.org/events/1950seve.zip",
        "https://www.retrosheet.org/events/1960seve.zip",
        "https://www.retrosheet.org/events/1970seve.zip",
        "https://www.retrosheet.org/events/1980seve.zip",
        "https://www.retrosheet.org/events/1990seve.zip",
        "https://www.retrosheet.org/events/2000seve.zip",
        "https://www.retrosheet.org/events/2010seve.zip",
        "https://www.retrosheet.org/events/2020seve.zip",
        "https://www.retrosheet.org/events/allpost.zip"
    ]
    for url in tqdm.tqdm(decade_zips, desc=" Files downloading"):
        request = requests.get(url)
        zip = zipfile.ZipFile(BytesIO(request.content))
        zip.extractall("downloads")
