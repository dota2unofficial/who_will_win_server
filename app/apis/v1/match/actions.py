from typing import List
from datetime import datetime

from pony.orm import select, desc

from ....libs.constants import (
    DEFAULT_PLAYER_VALUES,
    CONST_QUESTS_COUNT,
    CONST_DB_MAP_NAMES
)
from ....libs.logging import logger
from ....libs.utils import (
    optional_session,
    batch_postprocessing,
    result_keys_lower_decorator
)
from ....libs.functions import steam_id_to_str
from ....core.schemas.matchs import Leaderboards
from ....core.models.db import db
from ....core.models.players import Player
from ....core.models.achievements import Achievements, PlayerAchievements
from ....core.models.payments import GiftCodes
from ....core.models.quests import Quests, PlayerQuests
from ....core.models.patchnotes import Patchnotes


@optional_session
def process_incoming_players(
    steam_ids: List[str], key_type=str, **kwargs
) -> dict:
    steam_ids_as_int = [int(steam_id) for steam_id in steam_ids]
    players = list(Player.select(lambda p: p.steam_id in steam_ids_as_int))
    present_steam_ids = [player.steam_id for player in players]
    # insert new players, excluding bots
    for steam_id in steam_ids_as_int:
        if steam_id == 0:
            pass  # continue
        if steam_id not in present_steam_ids:
            # print("inserting new steam_id: ", steam_id)
            added_player = Player(
                steam_id=steam_id, settings="{}", supporter_state=0,
                **DEFAULT_PLAYER_VALUES
            )
            players.append(added_player)
    ret_players = {key_type(player.steam_id): player for player in players}
    return ret_players


@optional_session
def get_supporter_info_dict(
    player: dict, current_date: datetime, db_player: Player
) -> dict:
    # since supporter level influences some other values,
    #  we need to set it to actual value
    # accounting free games for new players
    level = player.pop('supporter_state')
    end_date = player.pop('supporter_enddate')
    if end_date and end_date < current_date:
        logger.info(f"Player {player['steam_id']} supporter expired!")
        db_player.supporter_state = 0
        db_player.supporter_enddate = None
        level = 0
        end_date = None
    return {
        'level': level,
        'endDate': end_date
    }


@batch_postprocessing
def get_players_achievements_batch(steam_ids: List[int]):
    achievements = list(
        PlayerAchievements.select(lambda ach: ach.steam_id in steam_ids)
    )
    return [ach.to_dict() for ach in achievements]


@batch_postprocessing
def get_players_gift_codes_batch(steam_ids: List[int]):
    gift_codes = list(GiftCodes.select(lambda gc: gc.steam_id in steam_ids))
    return [gc.to_dict() for gc in gift_codes]


@optional_session
@result_keys_lower_decorator
def get_player_quests(steam_id: int, supporter_level: int):
    quest_count = CONST_QUESTS_COUNT.get(supporter_level, 2)
    player_quests = list(
        PlayerQuests.select(lambda pq: pq.steam_id == steam_id)[:quest_count]
    )
    present_quest_ids = [pq.quest_id for pq in player_quests]
    player_quest_count = len(player_quests)

    count_diff = quest_count - player_quest_count
    if count_diff <= 0:
        return [steam_id_to_str(pq.to_dict()) for pq in player_quests]
    # if needed quest count was bigger then player quest count
    #  we need to roll more quests
    try:
        new_quest_ids = iter(list(select(
            q.id for q in Quests if q.id not in present_quest_ids
        ).random(count_diff)))

        for _ in range(count_diff):
            new_quest = PlayerQuests(
                steam_id=steam_id,
                quest_id=next(new_quest_ids),
                added_at=datetime.utcnow(),
                progress=0,
            )
            player_quests.append(new_quest)
    except StopIteration:
        return [steam_id_to_str(pq.to_dict()) for pq in player_quests]
    return [steam_id_to_str(pq.to_dict()) for pq in player_quests]


@optional_session
def get_leaderboards(*args):
    leaderboards = {
        'bestPvE': {
            'ffa': [],
            'duos': [],
            'squads': [],
        },
        'bestPvP': {
            'ffa': [],
            'duos': [],
            'squads': [],
        },
        'rating': {
            'ffa': [],
            'duos': [],
            'squads': [],
        }
    }

    for lb_type, lb_maps in leaderboards.items():
        for lb_map in lb_maps.keys():
            db_map_name = CONST_DB_MAP_NAMES[lb_map]
            main_field_name = f'{lb_type}_{db_map_name}'  # e.g. rating_ffa
            main_field_name = main_field_name[0].upper() + main_field_name[1:]

            # every field needs a '' because it's uppercase
            #  and postgres treats names as lowercase without quotes
            if lb_type == 'rating':
                field_filter_name = f'"{main_field_name}"'
                s_args = f'"steam_id", "{main_field_name}"'
                order_str = f'"{main_field_name}"'
            else:
                field_filter_name = f'"{main_field_name}_round"'
                s_args = (f'"steam_id", "{main_field_name}_round", ' +
                          f'"{main_field_name}_time"')
                order_str = f'"{main_field_name}_round"'

            # since we have a lot of types for lb, orm is not nearly as
            #  powerful and nice as this string expr
            # someone will probably say it's ass, but as if i cared lol

            select_str = (f'select {s_args} from "Player" ' +
                          f'where {field_filter_name} is not null ' +
                          f'order by {order_str} desc limit 50')
            lb_maps[lb_map] = list(db.select(select_str))

            for index, entry in enumerate(leaderboards[lb_type][lb_map]):
                leaderboards[lb_type][lb_map][index] = {
                    "steam_id": str(entry[0]),
                }
                if lb_type == "rating":
                    leaderboards[lb_type][lb_map][index]["rating"] = entry[1]
                else:
                    leaderboards[lb_type][lb_map][index]["round"] = entry[1]
                    leaderboards[lb_type][lb_map][index]["time"] = entry[2]

    return Leaderboards(**leaderboards)


@optional_session
@result_keys_lower_decorator
def get_achievements():
    return [row.to_dict() for row in list(select(ach for ach in Achievements))]


@optional_session
@result_keys_lower_decorator
def get_quests():
    return [row.to_dict() for row in list(select(q for q in Quests))]


@optional_session
def get_patch_notes():
    patch_notes = list(Patchnotes.select().order_by(desc(Patchnotes.date)))
    return {
        str(pn.date): {
            'russian': pn.content_russian,
            'english': pn.content_english,
            'chinese': pn.content_chinese,
        } for pn in patch_notes
    }
