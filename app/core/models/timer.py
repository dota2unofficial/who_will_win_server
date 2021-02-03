from pony.orm import Required

from .db import db


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
