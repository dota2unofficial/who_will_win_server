from typing import Final


MAP_NAMES: Final = [
    "ffa", "duos", "squads",
]

CONST_DB_MAP_NAMES: Final = {
    "ffa": "FFA",
    "duos": "Duos",
    "squads": "Squads",
}

CONST_PLAYERS_PER_TEAM: Final = {
    "ffa": 1,
    "duos": 2,
    "squads": 4,
}

CONST_RATING_CHANGES: Final = {
    "ffa": [35, 30, 25, 15, 5, -5, -15, -20, -25, -30],
    "duos": [35, 25, 15, 0, -11, -21, -31],
    "squads": [30, 10, -10, -30],
}

CONST_EXP_CHANGES: Final = {
    "ffa": [250, 225, 200, 175, 150, 125, 100, 75, 50, 25],
    "duos": [250, 210, 170, 130, 90, 55, 25],
}

CONST_EXP_MULTIPLIER: Final = {
    0: 1,
    1: 2,
    2: 4
}

CONST_EXP_DAILY_LIMIT: Final = {
    0: 2000,
    1: 4000,
    2: 8000
}


CONST_FORTUNE_GAME_REWARD: Final = 1

CONST_FORTUNE_DAILY_LIMIT: Final = {
    0: 1,
    1: 1,
    2: 1
}

CONST_PVE_BOSS_MULTIPLIER: Final = 5

CONST_PVE_ROUND_EXP: Final = {
    0: 0,
    1: 2,
    2: 4,
}

DEFAULT_PLAYER_VALUES: Final = {
    "Rating_FFA": 1500,
    "Rating_Duos": 1500,
    "Rating_Squads": 1500,
    "BattlePass_Exp": 0,
    "BattlePass_Glory": 0,
    "BattlePass_Level": 0,
    "BattlePass_DailyExp": 0,
    "BattlePass_Fortune": 10,
    "BattlePass_DailyFortune": 0,
    "MatchCount": 0,
}

# reduced by 1 to account for "Win a game" unchangeable quest
CONST_QUESTS_COUNT: Final = {
    0: 1,
    1: 2,
    2: 3,
}

BP_MINIMAL_REQUIRED_EXP: Final = 1000
BP_REQUIRED_EXP_PER_LEVEL: Final = 100

CONST_FREE_SUPPORTER_GAMES: Final = 6
