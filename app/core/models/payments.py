from datetime import date

from pony.orm import Required, Optional

from ..settings import db


class PriceList(db.Entity):
    _table_ = 'PriceList'
    payment_kind = Required(
        str,
        max_len=100,
        column='payment_kind',
        unique=True
    )
    price_usd = Required(
        int,
        sql_default=0,
        column='price_usd'
    )
    price_cny = Required(
        int,
        sql_default=0,
        column='price_cny'
    )
    item_name = Required(
        str,
        max_len=100,
        column='item_name'
    )


class ItemSellingHistory(db.Entity):
    _table_ = 'ItemSellingHistory'
    steam_id = Required(
        int,
        size=64,
        column='steam_id'
    )
    item_name = Required(
        str,
        max_len=100,
        column='item_name'
    )
    item_count = Required(
        int,
        column='item_count'
    )
    sold_at = Required(
        date,
        sql_type='date',
        column='sold_at'
    )
    glory_cost = Optional(
        int,
        nullable=True,
        column='glory_cost'
    )
    real_cost = Optional(
        int,
        nullable=True,
        column='real_cost'
    )


class GiftCodes(db.Entity):
    _table_ = 'GiftCodes'
    steam_id = Required(
        int,
        size=64,
        column='steam_id'
    )
    code = Required(
        str,
        max_len=50,
        column='code'
    )
    payment_kind = Required(
        str,
        max_len=100,
        column='payment_kind'
    )
    item_name = Required(
        str,
        max_len=100,
        column='item_name'
    )
    item_count = Required(
        int,
        sql_default=1,
        column='item_count'
    )
    redeemer_steamId = Optional(
        int,
        size=64,
        column='redeemer_steam_id'
    )
