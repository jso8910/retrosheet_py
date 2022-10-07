"""
In this file lies horrors
"""

from enum import IntFlag, auto


class Pitch(IntFlag):
    """
    +  following pickoff throw by the catcher AFTER THE PITCH
    *  indicates the following pitch was blocked by the catcher BEFORE THE PITCH
    .  marker for play not involving the batter (in any "play," of the same at bat after something like a balk, stolen base, caught stealing, etc (not pickoff)) AFTER PITCH
    1  pickoff throw to first NOT A MASK
    2  pickoff throw to second NOT A MASK
    3  pickoff throw to third NOT A MASK
    >  Indicates a runner going on the pitch that comes AFTER this

    B  ball
    C  called strike
    F  foul
    H  hit batter
    I  intentional ball (ONLY USED IF THERE WAS AN ACTUAL INTENTIONAL WALK WITH REAL PITCHES)
    K  strike (unknown type)
    L  foul bunt
    M  missed bunt attempt
    N  no pitch (on balks and interference calls)
    O  foul tip on bunt
    P  pitchout
    Q  swinging on pitchout
    R  foul ball on pitchout
    S  swinging strike
    T  foul tip
    U  unknown or missed pitch
    V  called ball because pitcher went to his mouth (ALSO USED IN THE NEW AUTO INTENTIONAL WALK)
    X  ball put into play by batter
    Y  ball put into play on pitchout

    """
    # Use flags (eg 0b00010000 or whatever) for stuff like pickoff by catcher. Look for examples of the 7 things at the top of the pitches record thing to see if they should be flags
    # Flags
    CATCHER_PICK = 0b100000000  # "Catcher pickoff after the pitch"
    CATCHER_BLOCK = 0b010000000  # "Catcher had to block the pitch"
    RUNNER_GOING = 0b001000000  # "Runner(s) going on the pitch"
    # "Play happened on this pitch where the batter wasn't involved"
    PLAY_NO_BATTER = 0b000100000
    B = auto()  # "Ball"
    C = auto()  # "Called strike"
    F = auto()  # "Foul"
    H = auto()  # "Hit by pitch"
    I = auto()  # "Pitched intentional ball"
    K = auto()  # "Strike, unknown type"
    L = auto()  # "Foul bunt"
    M = auto()  # "Missed bunt"
    N = auto()  # "No pitch (balk or interference)"
    O = auto()  # "Bunt foul tip"
    P = auto()  # "Pitchout"
    Q = auto()  # "Swing on pitchout"
    R = auto()  # "Foul on pitchout"
    S = auto()  # "Swinging strike"
    T = auto()  # "Foul tip"
    U = auto()  # "Unknown or missed pitch"
    V = auto()  # "Called ball because pitcher went to his mouth or no-pitch intentional ball"
    X = auto()  # "Ball put into play by batter"
    Y = auto()  # "Ball put into play on pitchout"
    PO_1 = auto()   # Pickoff 1B
    PO_2 = auto()   # Pickoff 2B
    PO_3 = auto()   # Pickoff 3B


