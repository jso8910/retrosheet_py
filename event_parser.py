# TODO: fix the typing error with the PlayFlags and Pylance thinking it's type auto

from typing import Dict
from play_enums import Pitch, PlayFlags
import re


def slash_split(s: str) -> list[str]:
    return re.split(r'\/\s*(?![^()]*\))', s)


class Play:
    def __init__(self, play_text: str, filename: str):
        self.play_text = play_text.rstrip("#!?")
        # Which ones advanced? Which ones got out? How?
        self.runners: dict[str, dict[str, int | list[PlayFlags | int]]] = {}
        # Bitwise OR of PlayFlags (error | error_flag (opt) | location | hit_type | outcome)
        self.batter_play_details: PlayFlags | int = 0
        # Indicates fielders in order, including errors
        self.batter_fielders: list[PlayFlags | int] = []
        self.filename = filename

    def parse_play(self):
        parts: list[str] = self.play_text.split('.')
        advances = len(parts) > 1
        advances_list = parts[1].split(";") if len(parts) > 1 else []
        batter_string: str = parts[0].split('/')[0]
        modifiers: list[str] = slash_split(parts[0].replace(
            '-', '').replace('+', ''))[1:] if len(parts[0].split('/')) > 1 else []
        if modifiers:
            modifiers[-1] = modifiers[-1].split(".", 1)[0]
        running_plays: list[str] = [
            "BK",
            "CS",
            "DI",
            "OA",
            "PB",
            "WP",
            "PO",
            "POCS",
            "SB"
        ]
        plays: Dict[str, PlayFlags] = {
            "FC": PlayFlags["FIELDERSCHOICE"],
            "K": PlayFlags["K"],
            "NP": PlayFlags["NP"],
            "C": PlayFlags["INTERFERENCE"],
            "S": PlayFlags["SINGLE"],
            "D": PlayFlags["DOUBLE"],
            "T": PlayFlags["TRIPLE"],
            "H": PlayFlags["HOMERUN"],
            "HR": PlayFlags["HOMERUN"],
            "H": PlayFlags["HOMERUN"],
            "HP": PlayFlags["HBP"],
            "I": PlayFlags["IBB"],
            "IW": PlayFlags["IBB"],
            "W": PlayFlags["WALK"],
            "FBE": PlayFlags["E"] | PlayFlags["FOUL"] | PlayFlags["OUT"],
            "GRD": PlayFlags["GR_DOUBLE"],
        }
        bases: dict[str, str] = {
            "B": "BATTER",
            "1": "FIRST",
            "2": "SECOND",
            "3": "THIRD",
            "H": "HOME"
        }
        fielders: Dict[str, PlayFlags] = {
            "1": PlayFlags.PITCHER,
            "2": PlayFlags.CATCHER,
            "3": PlayFlags.FIRST_BASE,
            "4": PlayFlags.SECOND_BASE,
            "5": PlayFlags.THIRD_BASE,
            "6": PlayFlags.SHORTSTOP,
            "7": PlayFlags.LEFT_FIELD,
            "8": PlayFlags.CENTER_FIELD,
            "9": PlayFlags.RIGHT_FIELD,
        }
        params_list: Dict[str, PlayFlags] = {
            "UR": PlayFlags.UR,
            "RBI": PlayFlags.RBI,
            "NR": PlayFlags.NR,
            "NORBI": PlayFlags.NR,
            "TUR": PlayFlags.TUR
        }
        loc_pos: Dict[str, str] = {
            "1": "P",
            "2": "C",
            "3": "B1",
            "4": "B2",
            "5": "B3",
            "6": "SS",
            "7": "LF",
            "8": "CF",
            "9": "RF"
        }

        def parse_fielders(fielder_string: str) -> list[PlayFlags | int]:
            fielders_list: list[PlayFlags | int] = []
            fielder_temp: PlayFlags | int = 0
            fielders_unknown = False
            string_temp: str = ""
            current_param = False
            # TODO: This doesn't account for the thing where a position can be listed as "99" to show unknown positions. I could find out if this actually exists after running the code
            # TODO: or just manually filter out plays with multiple RF in a row
            for idx, char in enumerate(fielder_string):
                if char == "(":
                    current_param = True
                elif char == ")":
                    current_param = False
                # We don't want to count a param as a fielder (a param is probably a base)
                if current_param:
                    continue
                if char.isdigit() and not string_temp and (fielder_string[idx + 1] if idx + 1 < len(fielder_string) else "NO") + char != "99" and not fielders_unknown:
                    fielders_list.append(fielders[char])
                elif not string_temp and (fielder_string[idx + 1] if (idx + 1 < len(fielder_string)) else "NO") + char == "99" or (char == "9" and fielders_unknown and fielder_string[idx - 1] != "9"):
                    fielders_list.append(PlayFlags.UNKNOWN)
                    fielders_unknown = True
                elif char.isdigit() and string_temp:
                    string_temp += char
                    if not fielders_unknown:
                        fielder_temp |= fielders[char]
                    else:
                        fielder_temp |= PlayFlags.UNKNOWN
                    if idx + 1 != len(fielder_string) and fielder_string[idx + 1] == "/":
                        continue
                    fielders_list.append(fielder_temp)
                    fielder_temp = 0
                    string_temp = ""
                elif string_temp and string_temp[-1] + char == "TH":
                    fielder_temp |= PlayFlags.TH
                    fielders_list.append(fielder_temp)
                    fielder_temp = 0
                    string_temp = ""
                elif string_temp and string_temp[-2:] + char == "INT":
                    print(
                        self.play_text, "THERE IS INTERFERENCE (n/INT) HERE, THIS MIGHT BE INTERESTING", self.filename)
                    fielders_list.append(PlayFlags.INT)
                elif not char.isdigit() and not string_temp:
                    if char == "E":
                        fielder_temp |= PlayFlags.E
                        string_temp += char
                    elif char == "U":
                        fielders_list.append(PlayFlags.UNKNOWN)

                elif not char.isdigit() and string_temp:
                    string_temp += char
            params = list(
                filter(None, fielder_string.replace(')', '(').split('(')))
            if len(params) > 1 and params[1] in ("B", "1", "2", "3"):
                self.batter_play_details |= PlayFlags[bases[params[1]] + "_START"]
            return fielders_list

        def proc_running_play(start_idx: int = 0):
            nonlocal batter_string
            temp_batter_string = batter_string[start_idx:]
            # param_idx = 0
            play_enum: PlayFlags | int = 0
            if temp_batter_string[:4] == "POCS":
                play_enum |= PlayFlags.POCS
                play_enum |= PlayFlags[bases[temp_batter_string[4]] + "_END"]
                # param_idx = 5
            else:
                # print(self.play_text)
                play_enum |= PlayFlags[temp_batter_string[:2]]
                # param_idx = 3
                if play_enum == PlayFlags.PO:
                    play_enum |= PlayFlags[bases[temp_batter_string[2]] + "_START"]
                elif play_enum == PlayFlags.SB:
                    play_enum |= PlayFlags[bases[temp_batter_string[2]] + "_END"]
                    if temp_batter_string[3:6] == ";SB":
                        play_enum |= PlayFlags[bases[temp_batter_string[6]] + "_END"]
                elif play_enum not in (PlayFlags.BK, PlayFlags.WP, PlayFlags.PB, PlayFlags.DI, PlayFlags.OA):
                    play_enum |= PlayFlags[bases[temp_batter_string[2]] + "_END"]
            self.batter_play_details |= play_enum

            params = list(
                filter(None, temp_batter_string.replace(')', '(').split('(')))
            for param in params[1:]:
                if not param in tuple(params_list.keys()):
                    f = parse_fielders(param)
                    self.batter_fielders.extend(f)
                    for item in f:
                        if item & PlayFlags.E:
                            self.batter_play_details |= PlayFlags.E | PlayFlags.OUT

                else:
                    self.batter_play_details |= params_list[param]

        def proc_play():
            nonlocal batter_string
            play_enum: PlayFlags | int = 0
            if batter_string.startswith(tuple(plays.keys())):
                next_idx = 0
                if batter_string.startswith("I"):
                    play_enum |= plays['IW']
                    next_idx = 2 if batter_string.startswith("IW") else 1
                elif batter_string.startswith("H"):
                    play_enum |= plays["HR"]
                    next_idx = 2 if batter_string.startswith("HR") else 1
                if batter_string.startswith(("IW+", "I+", "W+", "K+")):
                    next_idx = 3 if batter_string.startswith("IW+") else 2
                    if batter_string[next_idx] == "E":
                        fielder = fielders[batter_string[next_idx + 1]]
                        if batter_string[next_idx + 1] + (batter_string[next_idx + 2] if len(batter_string) > next_idx + 2 else "NO") == "99":
                            fielder = PlayFlags.UNKNOWN
                        self.batter_play_details |= PlayFlags.E | fielder
                    else:
                        proc_running_play(
                            3 if batter_string.startswith("IW+") else 2)
                for play in plays:
                    if batter_string.startswith(play) and play not in ("IW", "I", "HR", "H"):
                        play_enum |= plays[play]
                        next_idx = len(play)
                f = parse_fielders(batter_string[next_idx:])
                self.batter_fielders.extend(f)
            else:
                play_enum |= PlayFlags.OUT
                f = parse_fielders(batter_string)
                self.batter_fielders.extend(f)
                for item in f:
                    if item & PlayFlags.E:
                        self.batter_play_details |= PlayFlags.E
            self.batter_play_details |= play_enum

        def proc_modifiers():
            nonlocal modifiers
            if not modifiers:
                return
            play_enum: PlayFlags | int = 0
            for modifier in modifiers:
                if not modifier:
                    continue
                loc_code = ""
                if modifier == "TH":
                    continue
                # TODO: Figure out what this modifier does (wait for email reply)
                if modifier == "S":
                    continue
                if modifier.startswith(("G", "L", "P", "F", "B")) and len(modifier) > 1 and modifier[1].isdigit():
                    play_enum |= PlayFlags[modifier[:1]]
                    loc_code = modifier[1:]
                    # Weird edge case that I encountered in this play string (D7/F7DW/UREV.1-3)
                    if loc_code.endswith("W"):
                        loc_code = loc_code[:-1]
                    # print(self.play_text)
                    if loc_code == "2F":
                        loc_code = "CATCHERF_LOC"
                    else:
                        for original, replacement in loc_pos.items():
                            loc_code = loc_code.replace(original, replacement)
                        loc_code += "_LOC"
                    try:
                        play_enum |= PlayFlags[loc_code]
                    except KeyError:
                        play_enum |= PlayFlags.INVALID_LOC
                elif modifier.startswith(("G", "L", "P", "F", "B")) and len(modifier) == 1:
                    play_enum |= PlayFlags[modifier[:1]]
                elif modifier.startswith(("BG", "BP", "BL")) and len(modifier) == 2:
                    play_enum |= PlayFlags[modifier[:2]]
                elif modifier.startswith(("BG", "BP", "BL")) and modifier[2].isdigit():
                    play_enum |= PlayFlags[modifier[:2]]
                    loc_code = modifier[2:]
                    if loc_code == "2F":
                        loc_code = "CATCHERF_LOC"
                    else:
                        for original, replacement in loc_pos.items():
                            loc_code = loc_code.replace(original, replacement)
                        loc_code += "_LOC"
                    try:
                        play_enum |= PlayFlags[loc_code]
                    except KeyError:
                        play_enum |= PlayFlags.INVALID_LOC
                elif modifier[0] == "R" and (modifier[1] if len(modifier) > 1 else "N").isdigit():
                    play_enum |= PlayFlags.R | (
                        fielders[modifier[1]] if len(modifier) > 1 else 0)
                elif modifier[0] == "U":
                    play_enum |= PlayFlags.U
                    for char in modifier[1:]:
                        if char.isdigit():
                            play_enum |= fielders[char]
                        elif char == "R":
                            # TODO: Is it actually a relay? Wait for email reply.
                            play_enum |= PlayFlags.R
                elif modifier[0:2] == "TH" and (modifier[2] if len(modifier) > 1 else "N") in ("H", "1", "2", "3"):
                    play_enum |= PlayFlags.THM | (
                        PlayFlags[bases[modifier[2]] + "_END"] if len(modifier) > 2 else 0)
                elif modifier[0] == "E" and (modifier[1] if len(modifier) > 1 else "N") in (str(i) for i in range(1, 10)):
                    play_enum |= PlayFlags.E | (
                        fielders[modifier[1]] if len(modifier) > 1 else 0)
                elif modifier[0].isdigit():
                    loc_code = modifier
                    if loc_code == "2F":
                        loc_code = "CATCHERF_LOC"
                    else:
                        for original, replacement in loc_pos.items():
                            loc_code = loc_code.replace(original, replacement)
                        loc_code += "_LOC"
                    try:
                        play_enum |= PlayFlags[loc_code]
                    except KeyError:
                        play_enum |= PlayFlags.INVALID_LOC
                else:
                    # print(self.play_text)
                    try:
                        play_enum |= PlayFlags[modifier]
                    except KeyError:
                        print(modifier, self.play_text, self.filename)
                        play_enum |= PlayFlags.INVALID_MODIFIER
            self.batter_play_details |= play_enum

        def proc_advances():
            nonlocal advances_list
            for advance in advances_list:
                params = list(
                    filter(None, advance.replace(')', '(').split('(')))
                starting_base = params[0][0]
                outcome = params[0][1]
                ending_base = params[0][2]
                self.runners[starting_base] = {
                    "play_flags": 0, "fielders": [0]}
                if outcome == "X":
                    self.runners[starting_base]["play_flags"] |= PlayFlags.OUT  # type: ignore # nopep8
                self.runners[starting_base]["play_flags"] |= PlayFlags[bases[ending_base] + "_END"]  # type: ignore # nopep8
                for param in params[1:]:
                    if not param in tuple(params_list.keys()):
                        f = parse_fielders(param)
                        self.runners[starting_base]["fielders"].extend(f)  # type: ignore # nopep8
                        for item in f:
                            if item & PlayFlags.E:
                                self.runners[starting_base]["play_flags"] |= PlayFlags.E | PlayFlags.OUT  # type: ignore # nopep8
                    else:
                        self.runners[starting_base]["play_flags"] |= params_list[param]  # type: ignore # nopep8

        if batter_string.startswith(tuple(running_plays)):
            proc_running_play()
        elif batter_string.startswith(tuple(plays.keys())) or batter_string[0].isdigit():
            proc_play()

        proc_modifiers()
        if advances:
            proc_advances()


