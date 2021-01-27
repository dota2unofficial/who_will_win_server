from typing import List

from pydantic import BaseModel


class BeforeMatchIn(BaseModel):
    mapName: str
    players: List[str]
