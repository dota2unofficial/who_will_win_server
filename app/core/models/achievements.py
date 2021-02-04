from pony.orm import Required, Optional, Json, IntArray

from .db import db


class Achievements(db.Entity):
    _table_ = "Achievements"

    name = Required(
        str,
        max_len=100,
        nullable=False
    )
    type = Required(
        str,
        sql_type="varchar(50)",
        nullable=False,
        sql_default="'default'"
    )
    description = Optional(
        Json,
        nullable=True
    )
    reward = Optional(
        Json,
        nullable=True
    )


class PlayerAchievements(db.Entity):
    _table_ = 'PlayerAchievements'

    steam_id = Required(
        int,
        size=64,
        nullable=False,
        column='steam_id'
    )
    achievement_id = Required(
        int, size=16,
        nullable=False,
        column='achievement_id'
    )
    progress = Required(
        int,
        nullable=False
    )
    completed = Optional(
        bool,
        nullable=True,
        column='completed'
    )
    tier = Required(
        int,
        size=16,
        nullable=False,
        sql_default='1',
        column='tier'
    )
    meta_progress = Optional(
        IntArray,
        nullable=True,
        column='meta_progress'
    )
