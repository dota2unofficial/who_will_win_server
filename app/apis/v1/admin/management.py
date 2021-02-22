
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import RedirectResponse
from pony.orm import db_session

from ....libs.auth import http_auth
from ....libs.logging import logger
from ....libs.functions import (
    get_bp_levelup_reward,
    get_bp_levelup_fortune_reward,
    add_battle_pass_exp
)
from ....core.models.db import db
from ....core.models.inventory import PlayerInventory
from ....core.models.players import Player

router = APIRouter()


@router.get('/management/add_item')
async def add_player_item(
    steam_id: str,
    item_name: str,
    item_count=Query(default=1),
    inserted_gem=Query(default=None),
    user=Depends(http_auth)
):
    item_count = int(item_count) or 1
    logger.info(f'item_count: {item_count}, inserted_gem: {inserted_gem}')
    with db_session:
        if item := PlayerInventory.get(steam_id=steam_id, item_name=item_name):
            item.count += item_count
            if inserted_gem:
                item.inserted_gem = inserted_gem
        else:
            PlayerInventory(
                steam_id=steam_id,
                item_name=item_name,
                count=item_count,
                inserted_gem=inserted_gem
            )
    return RedirectResponse('/admin/player_management')


@router.get('/management/delete_item')
async def delete_player_item(
    steam_id: str,
    item_name: str,
    user=Depends(http_auth)
):
    with db_session:
        if item := PlayerInventory.get(steam_id=steam_id, item_name=item_name):
            item.delete()
    return RedirectResponse('/admin/player_management')


@router.get('/management/add_glory')
async def add_player_glory(
    steam_id: str,
    glory_amount: int,
    user=Depends(http_auth)
):
    if steam_id == '*':
        with db_session:
            db.execute("""
                update "Player"
                set "battlepass_glory" = "battlepass_glory" + $glory_amount
            """.strip())
        return RedirectResponse("/admin/player_management")

    with db_session:
        if player := Player.get(steam_id=steam_id):
            player.battlepass_glory += glory_amount
    return RedirectResponse('/admin/player_management')


@router.get('/management/set_glory')
async def set_player_glory(
    steam_id: str,
    glory_amount: int,
    user=Depends(http_auth)
):
    with db_session:
        if player := Player.get(steam_id=steam_id):
            player.battlepass_glory = glory_amount
    return RedirectResponse('/admin/player_management')


@router.get('/management/add_level')
async def add_player_level(
    steam_id: str,
    level_amount: int,
    user=Depends(http_auth)
):
    if steam_id == '*':
        with db_session:
            db.execute("""
                update "Player"
                set "battlepass_level" = "battlepass_level" + $level_amount
            """.strip())
        return RedirectResponse('/admin/player_management')
    with db_session:
        if player := Player.get(steam_id=steam_id):
            if level_amount < 0:
                raise HTTPException(
                    status_code=400,
                    detail="Can't add negative level, use set"
                )
            logger.info(f"Initial level {player.battlepass_level}")
            for level in range(
                player.battlepass_level,
                player.battlepass_level + level_amount
            ):
                logger.info(f'Added glory for added level {level}')
                player.battlepass_glory += get_bp_levelup_reward(level)
                player.battlepass_fortune += get_bp_levelup_fortune_reward(
                    level
                )
            player.battlepass_level += level_amount
    return RedirectResponse('/admin/player_management')


@router.get('/management/set_level')
async def set_player_level(
    steam_id: str,
    level_amount: int,
    user=Depends(http_auth)
):
    with db_session:
        if player := Player.get(steam_id=steam_id):
            player.battlepass_level = level_amount
    return RedirectResponse('/admin/player_management')


@router.get('/management/add_exp')
async def add_player_exp(
    steam_id: str,
    exp_amount: int,
    user=Depends(http_auth)
):
    if steam_id == '*':
        with db_session:
            db.execute("""
               update "Player"
               set "battlepass_exp" = "battlepass_exp" + $exp_amount
            """.strip())
        return RedirectResponse('/admin/player_management')

    with db_session:
        if player := Player.get(steam_id=steam_id):
            add_battle_pass_exp(exp_amount, player)
    return RedirectResponse("/admin/player_management")


@router.get('/management/set_daily_exp')
async def set_daily_exp(
    steam_id: str,
    daily_exp_amount: int,
    user=Depends(http_auth)
):
    with db_session:
        if player := Player.get(steam_id=steam_id):
            player.battlepass_daily_exp = daily_exp_amount
    return RedirectResponse('/admin/player_management')


@router.get('/management/add_fortune')
async def add_fortune(
    steam_id: str,
    fortune_amount: int,
    user=Depends(http_auth)
):
    if steam_id == '*':
        with db_session:
            db.execute("""
               update "Player"
               set "battlepass_fortune" = (
                   "battlepass_fortune" + $fortune_amount
               )
            """.strip())
        return RedirectResponse('/admin/player_management')

    with db_session:
        if player := Player.get(steam_id=steam_id):
            player.battlepass_fortune += fortune_amount
    return RedirectResponse('/admin/player_management')


@router.get('/management/set_fortune')
async def set_fortune(
    steam_id: str,
    fortune_amount: int,
    user=Depends(http_auth)
):
    if steam_id == '*':
        with db_session:
            db.execute("""
               update "Player"
               set "battlepass_fortune" = $fortune_amount
            """.strip())
        return RedirectResponse('/admin/player_management')

    with db_session:
        if player := Player.get(steam_id=steam_id):
            player.battlepass_fortune = fortune_amount
    return RedirectResponse('/admin/player_management')


@router.get('/management/set_daily_fortune')
async def set_daily_fortune(
    steam_id: str,
    daily_fortune_amount: int,
    user=Depends(http_auth)
):
    if steam_id == '*':
        with db_session:
            db.execute("""
               update "Player"
               set "battlepass_daily_fortune" = $daily_fortune_amount
            """.strip())
        return RedirectResponse('/admin/player_management')

    with db_session:
        if player := Player.get(steam_id=steam_id):
            player.battlepass_daily_fortune = daily_fortune_amount
    return RedirectResponse('/admin/player_management')
