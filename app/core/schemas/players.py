from datetime import datetime
from typing import Union, Optional, List

import orjson
from pony.orm.ormtypes import TrackedDict
from pydantic import BaseModel, Json


class PlayerBeforeMatch(BaseModel):
    steam_id: str
    settings: Union[TrackedDict, Json]

    supporter_state: int
    supporter_enddate: Optional[datetime]

    match_count: int

    rating_ffa: int
    rating_duos: int
    rating_squads: int

    battlepass_exp: int
    battlepass_glory: int
    battlepass_level: int
    battlepass_daily_exp: int

    battlepass_fortune: int
    battlepass_daily_fortune: int

    class Config:
        orm_mode = True

        json_encoders = {
            TrackedDict: TrackedDict.get_untracked
        }

        json_loads = orjson.loads
        json_dumps = orjson.dumps


class RoundDeath(BaseModel):
    round: int
    name: str
    totem: Optional[str]


class PlayerAfterMatch(BaseModel):
    player_id: int
    steam_id: str
    innate: Optional[str]
    abilities: Optional[List[str]]
    round_deaths: Optional[List[RoundDeath]]
    items: Optional[list]
    other_players_AvgMMR: int
    early_leaver: Optional[bool]
    mastery: Optional[str]
