from datetime import datetime

from pony.orm import Required, Optional, Json, StrArray

from .db import db


class Player(db.Entity):
    _table_ = 'Player'

    steam_id = Required(
        int,
        size=64,
        column='steam_id'
    )
    settings = Optional(
        Json, column='settings'
    )
    rating_ffa = Optional(
        int,
        column='rating_ffa'
    )
    rating_duos = Optional(
        int,
        column='rating_duos'
    )
    rating_squads = Optional(
        int,
        column='rating_squads'
    )

    supporter_enddate = Optional(
        datetime,
        sql_type='timestamp',
        column='supporter_enddate'
    )
    supporter_state = Required(
        int,
        size=16,
        column='supporter_state',
        sql_default=0
    )
    supporter_comment = Optional(
        str,
        sql_type='text',
        column='supporter_comment'
    )

    battlepass_level = Optional(
        int,
        sql_default=0,
        column='battlepass_level'
    )
    battlepass_glory = Optional(
        int,
        sql_default=0,
        column='battlepass_glory'
    )

    battlepass_exp = Optional(
        int,
        sql_default=0,
        column='battlepass_exp'
    )
    battlepass_daily_exp = Optional(
        int,
        sql_default=0,
        column='battlepass_daily_exp'
    )

    battlepass_fortune = Required(
        int,
        sql_default='10',
        column='battlepass_fortune'
    )
    battlepass_daily_fortune = Required(
        int,
        sql_default=0,
        size=16,
        column='battlepass_daily_fortune'
    )

    match_count = Optional(
        int,
        sql_default=0,
        column='match_count'
    )


class MatchPlayer(db.Entity):
    _table_ = 'MatchPlayer'

    match_id = Required(
        int,
        size=64,
        column='match_id'
    )
    player_id = Required(
        int,
        size=16,
        column='player_id'
    )
    steam_id = Required(
        int,
        size=64,
        column='steam_id'
    )
    team_id = Required(
        int,
        size=16,
        column='team_id'
    )
    rating_change_new = Optional(
        int,
        column='rating_change_new'
    )
    rating_change_old = Optional(
        int,
        column='rating_change_old'
    )
    abilities = Optional(
        StrArray,
        nullable=True,
        column='abilities'
    )
    innate = Optional(
        str,
        column='innate'
    )
    round_deaths = Optional(
        Json,
        column='round_deaths'
    )
    items = Optional(
        StrArray,
        nullable=True,
        column='items'
    )

    battlepass_expreward = Optional(
        int,
        sql_default=0,
        column='battlepass_expreward'
    )
    battlepass_gloryreward = Optional(
        int,
        sql_default=0,
        column='battlepass_gloryreward'
    )

    mastery = Optional(
        str,
        nullable=True,
        column='mastery'
    )
