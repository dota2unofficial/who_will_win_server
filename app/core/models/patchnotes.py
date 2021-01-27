from datetime import datetime

from pony.orm import Required, Optional

from ..settings import db


class Patchnotes(db.Entity):
    _table_ = 'Patchnotes'
    date = Required(datetime)
    content_english = Optional(
        str,
        sql_type='text',
        nullable=True
    )
    content_russian = Optional(
        str,
        sql_type='text',
        nullable=True
    )
    content_chinese = Optional(
        str,
        sql_type='text',
        nullable=True
    )
