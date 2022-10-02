"""

https://www.retrosheet.org/eventfile.htm
literal pain

Make sure to keep comments in the right place (I assume most comments are after the play they are attached to but check this just to be sure, maybe say afterPlay as the name of the db field)
Put the info somewhere

For pbp, read in detail from "The pitches field of the play record" to the end of "Event advances."

Return the dict or whatever is used to store the game at the end of this process

https://www.retrosheet.org/location.htm
somehow use this? idk

https://www.retrosheet.org/GameFiles.pdf
Make sure to pay attention to this!!!

Find a way to use something like an enum for things with set possible values (eg fieldcond, precip, sky, winddir, pitch_detail, etc)
"""

from event_parser import Event


class Game:
    def __init__(self, game):
        # TODO: Along with each event, keep the game state (where are there runners, lineup with substitutes, fielding positions, score, # of hits, etc) with it. Maybe use a tuple
        self.id = game[0].split(',')[1]
        self.game = game # line array of the game, starting with "id" and ending with the line right before the next id
        self.info = Info()
        self.earned_runs = {} # Pitchers and the number of earned runs they allowed, "data,er,num"
        # 2D array of dict, one for each spot of the order. If there is a DH, there are 10 inner arrays
        # Dict looks like: {"pid": id, "pname": FName LName, "lineup_num": 0-9, "pos": 1-12, "after": Event}
        # after is the event they were inserted into the lineup before. If they are the starter, "after" is None
        # Index 0 is only used if there's a dh
        self.home_lineup = [[] for _ in range(10)]
        self.away_lineup = [[] for _ in range(10)]
        # Dict with info including "after": Event
        self.comments = []
        # Eg runner, lineup, etc
        self.adj = []
        self.plate_appearances: list[list[Event]] = []    # 2D array of events (you might have multiple events per plate appearance)

    def process_game(self):
        lineup_idx = self.process_info(2)
        game_idx = self.process_lineups(lineup_idx)
        play_lines = []
        sub_line_before = False
        # for line in self.game[game_idx:]:
        #     if line.endswith("NP"):
        #         print(line)
        for line in self.game[game_idx:]:
            if line[1:4] == "adj":
                sub_line_before = False
                after = len(self.plate_appearances) - 1 if len(self.plate_appearances) != 0 else None
                if line[0] == "b":
                    self.adj.append({"type": "batter_hand", "player": line.split(',')[1], "hand": line.split(',')[2], "after_pa_idx": after})
                elif line[0] == "p":
                    self.adj.append({"type": "pitcher_hand", "player": line.split(',')[1], "hand": line.split(',')[2], "after_pa_idx": after})
                elif line[0] == "r":
                    self.adj.append({"type": "runner", "player": line.split(',')[1], "base": line.split(',')[2], "after_pa_idx": after})
                elif line[0] == "l":
                    self.adj.append({"type": "lineup_order", "home": bool(int(line.split(',')[1])), "ba_pos": line.split(',')[2], "after_pa_idx": after})
            elif line[0:4] == "data":
                sub_line_before = False
                self.earned_runs[line.split(',')[2]] = int(line.split(',')[3])
            elif line[0:3] == "com":
                sub_line_before = False
                after = len(self.plate_appearances) - 1 if len(self.plate_appearances) != 0 else None
                self.comments.append({"comment": ','.join(line.replace('"', '').split(',')[1:]), "after_pa_idx": after})
            elif line[0:3] == "sub":
                after = len(self.plate_appearances) - 1 if len(self.plate_appearances) != 0 else None
                sub_line_before = True
                if line.split(',')[3] == "0":
                    self.home_lineup[int(line.split(',')[4])].append({"pid": line.split(',')[1], "pname": line.split(',')[2].replace("\"", ""), "lineup_num": int(line.split(',')[4]), "pos": int(line.split(',')[5]), "after": after})
                else:
                    self.away_lineup[int(line.split(',')[4])].append({"pid": line.split(',')[1], "pname": line.split(',')[2].replace("\"", ""), "lineup_num": int(line.split(',')[4]), "pos": int(line.split(',')[5]), "after": after})
            elif line[0:4] == "play" and play_lines:
                # Check to see if the name is the same (ie same plate appearance)
                if line.split(',')[3] == play_lines[-1].split(',')[3] or sub_line_before:
                    temp_line = line.split(',')
                    temp_line[5] = temp_line[5].replace('..', '.N.')
                    if temp_line[5].startswith('.'):
                        # Make the pitch a no-pitch so there isn't an error
                        temp_line[5] = "N" + temp_line[5]
                    line = ",".join(temp_line)
                    play_lines.append(line)
                    sub_line_before = False
                else:
                    self.plate_appearances.append([Event(p) for p in play_lines])
                    play_lines = [line]
                    sub_line_before = False
            elif line[0:4] == "play" and not play_lines:
                temp_line = line.split(',')
                temp_line[5] = temp_line[5].replace('..', '.N.')
                if temp_line[5].startswith('.'):
                    # Make the pitch a no-pitch so there isn't an error
                    temp_line[5] = "N" + temp_line[5]
                line = ",".join(temp_line)
                sub_line_before = False
                play_lines.append(line)
        # Just in case a play ended the game file and not a data
        if play_lines:
            self.plate_appearances.append([Event(p) for p in play_lines])

    def process_lineups(self, start_idx):
        for index, line in enumerate(self.game[start_idx:]):
            if line.split(',')[0] == "start":
                if line.split(',')[3] == "1":
                    self.home_lineup[int(line.split(',')[4])] = [{"pid": line.split(',')[1], "pname": line.split(',')[2].replace("\"", ""), "lineup_num": int(line.split(',')[4]), "pos": int(line.split(',')[5]), "after": None}]
                else:
                    self.away_lineup[int(line.split(',')[4])] = [{"pid": line.split(',')[1], "pname": line.split(',')[2].replace("\"", ""), "lineup_num": int(line.split(',')[4]), "pos": int(line.split(',')[5]), "after": None}]
            else:
                return index + start_idx

    def process_info(self, start_idx):
        info_lines = []
        end_idx = 0
        for index, line in enumerate(self.game[start_idx:]):
            ident = line.split(',')[0]
            if ident == "info":
                info_lines.append(line)
            else:
                end_idx = index + start_idx
                break

        for info in info_lines:
            self.info.set_variable(info.split(',')[1], info.split(',')[2])

        return end_idx
        
            

