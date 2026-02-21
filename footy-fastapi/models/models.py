from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum

class Area(BaseModel):
    id: int
    name: str
    code: Optional[str]
    flag: Optional[str]


class Team(BaseModel):
    id: int
    name: str
    shortName: Optional[str]
    tla: Optional[str]
    crest: Optional[str]
    venue: Optional[str] = None
    area: Area | None = None

class StandingsTable(BaseModel):
    position: int
    team: Team
    playedGames: int
    form: Optional[str]
    won: int
    draw: int
    lost: int
    points: int
    goalsFor: int
    goalsAgainst: int
    goalDifference: int

class Season(BaseModel):
    id: int
    startDate: datetime
    endDate: datetime
    currentMatchday: Optional[int]
    winner: Optional[Team]

class Competition(BaseModel):
    id: int
    name: str
    code: Optional[str]
    type: Optional[str]
    emblem: Optional[str]
    plan: Optional[str] = None
    area: Optional[Area]
    currentSeason: Optional[Season] = None
    numberOfAvailableSeasons: Optional[int]

class Standing(BaseModel):
    stage: str
    type: str
    group: Optional[str]
    table: list[StandingsTable]

# class FullTimeScore(BaseModel):
#     homeTeam: Optional[int]
#     awayTeam: Optional[int]

# class HalfTimeScore(BaseModel):
#     homeTeam: Optional[int]
#     awayTeam: Optional[int]
class Score(BaseModel):
    home: Optional[int]
    away: Optional[int]

class MatchScore(BaseModel):
    winner: Optional[str]
    duration: str
    fullTime: Score
    halfTime: Score

class Referee(BaseModel):
    id: int
    name: str
    type: str
    nationality: Optional[str]

class Match(BaseModel):
    area: Area
    competition: Competition
    season: Season
    id: int
    utcDate: datetime
    status: str
    matchday: Optional[int]
    stage: str
    group: Optional[str]
    lastUpdated: datetime
    homeTeam: Team
    awayTeam: Team