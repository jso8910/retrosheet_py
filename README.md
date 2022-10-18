# Retrosheet sqlite database parser

## Copyright notice

> The information used here was obtained free of
> charge from and is copyrighted by Retrosheet. Interested
> parties may contact Retrosheet at "www.retrosheet.org".

## Information about the Retrosheet files included with the project

> The Retrosheet files included with this Python project include BIOFILE.txt, a list of every MLB player, manager, and umpire, and CurrentNames.csv, a file which contains the past names of every MLB team as it corresponds to its current name.

> Use of this project will result in the download of 13 files from Retrosheet. One zip file per decade for the play by play data of each decade from the 1910s to the 2020s and one zip file that contains every postseason game.

# Notes of clarification

If you see something like "BATTER_START", "FIRST_START", etc in batter_fielders along with a fielder, that represents the runner that was putout by that fielder, by the base they started at. This is either there because of a double or triple play, or because a player was covering a base they wouldnt normally cover (eg SS at first base).

# Information about the project and usage

This is a project which takes every Retrosheet regular season and postseason (not including the all star game) file and parses it into a database.
There are still a few bugs which need to be resolved. These involve some location codes and modifiers, so if you see INVALID_LOC or INVALID_MODIFIER then that's it.

To create the database, simply install all the requirements in requirements.txt (create a venv if you want to):

```sh
pip install -r requirements.txt
```

Then, make sure you are in the directory of this repository (not any other directory) and run this command:

```sh
python3 main.py
```

This will download the retrosheet files and then create the database in a file `retrosheet.sqlite`.

Once the database has been created (this may take well over an hour and maybe even 2 hours. Even if it appears the program isn't doing anything, don't halt it.), you should use the SQLAlchemy schema file `db_schema.py`. You can see an example of how to initialize the connection to the database in `build_db.py`, in `__init__`.

One thing to know is that if an attribute is a `relationship("ClassNameHere", backref="parent")`, that means that the attribute, when you access it, is a list of `ClassNameHere` (unless `uselist=False` is set as a parameter, in which case it is simply one object of that, not a list) and from a `ClassNameHere` instance you can access its parent through `ClassNameHere.parent`, as is in the `backref` parameter

After you make a query, what you'll need to do for all classes except for `PA`, `Player`, and `InfoDB` is to run `object.to_correct_types()`. The 3 stated tables which don't need it still have this function but it does nothing. This will convert the stringified types to the correct python types. You will also need to run this function when accessing, for example, `EventDB.play`, because this is an object of type `PlayDB` which has some stringified lists and dictionaries. So, to access the correctly typed functions, you would run `EventDB.play.to_correct_types()` before accessing anything from `EventDB.play`

You can see a very rudimentary example of a query and using `to_correct_types()` in `test_script.py`

In general, the types of the stringified fields correspond to the Model's respective class in either `event_parser.py` (contains `Play` and `Event`) or `process_game.py` (contains `Game`). Look inside the `__init__` function for type hinting. Later in this readme, there are examples of the basic format of the dictionaries and lists but you can do your own experimenting.

All enums are also flags, so you can use bitwise or and and to set bits and check if a bit is set.

# Examples of type converted fields

No real values here, just the type of the value

The listed key, B, can be any of these: B, 1, 2, 3. B represents the batter and 1, 2, and 3 represent starting bases

```py
PlayDB.runners = {"B": {"play_flags": PlayFlags, "fielders": list[PlayFlags]}}
```

```py
PlayDB.batter_play_details = PlayFlags
```

```py
PlayDB.batter_fielders = list[PlayFlags]
```

```py
GameDB.game = list[str]
```

```py
GameDB.earned_runs = {"Pitcher Name": int}
```

`GameDB.home_lineup` is a 2D array of dictionaries with the format below. There are 9 filled 2D arrays if there is no DH (there will be an empty 10th array) and 10 if there is a DH, with the 10th being the pitcher who I believe has a lineup_num of 0.
`after` is an integer representing the index of an event in the game's events list. This should be None for starters, and for any subsequent substitutions who are in the list, will be whatever event they were substituted in after
`GameDB.away_lineup` has the exact same format
`pid` represents a player ID that should almost definitely correspond to a row in the Player table

```py
GameDB.home_lineup = list[list[{"pid": str, "pname": str, "lineup_num": int, "pos": int, "after": int|None}]]
```

`after_pa_idx` in `GameDB.comments` is exactly the same as in the lineups. It will be None if the comment happened before the first Event of the game

```py
GameDB.comments = list[{"comment": str, "after_pa_idx": int}]
```

There are a few different formats of `GameDB.adj` depending on the value of `type`, as delimited by commas below and described in the python comments

```py
GameDB.adj = list[
    # `lineup_order` represents a team batting out of order.
    # ba_pos is a digit string that says which lineup position batted instead of the intended one.
    # home is a bool that says whether it was the home team or away team which did this
    {"type": "lineup_order", "home": bool, "ba_pos": str, "after_pa_idx": int},
    # `runner` is used for games in which a runner is placed on a base (for eg with the extra innings rule in 2020 and 2021)
    # Player is a player ID. You know the drill
    # Base is a string, type castable to an int which is either 1, 2, or 3 and corresponds to a base. I'm not sure there are any examples of this that aren't from the extra innings rule so it will almost always be 2
    {"type": "runner", "player": str, "base": str, "after_pa_idx": int},
    # `pitcher_hand` is for when a pitcher pitches using an unexpected hand. Not many examples of this being used
    # player is a player ID
    # Hand is either R or L, representing the hand they pitched with
    {"type": "pitcher_hand", "player": str, "hand": str, "after_pa_idx": int},
    # `batter_hand is for when a batter bats using an unexpected hand. This includes a switch hitter batting in a way that is usually unfavorable for splits
    # player is a player ID
    # Hand is either R or L
    {"type": "batter_hand", "player": str, "hand": str, "after_pa_idx": int}
]
```

Simply a list of Pitch enum types.

```py
EventDB.pitches = list[Pitch]
```