class PlayFlags(IntFlag):
    # Contains errors for the batter (ie E4, E5, E3, E2, E1, E6, E7, E8, E9, no error) and modifiers (eg throwing)
    # Fielder modifiers
    # Locations as defined in https://www.retrosheet.org/location.htm
    # Hit type/modifier as in Groundball, line drive, sac fly
    # Outcomes as in flyout, putout, gidp, 2b, 3b, hr, single, error, fielders choice, etc (defined in https://www.retrosheet.org/eventfile.htm)
    # Notation for multiple outs is just an list of outs
    # TODO: DOESNT SUPPORT K+EVENT, W+EVENT, or IW+EVENT (aka I+EVENT) YET

    # Plays
    OUT = auto()            # Use this on each play to show there was an out. Bitwise OR with fielders involved IN THAT OUT. WITH MULTIPLE OUTS, USE A SEPARATE PART OF THE ARRAY
    FIELDERSCHOICE = auto()  # Out not necessarily made, used for throwing a player out
    K = auto()              # Strikeout
    NP = auto()             # No play, substitution
    # Followed by an error modifier to say who did the interference. Implies batter advance to first. Notated by C/E$
    INTERFERENCE = auto()
    SINGLE = auto()
    DOUBLE = auto()
    TRIPLE = auto()
    HOMERUN = auto()        # Can be combined with fielder, either H or HR
    HBP = auto()
    IBB = auto()            # Either I or IW
    WALK = auto()           # Notated as W
    FOUL = auto()           # Used for FBE$
    GR_DOUBLE = auto()      # GRD, groundrule double

    # Baserunning events NOT INVOLVING BATTER (or used in K+event and IW+event or W+event)
    BK = auto()             # Balk
    CS = auto()             # Caught stealing
    DI = auto()             # Defensive indifference
    OA = auto()             # Unidentified advance
    PB = auto()             # Passed ball
    WP = auto()             # Wild pitch
    PO = auto()             # Picked off
    POCS = auto()           # Picked off caught stealing
    SB = auto()             # Stolen base

    # Params
    UR = auto()             # Unearned run
    RBI = auto()            # RBI credited
    NR = auto()             # No RBI. Along with NR, NORBI has to be used
    TUR = auto()            # Not sure what this is. Team unearned run

    # Multi-purpose
    E = auto()              # Error (remember to bitwise OR with position). This works as a modifier AND a play (in the case of an error allowing the batter to reach)
    # Throw. Normally paired with error to show it's a throwing error.
    TH = auto()

    # Modifiers
    THM = auto()            # Throw to base modifier
    AP = auto()             # Appeal play (I think this means out? Check this NOTE)
    BGDP = auto()           # Bunt GIDP
    BINT = auto()           # Batter interference
    BL = auto()             # Bunt linedrive
    BOOT = auto()           # Batting out of turn
    BG = auto()             # Bunt grounder
    BP = auto()             # Bunt popup
    BPDP = auto()           # Bunt popup into double play
    BR = auto()             # Runner hit by batted ball
    C = auto()              # Arguing called third strike
    COUB = auto()           # Courtesy batter
    COUF = auto()           # Courtesy fielder
    COUR = auto()           # Courtesy runner
    DP = auto()             # Unspecified double play
    F = auto()              # Fly
    FDP = auto()            # Fly into double play
    FINT = auto()           # Fan interference
    # Foul (I assume for popups, flyballs, bunts, etc. probably only when they end the AB)
    FL = auto()
    FO = auto()             # Forceout
    G = auto()              # Groundball
    GDP = auto()            # GIDP
    GTP = auto()            # Grounded into triple play lmfaooooo
    IF = auto()             # Infield fly rule
    # Interference (does this mean an out? I assume it does. TODO Look for examples of it)
    INT = auto()
    # Inside the park homerun (exists alongside H$ or HR$ to indicate the position)
    IPHR = auto()
    L = auto()              # Linedrive
    LDP = auto()            # Lined into double play
    LTP = auto()            # Lined into triple play
    # Manager review of call on field (TODO I can't find any examples of this being used)
    MREV = auto()
    # No double play credited. I don't know why, can't find examples in 2021 in the 4 teams I looked at
    NDP = auto()
    OBS = auto()            # Obstruction (fielder obstructing a runner). Look for examples
    P = auto()              # Pop fly
    # Runner passed another runner and was called out (TODO look for examples)
    PASS = auto()
    # R$. Relay from initial fielder to $ with no out. TODO look for examples
    R = auto()
    RINT = auto()           # Runner interference
    SF = auto()             # Sacrifice fly
    SH = auto()             # Sacrifice hit (bunt)
    TP = auto()             # Unspecified triple play
    UINT = auto()           # Umpire interference
    UREV = auto()           # Umpire review of call on field (TODO find examples)

    # Positions
    PITCHER = auto()
    CATCHER = auto()
    FIRST_BASE = auto()
    SECOND_BASE = auto()
    THIRD_BASE = auto()
    SHORTSTOP = auto()
    LEFT_FIELD = auto()
    CENTER_FIELD = auto()
    RIGHT_FIELD = auto()
    UNKNOWN = auto()

    # Bases, for starting position
    BATTER_START = auto()
    FIRST_START = auto()
    SECOND_START = auto()
    THIRD_START = auto()

    # Bases, for ending position
    HOME_END = auto()
    FIRST_END = auto()
    SECOND_END = auto()
    THIRD_END = auto()

    # Locations
    """
    For these locations, positions are replaced
    1 is replaced with P
    2 is replaced with C
    3 is replaced with B1
    4 is replaced with B2
    5 is replaced with B3
    6 is replaced with SS
    etc
    """
    # Foul balls
    # Left side/center
    # Foul ball near catcher NOTE I NEED TO MANAULLY CHANGE 2F TO CATCHERF_LOC, NO SIMPLE REPLACEMENT
    CATCHERF_LOC = auto()
    CB3F_LOC = auto()           # Foul ball between C and 3Bman
    B3F_LOC = auto()            # Foul ball behind/around 3Bman
    B3DF_LOC = auto()           # Foul ball deep behind 3Bman
    LFLSF_LOC = auto()          # Foul ball in shallow left fielder territory
    LFLF_LOC = auto()           # Foul ball in left field territory
    LFLDF_LOC = auto()          # Foul ball in deep left field
    # Right side
    CB1F_LOC = auto()           # Foul ball between C and 1B
    B1F_LOC = auto()            # Foul ball behind/around 1Bman
    B1DF_LOC = auto()           # Foul ball deep behind 1Bman
    RFLSF_LOC = auto()          # Foul ball in shallow left fielder territory
    RFLF_LOC = auto()           # Foul ball in left field territory
    RFLDF_LOC = auto()          # Foul ball in deep left field

    # Infield
    C_LOC = auto()              # In front of Catcher
    CB3_LOC = auto()            # Between catcher and 3b
    PS_LOC = auto()             # In front of mound (pitcher shallow)
    CB1_LOC = auto()            # Between catcher and 1B

    P3B_LOC = auto()            # 3B side of the mound
    P_LOC = auto()              # The mound lol
    PB1_LOC = auto()            # 1B side of mound

    B3S_LOC = auto()            # In front of 3B
    B3SSS_LOC = auto()          # In front of between 3b and SS
    SSS_LOC = auto()            # In front of shortstop
    SSMS_LOC = auto()           # Shortstop side of up the middle, shallow
    B2MS_LOC = auto()           # 2B side of up the middle, shallow
    B2S_LOC = auto()            # In front of 2B
    B1B2S_LOC = auto()          # In front of between 1b and 2b
    B1S_LOC = auto()            # In front of 1B

    B3_LOC = auto()             # 3B
    B3SS_LOC = auto()           # Between 3B and SS
    SS_LOC = auto()             # Shortstop
    SSM_LOC = auto()            # Shortstop side of up the middle
    B2M_LOC = auto()            # 2B side of up the middle
    B2_LOC = auto()             # 2B
    B1B2_LOC = auto()           # Between 1b and 2b
    B1_LOC = auto()             # 1B

    B3D_LOC = auto()            # 3B deep
    B3SSD_LOC = auto()          # Between 3B and SS deep
    SSD_LOC = auto()            # Shortstop deep
    SSMD_LOC = auto()           # Shortstop side of up the middle deep
    B2MD_LOC = auto()           # 2B side of up the middle deep
    B2D_LOC = auto()            # 2B deep
    B1B2D_LOC = auto()          # Between 1b and 2b deep
    B1D_LOC = auto()            # 1B deep

    LFLS_LOC = auto()           # Left field line shallow
    LFS_LOC = auto()            # Left field shallow
    LFCFS_LOC = auto()          # Left-Center Field Shallow
    CFS_LOC = auto()            # Center field shallow
    CFRFS_LOC = auto()          # Right-center field shallow
    RFS_LOC = auto()            # Right field shallow
    RFLS_LOC = auto()           # Right field line shallow

    LFL_LOC = auto()           # Left field line
    LF_LOC = auto()            # Left field
    LFCF_LOC = auto()          # Left-Center Field
    CF_LOC = auto()            # Center field
    CFRF_LOC = auto()          # Right-center field
    RF_LOC = auto()            # Right field
    RFL_LOC = auto()           # Right field line

    LFLD_LOC = auto()           # Left field line deep
    LFD_LOC = auto()            # Left field deep
    LFCFD_LOC = auto()          # Left-Center Field deep
    CFD_LOC = auto()            # Center field deep
    CFRFD_LOC = auto()          # Right-center field deep
    RFD_LOC = auto()            # Right field deep
    RFLD_LOC = auto()           # Right field line deep

    LFCFXD_LOC = auto()          # Left-Center Field extra deep
    CFXD_LOC = auto()            # Center field extra deep
    CFRFXD_LOC = auto()          # Right-center field extra deep
