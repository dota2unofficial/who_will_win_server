from pony.orm import Required

from .db import db


class ScriptError(db.Entity):
    _table_ = 'ScriptError'

    stack = Required(
        str,
        sql_type='text',
        column='Stack'
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


class TimerPerformance(db.Entity):
    _table_ = 'TimerPerformance'

    line = Required(
        str,
        column='line',
        optimistic=False
    )
    average_time = Required(
        float,
        column='average_time',
        optimistic=False
    )
