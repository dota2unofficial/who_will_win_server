from typing import Optional

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from orjson import loads
from pony.orm import db_session, desc

from .templates import templates
from ....libs.actions import get_quests
from ....libs.auth import http_auth
from ....core.models.db import db
from ....core.models.quests import Quests, PlayerQuests

router = APIRouter()


@router.get('/admin/quests', response_class=HTMLResponse)
async def get_quests_page(request: Request, user=Depends(http_auth)):
    quests = get_quests(create_session=True)
    return templates.TemplateResponse(
        'quests/quests.html',
        {
            'title': 'Quests Editor',
            'request': request,
            'quests': quests
        }
    )


@router.post('/quests')
async def update_quests_page(request: Request, user=Depends(http_auth)):
    data = await request.json()
    with db_session:
        for quests_id, new_values in data.items():
            Quests[int(quests_id)].set(**new_values)
    return HTMLResponse(status_code=200)


@router.get('/add_quest')
async def add_quest(
    quest_name: str,
    quest_type: str,
    quest_reward: str,
    quest_description: Optional[str] = None,
    user=Depends(http_auth)
):
    with db_session:
        new_quest = Quests(
            name=quest_name,
            type=quest_type,
            reward=loads(quest_reward)
        )
        if quest_description:
            new_quest.description = loads(quest_description)
    return RedirectResponse(url='/admin/quests')


@router.get('/admin/remove_quest')
async def remove_quest(quest_id: int, user=Depends(http_auth)):
    with db_session:
        Quests[quest_id].delete()
    return RedirectResponse(url='/admin/quests')


@router.post('/reset_daily_quests')
async def reset_daily_quests(user=Depends(http_auth)):
    with db_session:
        db.execute("""
            select replace_player_quests();
        """.strip())
        return [
            item.to_dict() for item in list(
                PlayerQuests.select().order_by(desc(PlayerQuests.steam_id))
            )
        ]
