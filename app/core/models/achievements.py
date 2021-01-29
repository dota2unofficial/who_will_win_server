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

    SteamId = Required(
        int,
        size=64,
        nullable=False,
        column='steam_id'
    )
    AchievementId = Required(
        int, size=16,
        nullable=False,
        column='achievement_id'
    )
    Progress = Required(
        int,
        nullable=False
    )
    Completed = Optional(
        bool,
        nullable=True,
        column='completed'
    )
    Tier = Required(
        int,
        size=16,
        nullable=False,
        sql_default='1',
        column='tier'
    )
    MetaProgress = Optional(
        IntArray,
        nullable=True,
        column='meta_progress'
    )
