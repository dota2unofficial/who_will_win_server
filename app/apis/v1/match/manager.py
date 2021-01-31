from typing import List
from datetime import datetime

from pony.orm import delete
from pony.orm.core import MultipleObjectsFoundError

from ....libs.logging import logger
from ....libs.constants import (
    CONST_RATING_CHANGES,
    CONST_DB_MAP_NAMES,
    CONST_EXP_CHANGES,
    CONST_EXP_MULTIPLIER,
    CONST_EXP_DAILY_LIMIT,
    CONST_FORTUNE_GAME_REWARD,
    CONST_FORTUNE_DAILY_LIMIT
)
from ....libs.functions import clamp
from ....libs.functions import (
    get_bp_pve_exp,
    get_bp_required_exp,
    get_bp_levelup_reward,
    get_bp_levelup_fortune_reward
)
from ....core.schemas.matchs import AfterMatchPlayerBased, AfterMatchTeam
from ....core.models.matchs import Match, MatchTeam
from ....core.models.players import Player, MatchPlayer
from .actions import process_incoming_players


def calculate_new_rating(old_rating, map_name, index, average_rating):
    base_change = CONST_RATING_CHANGES[map_name][index]
    correction_change = round((average_rating - old_rating) * 0.02)
    expected_change = base_change + clamp(correction_change, -20, 20)
    return max(old_rating + expected_change, 1)


def record_best_time(
    team: AfterMatchTeam, team_players, map_name, is_pvp: bool
):
    db_map_name = CONST_DB_MAP_NAMES[map_name]
    mode = f"BestPv{'P' if is_pvp else 'E'}"
    # set new best rounds / times
    for player in team.players:
        db_player = team_players[player.steam_id]
        old_round = getattr(db_player, f"{mode}_{db_map_name}_round") or 0
        # if player set new round record
        if team.round > old_round:
            setattr(db_player, f"{mode}_{db_map_name}_round", team.round)
            setattr(db_player, f"{mode}_{db_map_name}_time", team.time)
        # or if he's on same round but with better time
        elif team.round == old_round:
            old_time = getattr(db_player, f"{mode}_{db_map_name}_time") or 0
            if team.time > old_time or old_time == 0:
                setattr(db_player, f"{mode}_{db_map_name}_round", team.round)
                setattr(db_player, f"{mode}_{db_map_name}_time", team.time)


def set_battle_pass_exp(new_exp: int, db_player: Player):
    """ REQUIRES PRESENT DB SESSION """
    # logger.info(f"<{db_player.steamId}> Set battle exp: {new_exp}")
    required_exp = get_bp_required_exp(db_player.battlepass_level)
    while new_exp >= required_exp:
        # logger.info(f"[Level up]: {new_exp}/{required_exp}")
        db_player.battlepass_exp = new_exp - required_exp
        db_player.battlepass_level += 1
        glory_reward = get_bp_levelup_reward(db_player.battlepass_level)
        db_player.battlepass_glory += glory_reward
        db_player.battlepass_fortune += get_bp_levelup_fortune_reward(
            db_player.battlepass_level
        )
        new_exp -= required_exp
        required_exp = get_bp_required_exp(db_player.battlepass_level)

    # logger.info(f"Set {new_exp}")
    db_player.battlepass_exp = new_exp


