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

from typing import Callable, Dict
from event_parser import Event


class Game:
    def __init__(self, game: list[str], fname: str, postseason: bool = False, deduced: bool = False):
        self.id: str = game[0].split(',')[1]
        self.game = game  # line array of the game, starting with "id" and ending with the line right before the next id
        self.info = Info()
        # Pitchers and the number of earned runs they allowed, "data,er,num"
        self.earned_runs: Dict[str, int] = {}
        # 2D array of dict, one for each spot of the order. If there is a DH, there are 10 inner arrays
        # Dict looks like: {"pid": id, "pname": FName LName, "lineup_num": 0-9, "pos": 1-12, "after": Event}
        # after is the event they were inserted into the lineup before. If they are the starter, "after" is None
        # Index 0 is only used if there's a dh
        self.home_lineup: list[list[Dict[str, str | int | None]]] = [
            [{}] for _ in range(10)]
        self.away_lineup: list[list[Dict[str, str | int | None]]] = [
            [{}] for _ in range(10)]
        # Dict with info including "after": Event
        self.comments: list[Dict[str, str | int | None]] = []
        # Eg runner, lineup, etc
        self.adj: list[Dict[str, str | int | None]] = []
        # 2D array of events (you might have multiple events per plate appearance)
        self.plate_appearances: list[list[Event]] = []
        self.postseason = postseason
        self.deduced = deduced
        self.fname = fname

    def process_game(self):
        """
        Processes the WHOLE GAME. Consists of the other functions
        """
        lineup_idx = self.process_info(2)
        game_idx = self.process_lineups(lineup_idx)
        play_lines = []
        state: dict[str, int] = {
            "home_runs": 0,
            "away_runs": 0,
            "home_errors": 0,
            "away_errors": 0,
            "home_hits": 0,
            "away_hits": 0,
            "bases_occupied": 0b0,
            "half_is_top": True,
            "outs": 0
        }
        sub_line_before = False
        for line in self.game[game_idx:]:
            if line[1:4] == "adj":
                sub_line_before = False
                after = len(self.plate_appearances) if len(
                    self.plate_appearances) != 0 else None
                if line[0] == "b":
                    self.adj.append({"type": "batter_hand", "player": line.split(
                        ',')[1], "hand": line.split(',')[2], "after_pa_idx": after})
                elif line[0] == "p":
                    self.adj.append({"type": "pitcher_hand", "player": line.split(
                        ',')[1], "hand": line.split(',')[2], "after_pa_idx": after})
                elif line[0] == "r":
                    self.adj.append({"type": "runner", "player": line.split(
                        ',')[1], "base": line.split(',')[2], "after_pa_idx": after})
                elif line[0] == "l":
                    self.adj.append({"type": "lineup_order", "home": bool(
                        int(line.split(',')[1])), "ba_pos": line.split(',')[2], "after_pa_idx": after})
            elif line[0:4] == "data":
                sub_line_before = False
                self.earned_runs[line.split(',')[2]] = int(
                    line.split(',')[3].split(' ')[0])
            elif line[0:3] == "com":
                # sub_line_before = False
                after = len(self.plate_appearances) if len(
                    self.plate_appearances) != 0 else None
                self.comments.append({"comment": ','.join(line.replace(
                    '"', '').split(',')[1:]), "after_pa_idx": after})
            elif line[0:3] == "sub":
                after = len(self.plate_appearances) if len(
                    self.plate_appearances) != 0 else None
                sub_line_before = True
                if line.split(',')[3] == "0":
                    self.home_lineup[int(line.split(',')[4])].append({"pid": line.split(',')[1], "pname": line.split(',')[2].replace(
                        "\"", ""), "lineup_num": int(line.split(',')[4]), "pos": int(line.split(',')[5]), "after": after})
                else:
                    self.away_lineup[int(line.split(',')[4])].append({"pid": line.split(',')[1], "pname": line.split(',')[2].replace(
                        "\"", ""), "lineup_num": int(line.split(',')[4]), "pos": int(line.split(',')[5]), "after": after})
            elif line[0:4] == "play":
                temp_line = line.split(',')
                temp_line[5] = temp_line[5].replace('"', '').replace("'", '')
                while '..' in temp_line[5]:
                    temp_line[5] = temp_line[5].replace('..', '.N.')
                if temp_line[5].startswith('.'):
                    # Make the pitch a no-pitch so there isn't an error
                    temp_line[5] = "N" + temp_line[5]
                line = ",".join(temp_line)
                if play_lines and (line.split(',')[3] == play_lines[-1].split(',')[3] or sub_line_before):
                    play_lines.append(line)
                    sub_line_before = False
                elif play_lines:
                    self.plate_appearances.append(
                        [Event(p, self.fname, state) for p in play_lines])
                    play_lines = [line]
                    sub_line_before = False
                else:
                    sub_line_before = False
                    play_lines.append(line)
        # Just in case a play ended the game file and not a data
        if play_lines:
            self.plate_appearances.append(
                [Event(p, self.fname, state) for p in play_lines])
        # print(state)

    def process_lineups(self, start_idx: int) -> int:
        for index, line in enumerate(self.game[start_idx:]):
            if line.split(',')[0] == "start":
                if line.split(',')[3] == "1":
                    self.home_lineup[int(line.split(',')[4])] = [{"pid": line.split(',')[1], "pname": line.split(',')[2].replace(
                        "\"", ""), "lineup_num": int(line.split(',')[4]), "pos": int(line.split(',')[5]), "after": None}]  # type: ignore
                else:
                    self.away_lineup[int(line.split(',')[4])] = [{"pid": line.split(',')[1], "pname": line.split(',')[2].replace(
                        "\"", ""), "lineup_num": int(line.split(',')[4]), "pos": int(line.split(',')[5]), "after": None}]  # type: ignore
            else:
                return index + start_idx

        return start_idx

    def process_info(self, start_idx: int) -> int:
        info_lines: list[str] = []
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
        self.date: str | None = None
        self.home: str | None = None
        self.away: str | None = None
        self.night_game: bool = False
        # Scheduled number of innings, other than 2020 doubleheader should be 9
        self.innings: int = 9
        # umphome, ump1b, umplf, etc. if there isn't one of these umps, it will be "(none)"
        self.umps: Dict[str, str | None] = {
            "home": None, "1B": None, "2B": None, "3B": None, "LF": None, "RF": None}
        # 0, 1, or 2. 0 for single game, 1 for doubleheader game 1, 2 for doubleheader game 2
        self.game_number: int | None = None
        # Bool value, corresponds to info,usedh but it isn't clear on the site
        self.dh: bool = False
        # What base does the manfred runner start at? If this field doesn't exist (ie no Manfred runner) then keep it as None.
        self.tiebreaker: int | None = None
        # Either pitches (detailed pitch-by-pitch), count (count on which the play happened), or none (no info about pitches in this game)
        self.pitch_detail: str | None = None
        self.field_cond: str | None = None  # Field condition
        self.precip: str | None = None  # Rain?
        self.sky: str | None = None  # Night, sunny, dome, cloudy, etc
        self.temp: int | None = None  # 0 means unknown so if it's 0, keep it as None
        self.wind_dir: str | None = None  # Direction of wind relative to field
        self.windspeed: int | None = None  # Speed of wind, -1 means unknown
        self.start_time: str | None = None
        self.game_length: int | None = None  # Length of game in minutes
        self.attendance: int | None = None
        # Code as in https://www.retrosheet.org/parkcode.txt
        self.ballpark: str | None = None
        self.winning_pitcher: str | None = None
        self.losing_pitcher: str | None = None
        self.save: str | None = None

    def old_name_to_new(self, old_name: str) -> str:
        with open("data/CurrentNames.csv", 'r') as f:
            file = [line.rstrip().split(',') for line in f.readlines()]
            for line in file:
                if old_name == line[1]:
                    return line[0]
            return old_name

    def set_variable(self, ident: str, value: str):
        vars: dict[str, Callable[[str], None]] = {
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

    def _set_win(self, pitcher: str):
        self.winning_pitcher = pitcher

    def _set_loss(self, pitcher: str):
        self.losing_pitcher = pitcher

    def _set_save(self, pitcher: str):
        self.save = pitcher

    def _set_ballpark(self, park: str):
        self.ballpark = park

    def _set_attendance(self, attendance: str):
        try:
            self.attendance = int(attendance)
        except:
            self.attendance = None

    def _set_game_length(self, length: str):
        try:
            self.game_length = int(length)
        except:
            self.game_length = None

    def _set_night_game(self, daynight: str):
        self.night_game = daynight.lower() == 'night'

    def _set_innings(self, innings: str):
        self.innings = int(innings)

    def _set_starttime(self, time: str):
        self.start_time = None if time == "0:00" or time.lower() == "unknown" else time

    def _set_date(self, date: str):
        self.date = date

    def _set_home(self, home: str):
        self.home = self.old_name_to_new(home)

    def _set_away(self, away: str):
        self.away = self.old_name_to_new(away)

    def _set_ump_home(self, ump: str):
        self.umps['home'] = ump if ump != "(none)" else None

    def _set_ump_1b(self, ump: str):
        self.umps['1B'] = ump if ump != "(none)" else None

    def _set_ump_2b(self, ump: str):
        self.umps['2B'] = ump if ump != "(none)" else None

    def _set_ump_3b(self, ump: str):
        self.umps['3B'] = ump if ump != "(none)" else None

    def _set_ump_lf(self, ump: str):
        self.umps['LF'] = ump if ump != "(none)" else None

    def _set_ump_rf(self, ump: str):
        self.umps['RF'] = ump if ump != "(none)" else None

    def _set_dh(self, dh: str):
        self.dh = True if dh.lower() == "true" else False

    def _set_tiebreaker(self, tiebreaker: str):
        try:
            self.tiebreaker = int(tiebreaker)
        except:
            self.tiebreaker = None

    def _set_pitchdetail(self, detail: str):
        self.pitch_detail = None if detail.lower() == "none" else detail

    def _set_gamenumber(self, num: str):
        try:
            self.game_number = int(num)
        except:
            self.game_number = None

    def _set_fieldcond(self, cond: str):
        self.field_cond = None if cond.lower() == "unknown" else cond

    def _set_precip(self, precip: str):
        self.precip = None if precip.lower() == "unknown" else precip

    def _set_sky(self, sky: str):
        self.sky = None if sky.lower() == "unknown" else sky

    def _set_winddir(self, winddir: str):
        self.wind_dir = None if winddir.lower() == "unknown" else winddir

    def _set_temp(self, temperature: str):
        try:
            temp_int = int(temperature)
        except:
            self.temp = None
            return
        if temp_int != 0:
            self.temp = temp_int
        else:
            self.temp = None

    def _set_windspeed(self, speed: str):
        try:
            speed_int = int(speed)
        except:
            self.windspeed = None
            return
        if speed_int != -1:
            self.windspeed = speed_int
        else:
            self.windspeed = None
