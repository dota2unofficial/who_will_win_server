from typing import Optional

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from orjson import loads
from pony.orm import db_session

from .templates import templates
from ....libs.auth import http_auth
from ..match.actions import get_achievements
from ....core.models.achievements import Achievements

router = APIRouter()


@router.get('/achievements', response_class=HTMLResponse)
async def get_achievements_page(request: Request, user=Depends(http_auth)):
    achievements = get_achievements(create_session=True)
    return templates.TemplateResponse(
        'achievements/achievements.html',
        {
            'title': 'Achievements Editor',
            'request': request,
            'achievements': achievements
        }
    )


@router.post('/achievements')
async def update_achievements_page(request: Request, user=Depends(http_auth)):
    data = await request.json()
    with db_session:
        for achievement_id, new_values in data.items():
            Achievements[int(achievement_id)].set(**new_values)
    return HTMLResponse(status_code=200)


@router.get('/add_achievement')
async def add_achievement(
    achievement_name: str,
    achievement_type: str,
    achievement_reward: str,
    achievement_description: Optional[str] = None,
    user=Depends(http_auth)
):
    with db_session:
        new_achievement = Achievements(
            name=achievement_name,
            type=achievement_type,
            reward=loads(achievement_reward)
        )
        if achievement_description:
            new_achievement.description = loads(achievement_description)
    return RedirectResponse(url='/admin/achievements')


@router.get('/remove_achievement')
async def remove_achievement(achievement_id: int, user=Depends(http_auth)):
    with db_session:
        Achievements[achievement_id].delete()
    return RedirectResponse(url='/admin/achievements')