def record_battle_pass_progress(
    team: AfterMatchTeam,
    team_players,
    map_name: str,
    team_index: int,
    is_pvp: bool
) -> dict:
    bp_changes = {}
    for player in team.players:
        bp_changes[player.steam_id] = {
            'level': {},
            'exp': {},
            'glory': {},
            'fortune': {},
        }
        db_player: Player = team_players[player.steam_id]
        if is_pvp:
            added_exp = (
                CONST_EXP_CHANGES[map_name][team_index] *
                CONST_EXP_MULTIPLIER[db_player.supporter_state]
            )
        else:
            added_exp = (
                get_bp_pve_exp(team.round) *
                CONST_EXP_MULTIPLIER[db_player.supporter_state]
            )

        daily_exp_limit = CONST_EXP_DAILY_LIMIT[db_player.supporter_state]

        if added_exp + db_player.battlepass_daily_exp > daily_exp_limit:
            added_exp = max(
                daily_exp_limit - db_player.battlepass_daily_exp, 0
            )

        daily_fortune_limit = (
            CONST_FORTUNE_DAILY_LIMIT[db_player.supporter_state]
        )
        added_fortune = (
            CONST_FORTUNE_GAME_REWARD if not player.early_leaver else 0
        )

        if (
            (added_fortune + db_player.battlepass_daily_fortune) >
            daily_fortune_limit
        ):
            added_fortune = max(
                daily_fortune_limit - db_player.battlepass_daily_fortune, 0
            )

        new_exp = db_player.battlepass_exp + added_exp
        # add glory if leveled up
        player_bp_changes = bp_changes[player.steam_id]

        player_bp_changes['level']['old'] = db_player.battlepass_level
        player_bp_changes['exp']['old'] = db_player.battlepass_exp
        player_bp_changes['glory']['old'] = db_player.battlepass_glory
        player_bp_changes['fortune']['old'] = db_player.battlepass_fortune

        player_bp_changes['exp']['change'] = added_exp
        player_bp_changes['fortune']['change'] = added_fortune
        player_bp_changes['glory']['change'] = 0

        set_battle_pass_exp(new_exp, db_player)
        db_player.battlepass_fortune += added_fortune
        db_player.battlepass_daily_fortune += added_fortune
        db_player.battlepass_daily_exp += added_exp
        player_bp_changes['glory']['change'] = (
            db_player.battlepass_glory - player_bp_changes['glory']['old']
        )

        player_bp_changes['level']['new'] = db_player.battlepass_level
        player_bp_changes['exp']['new'] = db_player.battlepass_exp
        player_bp_changes['exp']['levelup_requirement'] = get_bp_required_exp(
            db_player.battlepass_level
        )
        player_bp_changes['exp']['daily_exp_current'] = (
            db_player.battlepass_daily_exp
        )
        player_bp_changes['exp']['daily_exp_limit'] = daily_exp_limit
        player_bp_changes['glory']['new'] = db_player.battlepass_glory

        player_bp_changes['fortune']['new'] = db_player.battlepass_fortune
        player_bp_changes['fortune']['daily_fortune_current'] = (
            db_player.battlepass_daily_fortune
        )
        player_bp_changes['fortune']['daily_fortune_limit'] = (
            daily_fortune_limit
        )

    return bp_changes


def record_team_players_rating(
    data: AfterMatchPlayerBased,
    rating_field_name: str,
    players_steam_ids: List[str],
    map_name: str,
    is_pvp: bool
):
    team = data.team
    players = process_incoming_players(players_steam_ids)
    match_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")
    round_number = team.round
    # logger.info(f"Recording match id {data.matchId}")

    try:
        match = Match.get(match_id=data.match_id)
    except MultipleObjectsFoundError:
        logger.info(f'Multiple records of match id <{data.match_id}> ' +
                    'were found. Removing all of them and starting over.')
        delete(m for m in Match if m.match_id == data.match_id)
        logger.info("Successfully deleted old entries")
        match = None

    if not match:
        Match(match_id=data.match_id, map_name=map_name, ended_at=match_time)
    else:
        match.ended_at = match_time

    match_team = MatchTeam.get(match_id=data.match_id, team_id=team.team_id)
    if not match_team:
        MatchTeam(
            match_id=data.match_id,
            team_id=team.team_id,
            time=team.time,
            round=round_number
        )
    else:
        match_team.time = team.time
        match_team.round = round_number

    players_changes = {}
    match_players = {}
    for player in team.players:
        # if player.steamId == "0":  # not counting bots in!
        #    continue
        db_player = players[player.steam_id]

        db_player.match_count += 1

        other_avg_mmr = player.other_players_AvgMMR or team.other_teams_AvgMMR
        players_changes[player.steamId] = {}
        old_rating = getattr(db_player, rating_field_name)
        # mmr is changed only in pvp
        new_rating = calculate_new_rating(
            old_rating, map_name, team.match_place, other_avg_mmr
        ) if is_pvp else old_rating
        match_player = MatchPlayer(
            match_id=data.match_id,
            player_id=player.player_id,
            steam_id=player.steam_id,
            team_id=team.team_id,
            rating_change_new=new_rating if is_pvp else old_rating,
            rating_change_old=old_rating,
        )
        players_changes[player.steam_id]['rating'] = {
            'new': new_rating if is_pvp else old_rating,
            'old': old_rating
        }
        if player.innate:
            match_player.innate = player.innate
        if player.round_deaths:
            match_player.round_deaths = [
                rd.dict() for rd in player.round_deaths
            ]
        else:
            match_player.round_deaths = []
        if player.items:
            match_player.items = [
                str(item) for item in player.items if item is not None
            ]
        if player.abilities:
            match_player.abilities = player.abilities
        if player.mastery:
            match_player.mastery = player.mastery
        if is_pvp and match_player.steam_id != 0:
            setattr(
                Player.get(steam_id=match_player.steam_id),
                rating_field_name,
                new_rating
            )
        match_players[player.steam_id] = match_player
    record_best_time(data.team, players, map_name, is_pvp)
    bp_changes = record_battle_pass_progress(
        data.team, players, map_name, team.match_place, is_pvp
    )
    for steam_id, changes in bp_changes.items():
        # if steam_id == "0":  # not counting bots in!
        #    continue
        players_changes[steam_id]["battlepass"] = changes
        match_players[steam_id].battlepass_expreward = changes["exp"]["change"]
        match_players[steam_id].battlepass_gloryreward = (
            changes["glory"]["change"]
        )
    return players_changes