class Event:
    def __init__(self, event_string: str, filename: str):
        # Event string: list of lines of events. Normally just one line
        self.event_string = event_string
        self.inning = int(self.event_string.split(',')[1])
        self.half_is_top = int(self.event_string.split(',')[2]) != 1
        self.batter = self.event_string.split(',')[3]
        self.count_of_play = (list(self.event_string.split(',')[4])[0], list(self.event_string.split(
            ',')[4])[1]) if (len(self.event_string.split(',')[4]) == 2 and self.event_string.split(',')[4][1].isdigit() and self.event_string.split(',')[4][0] != "?") else (None, None)
        self.pitches = []
        self.play: Play | None = None
        self.filename = filename
        self.get_pitches()
        self.create_plays()

    def create_plays(self):
        p = Play(self.event_string.split(',')[6], self.filename)
        p.parse_play()
        self.play = p

    def get_pitches(self) -> None:
        """
        Late in the night (idk, around 10:30pm, so not that late) on September 28 2022 Singapore time, this code worked 5 minutes after I ran it for the first time
        """
        pitch_string = self.event_string.split(
            ',')[5].replace("'", "").replace('"', '')
        if not pitch_string or pitch_string[0] == "?":
            return
        pitch_list: list[Pitch] = []
        temp: list[Pitch] = []
        for idx, char in enumerate(pitch_string):
            if char.isdigit():
                char = "PO_" + char
            # If it's just a normal pitch
            if not temp and char not in ['*', '>'] and idx < len(pitch_string) - 1 and pitch_string[idx + 1] not in ['+', '.']:
                try:
                    pitch_list.append(Pitch[char])
                except KeyError:
                    print("PITCH ERROR", char, self.event_string, self.filename)
                continue

            if not temp and char not in ['*', '>'] and idx + 1 == len(pitch_string):
                try:
                    pitch_list.append(Pitch[char])
                except KeyError:
                    print("PITCH ERROR", char, self.event_string, self.filename)
                continue

            # If it is a preceding modifier
            if char in ['*', '>']:
                temp.append(Pitch['CATCHER_BLOCK' if char ==
                            '*' else 'RUNNER_GOING'])
                continue

            # If it's a pitch with a post-modifier
            if idx < len(pitch_string) - 1 and pitch_string[idx + 1] in ['+', '.']:
                try:
                    temp.append(Pitch[char if char not in [
                                '+', '.'] else ('CATCHER_PICK' if char == '+' else 'PLAY_NO_BATTER')])
                except KeyError:
                    print("PITCH ERROR", char, self.event_string, self.filename)
                continue

            # If there is a post-modifier (there might also be a preceding modifier, who knows)
            if char in ['+', '.'] and temp and (pitch_string[idx + 1]if idx + 1 < len(pitch_string) else "x") not in ['+', '.']:
                temp_num = Pitch['CATCHER_PICK' if char ==
                                 '+' else 'PLAY_NO_BATTER']
                for mod in temp:
                    temp_num |= mod
                pitch_list.append(temp_num)
                temp = []
                continue

            # No postfix
            if temp and char not in ['+', '.']:
                try:
                    n = Pitch[char]
                    for mod in temp:
                        n |= mod
                    pitch_list.append(n)
                except KeyError:
                    print("PITCH ERROR", char, self.event_string, self.filename)
                temp = []
                continue
        self.pitches = pitch_list
