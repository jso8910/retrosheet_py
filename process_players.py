import csv
from typing import Any, Dict


def proc_players() -> Dict[str, Dict[str, Any]]:
    data: Dict[str, Dict[str, Any]] = {}

    with open("data/BIOFILE.txt", "r") as f:
        reader = csv.DictReader(f)

        for row in reader:
            data[row["PLAYERID"]] = row
    return data
