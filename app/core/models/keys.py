from pony.orm import Required

from .db import db


class DedicatedKeys(db.Entity):
    _table_ = "DedicatedKeys"
    key = Required(
        str,
        max_len=100
    )
