import math


from .constants import (
    BP_MINIMAL_REQUIRED_EXP,
    BP_REQUIRED_EXP_PER_LEVEL,
    CONST_PVE_BOSS_MULTIPLIER,
    CONST_PVE_ROUND_EXP
)


def steam_id_to_str(obj: dict):
    for key, val in obj.items():
        if key in ('SteamId', 'steam_id', 'steamId',):
            obj[key] = str(val)
        if type(val) == dict:
            steam_id_to_str(val)
    return obj


def get_bp_required_exp(level: int) -> int:
    if level <= 25:
        return max(BP_MINIMAL_REQUIRED_EXP, level * BP_REQUIRED_EXP_PER_LEVEL)
    else:
        return min(25 * BP_REQUIRED_EXP_PER_LEVEL + 500 * (level - 25), 10000)


def clamp(value, min_v, max_v):
    return max(min(value, max_v), min_v)


def get_bp_pve_exp(finished_round: int) -> int:
    if finished_round <= 20:
        return finished_round * CONST_PVE_ROUND_EXP[0]
    else:
        mid_rounds = min(finished_round - 20, 30)
        end_rounds = max(finished_round - 50, 0)

        midgame_rounds_exp = mid_rounds * CONST_PVE_ROUND_EXP[1]
        endgame_rounds_exp = end_rounds * CONST_PVE_ROUND_EXP[2]

        # bosses every 10th wave
        midgame_bosses_count = divmod(mid_rounds, 10)[0]
        endgame_bosses_count = divmod(end_rounds, 10)[0]
        # effectively, we are replacing exp rewards for boss rounds
        #  from default to boss-multiplied
        midgame_bosses_exp = (
            midgame_bosses_count *
            CONST_PVE_ROUND_EXP[1] * CONST_PVE_BOSS_MULTIPLIER
        )
        endgame_bosses_exp = (
            endgame_bosses_count *
            CONST_PVE_ROUND_EXP[2] * CONST_PVE_BOSS_MULTIPLIER
        )

        midgame_rounds_exp -= midgame_bosses_count * CONST_PVE_ROUND_EXP[1]
        endgame_bosses_exp -= endgame_bosses_count * CONST_PVE_ROUND_EXP[2]

        return (
            midgame_rounds_exp + endgame_rounds_exp +
            midgame_bosses_exp + endgame_bosses_exp
        )


def get_bp_levelup_reward(level: int) -> int:
    level = min(level, 100)
    reward = 50 + 5 * math.floor(level / 10)
    if level % 5 == 0:
        return reward * 2
    return reward


def get_bp_levelup_fortune_reward(level: int) -> int:
    return 1
