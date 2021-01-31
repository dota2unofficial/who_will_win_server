from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pony.orm import db_session

from ....libs.logging import logger
from ....libs.auth import lua_auth
from ....libs.constants import (
    MAP_NAMES,
    CONST_PLAYERS_PER_TEAM,
    CONST_DB_MAP_NAMES
)
from ....libs.functions import (
    get_bp_required_exp,
)
from ....core.schemas.matchs import BeforeMatchIn, AfterMatchPlayerBased
from ....core.schemas.players import PlayerBeforeMatch
from .manager import record_team_players_rating
from .actions import (
    process_incoming_players,
    get_players_achievements_batch,
    get_players_gift_codes_batch,
    get_supporter_info_dict,
    get_player_quests,
    get_leaderboards,
    get_achievements,
    get_quests,
    get_patch_notes
)


router = APIRouter()


@db_session
@router.post('/before')
async def before_match(data: BeforeMatchIn, auth=Depends(lua_auth)):
    current_date = datetime.utcnow()
    if data.map_name not in MAP_NAMES:
        raise HTTPException(
            status_code=403,
            detail=f'Map name <{data.map_name}> does not belong to us!'
        )

    players = process_incoming_players(data.players)
    players_dict = {
        steam_id: PlayerBeforeMatch.from_orm(
            player).dict() for steam_id, player in players.items()
    }
    resp_players = []
    steam_ids_int = [int(steam_id) for steam_id in data.players]

    achievements_batch = get_players_achievements_batch(steam_ids_int)
    gift_codes_batch = get_players_gift_codes_batch(steam_ids_int)

    for steam_id, player in players_dict.items():
        player['match_count'] = player.pop('match_count')
        bp_level = player.pop('battlepass_level')
        supporter_state = get_supporter_info_dict(
            player,
            current_date,
            players[steam_id]
        )
        supporter_level = supporter_state['level']
        player['supporter_state'] = supporter_state

        player['rating'] = {
            'ffa': player.pop('rating_ffa'),
            'duos': player.pop('rating_duos'),
            'squads': player.pop('rating_squads'),
        }

        player['achievements'] = achievements_batch.get(steam_id, [])
        player['quests'] = get_player_quests(steam_id, supporter_level)
        player['gift_codes'] = gift_codes_batch.get(steam_id, [])

        player['progress'] = {
            'level': bp_level,
            'glory': player.pop('battlepass_glory'),
            'current_exp': player.pop('battlepass_exp'),
            'required_exp': get_bp_required_exp(bp_level),
            'earned_exp': player.pop('battlepass_dailyexp'),
            'fortune': player.pop('battlepass_fortune'),
            'earned_fortune': player.pop('battlepass_dailyfortune')
        }

        resp_players.append(player)

    resp = {
        'players': resp_players,
        'leaderboards': get_leaderboards(),
        'achievements': get_achievements(),
        'quests': get_quests(),
        'patchnotes': get_patch_notes()
    }
    return resp


@db_session
@router.post('/after_match_player')
async def after_match_player(
    data: AfterMatchPlayerBased, auth=Depends(lua_auth)
):
    map_name = data.mapName
    if map_name not in CONST_PLAYERS_PER_TEAM:
        logger.info(f'Map name <{map_name}> does not belong to us!')
        raise HTTPException(
            status_code=403,
            detail=f'Map name <{map_name}> does not belong to us!'
        )
    rating_field_name = f'Rating_{CONST_DB_MAP_NAMES[map_name]}'

    players_steam_ids = []
    for player in data.team.players:
        if player.steamId != 0:
            players_steam_ids.append(player.steamId)
    with db_session:
        team_changes = record_team_players_rating(
            data, rating_field_name, players_steam_ids, map_name, data.isPvp
        )
    return {
        'players': {
            steam_id:
                {
                    'rating_change': {
                        m_key: val for m_key, val in changes['rating'].items()
                    },
                    'battlepass_change': {
                        m_key: val for (
                            m_key, val
                        ) in changes['battlepass'].items()
                    }
                 }
            for steam_id, changes in team_changes.items()
        }
    }


@router.post('/events')
async def match_events():
    return {'message': 'Hello world'}


@router.post('/update_settings')
async def update_player_setting():
    return {'message': 'Hello world'}


@router.post('/script_errors')
async def script_errors():
    return {'message': 'Hello world'}
