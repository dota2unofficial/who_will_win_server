from fastapi import APIRouter, Request, Depends
from pony.orm import db_session
from orjson import loads

from ....libs.auth import http_auth
from ....libs.actions import get_or_create_player
from ....libs.functions import http_get, get_bp_required_exp
from ....core.models.db import db
from ....core.settings import settings
from ....core.models.inventory import PlayerInventory
from ....core.models.payments import ItemSellingHistory
from ....core.models.quests import PlayerQuests
from ....core.models.achievements import PlayerAchievements
from .templates import templates

router = APIRouter()


@router.get('/player_management')
async def get_player_management_page(
    request: Request,
    user=Depends(http_auth)
):
    return templates.TemplateResponse(
        'players/player_management.html',
        {
            'title': 'Player Management',
            'request': request
        }
    )


@router.get('/players/{steam_id}')
async def get_player_profile(request: Request, steam_id: int):
    with db_session:
        player = get_or_create_player(steam_id)

        player_matches = []
        db_matches = db.select("""
            select
                MP."match_id",
                "ended_at",
                "map_name",
                "rating_change_new",
                "rating_change_old",
                "abilities",
                "innate",
                "round_deaths",
                "items",
                "battlepass_expreward",
                "battlepass_gloryreward",
                "mastery"
            from "Match"
            join "MatchPlayer" MP on "Match"."match_id" = MP."match_id"
            where MP."steam_id" = $steam_id
            order by "Match"."ended_at" desc
            limit 10
        """.strip())
        for match in db_matches:
            m_match = []
            for i, item in enumerate(match):
                if i == 7:
                    m_match.append(loads(item))
                else:
                    m_match.append(item)
            player_matches.append(m_match)

        steam_key = settings.STEAM_WEBAPI_KEY
        steam_profile_data = await http_get(
            f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/'
            f'?key={steam_key}&steamids={steam_id}'
        )

        profile_avatar_link, profile_name = None, None
        if steam_profile_data:
            steam_profile_data = steam_profile_data["response"]["players"][0]
            profile_avatar_link = steam_profile_data["avatarmedium"]
            profile_name = steam_profile_data["personaname"]

        data = {
            'player': player,
            'exp_required': get_bp_required_exp(player.battlepass_level),
            'matches': player_matches,
            'profile_link': profile_avatar_link,
            'profile_name': profile_name,
            'items': list(
                PlayerInventory.select(
                    lambda pi: pi.steam_id == steam_id
                ).order_by(PlayerInventory.item_name)
            ),
            'purchases': list(
                ItemSellingHistory.select(lambda sh: sh.steam_id == steam_id)
            ),
            # 'masteries': list(
            #     PlayerMasteries.select(
            #         lambda pm: pm.SteamId == steam_id
            #     ).order_by(
            #         PlayerMasteries.MasteryName,
            #         PlayerMasteries.MasteryLevel
            #     )
            # ),
            'quests': list(
                PlayerQuests.select(lambda pq: pq.steam_id == steam_id)
            ),
            'achievements': list(
                PlayerAchievements.select(lambda pa: pa.steam_id == steam_id)
            ),
        }

        return templates.TemplateResponse(
            'players/player_profile.html',
            {
                'title': 'Player Profile',
                'request': request,
                'steam_id': steam_id,
                **data
            }
        )
