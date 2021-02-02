from pony.orm import Required, Optional

from .db import db


class PlayerInventory(db.Entity):
    _table_ = 'PlayerInventory'

    steam_id = Required(
        int,
        size=64,
        nullable=False,
        column='steam_id'
    )
    item_name = Required(
        str,
        max_len=100,
        nullable=False,
        sql_type='varchar(100)',
        column='item_name'
    )
    Count = Optional(
        int,
        size=16,
        sql_default=0,
        column='count'
    )
    inserted_gem = Optional(
        str,
        max_len=16,
        column='inserted_gem',
        nullable=True
    )
