from datetime import datetime

from pony.orm import Required, Optional, Json

from .db import db


class Match(db.Entity):
    _table_ = 'Match'

    match_id = Required(
        int,
        size=64,
        column='match_id'
    )
    ended_at = Required(
        datetime,
        sql_type='timestamp without time zone',
        column='ended_at'
    )
    map_name = Optional(
        str,
        column='map_name'
    )


class MatchEvent(db.Entity):
    _table_ = 'MatchEvent'

    match_id = Required(
        int,
        size=64,
        column='match_id'
    )
    body = Required(
        Json,
        column='body'
    )


class MatchTeam(db.Entity):
    _table_ = 'MatchTeam'
    match_id = Required(
        int,
        size=64,
        column='match_id'
    )
    team_id = Required(
        int,
        size=16,
        column='team_id'
    )
    time = Required(
        float,
        sql_type='double precision',
        column='time'
    )
    round = Required(
        int,
        column='round'
    )


class ScriptError(db.Entity):
    _table_ = 'ScriptError'

    stack = Required(
        str,
        sql_type='text',
        column='stack'
    )
    match_id = Required(
        int,
        size=64,
        sql_default=0,
        column='match_id'
    )
    count = Required(
        int,
        sql_default=0,
        column='count'
    )
