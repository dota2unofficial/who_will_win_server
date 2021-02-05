from fastapi import APIRouter, Request, HTTPException, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from pony.orm import db_session, ObjectNotFound, desc

from ....core.models.players import Player
from .templates import templates
from ....libs.functions import add_battle_pass_exp
from ....libs.constants import (
    CONST_SUPPORTER_EXP_REWARD,
    CONST_SUPPORTER_GLORY_REWARD,
    CONST_SUPPORTER_FORTUNE_REWARD
)
from ....libs.actions import get_or_create_player
from ....libs.auth import http_auth

router = APIRouter()


@router.post('/supporters')
async def update_supporters_page(
    steam_id: int = Form(...),
    level: int = Form(...),
    comment: str = Form(...),
    user=Depends(http_auth)
):
    with db_session:
        db_player = get_or_create_player(steam_id)
        db_player.supporter_state = level
        db_player.supporter_comment = comment
        if db_player.supporter_state > 0:
            db_player.battlepass_glory += (
                CONST_SUPPORTER_GLORY_REWARD[db_player.supporter_state]
            )
            db_player.battlepass_fortune += (
                CONST_SUPPORTER_FORTUNE_REWARD[db_player.supporter_state]
            )
            add_battle_pass_exp(
                CONST_SUPPORTER_EXP_REWARD[db_player.supporter_state],
                db_player
            )
    return HTMLResponse(status_code=200)


@router.get('/supporters')
def get_supporters_page(request: Request, user=Depends(http_auth)):
    with db_session:
        manual_supporters = list(
            Player.select(
                lambda pl: pl.supporter_state > 0 and
                pl.supporter_enddate is None
            ).order_by(desc(Player.steam_id))
        )
        automatic_supporters = list(
            Player.select(
                lambda pl: pl.supporter_state > 0 and
                pl.supporter_enddate is not None
            )
        )
    return templates.TemplateResponse(
        'supporters/supporters.html',
        {
            'title': 'Supporters Editor',
            'request': request,
            'manual': manual_supporters,
            'automatic': automatic_supporters
        }
    )


@router.get('/remove_supporter')
async def remove_supporter(supporter_id: int, user=Depends(http_auth)):
    with db_session:
        try:
            db_player = Player[supporter_id]
        except ObjectNotFound:
            raise HTTPException(
                status_code=404,
                detail='This player id is not present in database!'
            )
        db_player.supporter_state = 0
        db_player.supporter_comment = ''
    return RedirectResponse(url='/admin/supporters')


@router.get('/add_supporter_reward')
async def add_monthly_reward(supporter_id: int, user=Depends(http_auth)):
    with db_session:
        try:
            db_player = Player[supporter_id]
        except ObjectNotFound:
            raise HTTPException(
                status_code=404,
                detail='This player id is not present in database!'
            )
        if db_player.supporter_state > 0:
            db_player.battlepass_glory += (
                CONST_SUPPORTER_GLORY_REWARD[db_player.supporter_state]
            )
            db_player.battlepass_fortune += (
                CONST_SUPPORTER_FORTUNE_REWARD[db_player.supporter_state]
            )
            add_battle_pass_exp(
                CONST_SUPPORTER_EXP_REWARD[db_player.supporter_state],
                db_player
            )
    return RedirectResponse(url='/admin/supporters')
