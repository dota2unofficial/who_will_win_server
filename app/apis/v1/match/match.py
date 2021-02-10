from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response
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
from ....core.schemas.matchs import (
    BeforeMatchIn,
    AfterMatchPlayerBased,
    AfterMatchPlayerBasedUpdate,
    PollEventsIn,
    UpdateSettingsIn,
    ScriptErrorIn
)
from ....core.schemas.players import PlayerBeforeMatch
from ....core.models.matchs import MatchTeam, MatchEvent, ScriptError
from ....core.models.players import MatchPlayer
from .manager import record_team_players_rating, record_best_time
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
    with db_session:
        players = process_incoming_players(data.players)
        players_dict = {
            steam_id: PlayerBeforeMatch.from_orm(player).dict() for (
                steam_id, player
            ) in players.items()
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
                'earned_exp': player.pop('battlepass_daily_exp'),
                'fortune': player.pop('battlepass_fortune'),
                'earned_fortune': player.pop('battlepass_daily_fortune')
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


@db_session
@router.post('/set_match_player_round_data')
def set_match_player_round_data(
    data: AfterMatchPlayerBasedUpdate,
    auth=Depends(lua_auth)
):

    match_team = MatchTeam.get(
        match_id=data.match_id,
        team_id=data.team.team_id
    )
    if not match_team:
        return Response(
            status_code=404,
            content=(f'MatchTeam with team_id<{data.team.team_id}> '
                     f"and match_id<{data.match_id} doesn't exist>")
        )
    match_team.time = data.team.time
    match_team.round = data.team.round
    players_steam_ids = []
    for player in data.team.players:
        if player.steam_id != 0:
            players_steam_ids.append(player.steam_id)
    players = process_incoming_players(players_steam_ids)
    record_best_time(data.team, players, data.map_name, True)

    match_players = MatchPlayer.select(
        lambda mp: mp.match_id == data.match_id and
        mp.team_id == data.team.team_id
    )
    match_players = {str(mp.steam_id): mp for mp in match_players}

    for player in data.team.players:
        db_player = match_players.get(player.steam_id, None)
        if not db_player:
            continue
        if player.innate:
            db_player.innate = player.innate
        if player.round_deaths:
            db_player.round_deaths = [rd.dict() for rd in player.round_deaths]
        else:
            db_player.round_deaths = []
        if player.items:
            db_player.items = (
                [str(item) for item in player.items if item is not None]
            )
        if player.abilities:
            db_player.abilities = player.abilities
        if player.mastery:
            db_player.mastery = player.mastery


@db_session
@router.post('/events')
async def poll_events(data: PollEventsIn, auth=Depends(lua_auth)):
    response = []
    events_query = MatchEvent.select(lambda me: me.match_id == data.match_id)
    events = list(events_query)
    if events:
        logger.info(f'Got following events fetched: {events}')
    for event in events:
        logger.info(f'converting and deleting event: {event}')
        response.append(event.to_dict()['Body'])
    events_query.delete(bulk=True)
    return response


@db_session
@router.post('/update_settings')
async def update_players_settings(
    data: UpdateSettingsIn, auth=Depends(lua_auth)
):
    steam_ids = [player.steam_id for player in data.players]
    players_settings_dict = {
        int(player.steam_id): player.settings for player in data.players
    }
    players = process_incoming_players(steam_ids)
    for player in players.values():
        player.settings = players_settings_dict[player.steam_id]
    return Response(status_code=200)


@db_session
@router.post('/script_errors')
async def script_error_report(data: ScriptErrorIn, auth=Depends(lua_auth)):
    for stack, error_count in data.errors.items():
        existing_error = ScriptError.get(stack=stack, match_id=data.match_id)
        if not existing_error:
            ScriptError(stack=stack, match_id=data.match_id, count=error_count)
        else:
            existing_error.count += error_count

    return Response(status_code=200)
