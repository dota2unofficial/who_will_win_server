from typing import List, Dict, Optional

from pydantic import BaseModel

from .players import PlayerAfterMatch


class BeforeMatchIn(BaseModel):
    map_name: str
    players: List[str]


class LeaderboardRating(BaseModel):
    steam_id: str
    rating: int

    class Config:
        orm_mode = True


class LeaderboardRound(BaseModel):
    steam_id: str
    round: int
    time: int

    class Config:
        orm_mode = True


class Leaderboards(BaseModel):
    rating: Dict[str, List[LeaderboardRating]]
    bestPvE: Dict[str, List[LeaderboardRound]]
    bestPvP: Dict[str, List[LeaderboardRound]]

    class Config:
        orm_mode = True


class AfterMatchTeam(BaseModel):
    team_id: int
    round: int
    time: int
    players: List[PlayerAfterMatch]


class AfterMatchTeamSeparated(AfterMatchTeam):
    match_place: int
    other_teams_AvgMMR: Optional[int]


class AfterMatchPlayerBased(BaseModel):
    map_name: str
    match_id: int
    isPvp: bool
    team: AfterMatchTeamSeparated
