import csv
import requests


def proc_players():
    data = {}
    res = requests.get("https://www.retrosheet.org/BIOFILE.TXT")
    # TODO: make sure this folder is always created before this function is run
    with open("downloads/BIOFILE.txt", "w") as out:
        out.write(res.text)

    with open("downloads/BIOFILE.txt", "r") as f:
        reader = csv.DictReader(f)

        for row in reader:
            data[row["PLAYERID"]] = row
    return data
