from datetime import datetime
from typing import Union, Optional

import orjson
from pony.orm.ormtypes import TrackedDict
from pydantic import BaseModel, Json


class PlayerBeforeMatch(BaseModel):
    steamId: str
    settings: Union[TrackedDict, Json]

    supporterState: int
    SupporterEndDate: Optional[datetime]

    MatchCount: int

    Rating_FFA: int
    Rating_Duos: int
    Rating_Squads: int

    BattlePass_Exp: int
    BattlePass_Glory: int
    BattlePass_Level: int
    BattlePass_DailyExp: int

    BattlePass_Fortune: int
    BattlePass_DailyFortune: int

    # battlePass: PlayerBattlePassData

    class Config:
        orm_mode = True

        json_encoders = {
            TrackedDict: TrackedDict.get_untracked
        }

        json_loads = orjson.loads
        json_dumps = orjson.dumps
