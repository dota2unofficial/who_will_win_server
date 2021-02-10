from typing import Final


MAP_NAMES: Final = [
    'ffa', 'duos', 'squads',
]

CONST_DB_MAP_NAMES: Final = {
    'ffa': 'ffa',
    'duos': 'duos',
    'squads': 'squads',
}

CONST_PLAYERS_PER_TEAM: Final = {
    'ffa': 1,
    'duos': 2,
    'squads': 4,
}

CONST_RATING_CHANGES: Final = {
    'ffa': [35, 30, 25, 15, 5, -5, -15, -20, -25, -30],
    'duos': [35, 25, 15, 0, -11, -21, -31],
    'squads': [30, 10, -10, -30],
}

CONST_EXP_CHANGES: Final = {
    'ffa': [250, 225, 200, 175, 150, 125, 100, 75, 50, 25],
    'duos': [250, 210, 170, 130, 90, 55, 25],
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
    'rating_ffa': 1500,
    'rating_duos': 1500,
    'rating_squads': 1500,
    'battlepass_exp': 0,
    'battlepass_glory': 0,
    'battlepass_level': 0,
    'battlepass_daily_exp': 0,
    'battlepass_fortune': 10,
    'battlepass_daily_fortune': 0,
    'match_count': 0,
}

# reduced by 1 to account for 'Win a game' unchangeable quest
CONST_QUESTS_COUNT: Final = {
    0: 1,
    1: 2,
    2: 3,
}

BP_MINIMAL_REQUIRED_EXP: Final = 1000
BP_REQUIRED_EXP_PER_LEVEL: Final = 100

CONST_FREE_SUPPORTER_GAMES: Final = 6

CURRENCY_CONVERSION_RATE = 4.58599

CONST_SUPPORTER_GLORY_REWARD: Final = {
    1: 300,
    2: 2000,
}

CONST_SUPPORTER_EXP_REWARD: Final = {
    1: 3000,
    2: 10000,
}

CONST_SUPPORTER_FORTUNE_REWARD: Final = {
    1: 15,
    2: 60
}


CONST_STAT_TYPES = {
    'abilities',
    'items',
    'battlepass',
    'innates',
    'rounds',
    'leaderboard',
    'sells',
    'match_count',
    'masteries',
}


CHANGELOG_URL = (
    'https://steamcommunity.com/sharedfiles/filedetails/changelog/2141071809'
)


MONTHS = {
    'english': {
        'Jan': 1,
        'Feb': 2,
        'Mar': 3,
        'Apr': 4,
        'May': 5,
        'Jul': 6,
        'Jun': 7,
        'Aug': 8,
        'Sep': 9,
        'Oct': 10,
        'Nov': 11,
        'Dec': 12,
    },
    'russian': {
        'янв': 1,
        'фев': 2,
        'мар': 3,
        'апр': 4,
        'мая': 5,
        'июл': 6,
        'июн': 7,
        'авг': 8,
        'сен': 9,
        'окт': 10,
        'ноя': 11,
        'дек': 12,
    },
    'schinese': {
        '1': 1,
        '2': 2,
        '3': 3,
        '4': 4,
        '5': 5,
        '6': 6,
        '7': 7,
        '8': 8,
        '9': 9,
        '10': 10,
        '11': 11,
        '12': 12,
    }
}


UPDATE_KEYWORDS = {
    'english': 'Update: ',
    'russian': 'Обновление: ',
    'schinese': '更新于：',
}


DELIMITER = {
    'english': ' @ ',
    'russian': ' в ',
    'schinese': ' ',
}


DATE_SPLITTER = {
    'english': ' ',
    'russian': ' ',
    'schinese': '月',
}