class Info:
    def __init__(self):
        # These are all info fields https://www.retrosheet.org/eventfile.htm#1
        self.date = None
        self.home = None
        self.away = None
        self.night_game = False
        self.innings = 9 # Scheduled number of innings, other than 2020 doubleheader should be 9
        self.umps = {"home": None, "1B": None, "2B": None, "3B": None, "LF": None, "RF": None} # umphome, ump1b, umplf, etc. if there isn't one of these umps, it will be "(none)"
        self.game_number = None # 0, 1, or 2. 0 for single game, 1 for doubleheader game 1, 2 for doubleheader game 2
        self.dh = None # Bool value, corresponds to info,usedh but it isn't clear on the site
        self.tiebreaker = None # What base does the manfred runner start at? If this field doesn't exist (ie no Manfred runner) then keep it as None.
        self.pitch_detail = None # Either pitches (detailed pitch-by-pitch), count (count on which the play happened), or none (no info about pitches in this game)
        self.field_cond = None # Field condition
        self.precip = None # Rain?
        self.sky = None # Night, sunny, dome, cloudy, etc
        self.temp = None # 0 means unknown so if it's 0, keep it as None
        self.wind_dir = None # Direction of wind relative to field
        self.windspeed = None # Speed of wind, -1 means unknown
        self.start_time = None
        self.game_length = None # Length of game in minutes
        self.attendance = None
        self.ballpark = None # Code as in https://www.retrosheet.org/parkcode.txt
        self.winning_pitcher = None
        self.losing_pitcher = None
        self.save = None

    def set_variable(self, ident, value):
        vars = {
            "date": self._set_date,
            "visteam": self._set_away,
            "hometeam": self._set_home,
            "number": self._set_gamenumber,
            "starttime": self._set_starttime,
            "daynight": self._set_night_game,
            "innings": self._set_innings,
            "tiebreaker": self._set_tiebreaker,
            "usedh": self._set_dh,
            "pitches": self._set_pitchdetail,
            "umphome": self._set_ump_home,
            "ump1b": self._set_ump_1b,
            "ump2b": self._set_ump_2b,
            "ump3b": self._set_ump_3b,
            "umplf": self._set_ump_lf,
            "umplf": self._set_ump_rf,
            "fieldcond": self._set_fieldcond,
            "precip": self._set_precip,
            "sky": self._set_sky,
            "temp": self._set_temp,
            "winddir": self._set_winddir,
            "windspeed": self._set_windspeed,
            "timeofgame": self._set_game_length,
            "attendance": self._set_attendance,
            "site": self._set_ballpark,
            "wp": self._set_win,
            "lp": self._set_loss,
            "save": self._set_save,
        }
        if ident in vars:
            vars[ident](value)

    def _set_win(self, pitcher):
        self.winning_pitcher = pitcher

    def _set_loss(self, pitcher):
        self.losing_pitcher = pitcher

    def _set_save(self, pitcher):
        self.save = pitcher

    def _set_ballpark(self, park):
        self.ballpark = park

    def _set_attendance(self, attendance):
        try:
            self.attendance = int(attendance)
        except:
            self.attendance = None

    def _set_game_length(self, length):
        try:
            self.game_length = int(length)
        except:
            self.game_length = None

    def _set_night_game(self, daynight):
        self.night_game = daynight.lower() == 'night'

    def _set_innings(self, innings):
        self.innings = int(innings)

    def _set_starttime(self, time):
        self.start_time = None if time == "0:00" or time.lower() == "unknown" else time

    def _set_date(self, date):
        self.date = date

    def _set_home(self, home):
        self.home = home

    def _set_away(self, away):
        self.away = away

    def _set_ump_home(self, ump):
        self.umps['home'] = ump if ump != "(none)" else None

    def _set_ump_1b(self, ump):
        self.umps['1B'] = ump if ump != "(none)" else None

    def _set_ump_2b(self, ump):
        self.umps['2B'] = ump if ump != "(none)" else None

    def _set_ump_3b(self, ump):
        self.umps['3B'] = ump if ump != "(none)" else None

    def _set_ump_lf(self, ump):
        self.umps['LF'] = ump if ump != "(none)" else None

    def _set_ump_rf(self, ump):
        self.umps['RF'] = ump if ump != "(none)" else None

    def _set_dh(self, dh):
        self.dh = True if dh.lower() == "true" else False

    def _set_tiebreaker(self, tiebreaker):
        try:
            self.tiebreaker = int(tiebreaker)
        except:
            self.tiebreaker = None

    def _set_pitchdetail(self, detail):
        self.pitch_detail = None if detail.lower() == "none" else detail

    def _set_gamenumber(self, num):
        try:
            self.game_number = int(num)
        except:
            self.game_number = None

    def _set_fieldcond(self, cond):
        self.field_cond = None if cond.lower() == "unknown" else cond

    def _set_precip(self, precip):
        self.precip = None if precip.lower() == "unknown" else precip

    def _set_sky(self, sky):
        self.sky = None if sky.lower() == "unknown" else sky

    def _set_winddir(self, winddir):
        self.wind_dir = None if winddir.lower() == "unknown" else winddir

    def _set_temp(self, temperature):
        try:
            temperature = int(temperature)
        except:
            self.temp = None
            return
        if temperature != 0:
            self.temp = temperature
        else:
            self.temp = None

    def _set_windspeed(self, speed):
        try:
            speed = int(speed)
        except:
            self.windspeed = None
            return
        if speed != -1:
            self.windspeed = speed
        else:
            self.windspeed = None


# NOTE SAMPLE CODE. Requires downloading 2021CHN.EVN
from itertools import groupby

with open("2021CHN.EVN", "r") as f:
    # Use this code in process_season.py
    file = [line.rstrip() for line in f.readlines()]
    i = (list(group) for _, group in groupby(file, lambda x: x.startswith("id,")))
    season = [a + b for a, b in zip(i, i)]
    game = Game(season[0])
    game.process_game()
    # print([g for g in game.plate_appearances[:5]])
    # __import__('pprint').pprint([[vars(g) for g in p] for p in game.plate_appearances[:5]])
    # __import__('pprint').pprint(game.comments)
    # __import__('pprint').pprint(vars(game.plate_appearances[20][0]))
    # __import__('pprint').pprint(game.home_lineup)
    # __import__('pprint').pprint(game.away_lineup)
    # __import__('pprint').pprint(vars(game.info))