from pydantic import BaseModel
from typing import Optional
from enum import Enum


class EventType(str, Enum):
    GOAL = "GOAL"
    YELLOW_CARD = "YELLOW_CARD"
    RED_CARD = "RED_CARD"
    SUBSTITUTION = "SUBSTITUTION"
    CORNER = "CORNER"
    FOUL = "FOUL"
    OFFSIDE = "OFFSIDE"
    VAR_CHECK = "VAR_CHECK"
    INJURY = "INJURY"
    SHOT_ON_TARGET = "SHOT_ON_TARGET"
    POSSESSION_UPDATE = "POSSESSION_UPDATE"


class TeamStats(BaseModel):
    name: str
    score: int
    possession: int
    shots: int
    shots_on_target: int
    corners: int
    fouls: int
    yellow_cards: int
    red_cards: int


class MatchEvent(BaseModel):
    event_id: str
    event_type: EventType
    minute: int
    added_time: Optional[int] = None
    team: str
    player: str
    description: str


class MatchState(BaseModel):
    match_id: str
    status: str
    minute: int
    added_time: int
    home: TeamStats
    away: TeamStats
    latest_event: Optional[MatchEvent] = None


class LiveMatchPayload(BaseModel):
    timestamp: str
    match: MatchState