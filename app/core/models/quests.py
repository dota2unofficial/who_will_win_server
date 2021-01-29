from datetime import datetime

from pony.orm import Required, Json, Optional

from .db import db


class Quests(db.Entity):
    _table_ = 'Quests'

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


class PlayerQuests(db.Entity):
    _table_ = 'PlayerQuests'

    steam_id = Required(
        int,
        size=64,
        nullable=False,
        column='steam_id'
    )
    quest_id = Required(
        int,
        size=16,
        nullable=False,
        column='quest_id'
    )
    added_at = Required(
        datetime,
        nullable=False,
        column='added_at'
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
