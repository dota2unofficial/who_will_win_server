from pony.orm import select

from .utils import optional_session, result_keys_lower_decorator
from .constants import DEFAULT_PLAYER_VALUES
from ..core.models.players import Player
from ..core.models.quests import Quests
from ..core.models.payments import PriceList


@optional_session
def get_or_create_player(steam_id: int) -> Player:
    db_player = Player.get(steam_id=steam_id)
    if db_player:
        return db_player
    else:
        return Player(
            steam_id=steam_id,
            settings="{}",
            supporter_state=0,
            **DEFAULT_PLAYER_VALUES
        )


@optional_session
@result_keys_lower_decorator
def get_price_list():
    return [row.to_dict() for row in list(select(q for q in PriceList))]


@optional_session
@result_keys_lower_decorator
def get_quests():
    return [row.to_dict() for row in list(select(q for q in Quests))]
