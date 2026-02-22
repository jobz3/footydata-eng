from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum

class Area(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    code: Optional[str] = None
    flag: Optional[str] = None


class Team(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    shortName: Optional[str] = None
    tla: Optional[str] = None
    crest: Optional[str] = None
    venue: Optional[str] = None
    area: Optional[Area] = None

class StandingsTable(BaseModel):
    position: Optional[int] = None
    team: Optional[Team] = None
    playedGames: Optional[int] = None
    form: Optional[str] = None
    won: Optional[int] = None
    draw: Optional[int] = None
    lost: Optional[int] = None
    points: Optional[int] = None
    goalsFor: Optional[int] = None
    goalsAgainst: Optional[int] = None
    goalDifference: Optional[int] = None

class Season(BaseModel):
    id: Optional[int] = None
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    currentMatchday: Optional[int] = None
    winner: Optional[Team] = None

class Competition(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    code: Optional[str] = None
    type: Optional[str] = None
    emblem: Optional[str] = None
    plan: Optional[str] = None
    area: Optional[Area] = None
    currentSeason: Optional[Season] = None
    numberOfAvailableSeasons: Optional[int] = None

class Standing(BaseModel):
    stage: Optional[str] = None
    type: Optional[str] = None
    group: Optional[str] = None
    table: Optional[list[StandingsTable]] = None

# class FullTimeScore(BaseModel):
#     homeTeam: Optional[int]
#     awayTeam: Optional[int]

# class HalfTimeScore(BaseModel):
#     homeTeam: Optional[int]
#     awayTeam: Optional[int]
class Score(BaseModel):
    home: Optional[int] = None
    away: Optional[int] = None

class MatchScore(BaseModel):
    winner: Optional[str] = None
    duration: Optional[str] = None
    fullTime: Optional[Score] = None
    halfTime: Optional[Score] = None

class Referee(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    type: Optional[str] = None
    nationality: Optional[str] = None

class Match(BaseModel):
    area: Optional[Area] = None
    competition: Optional[Competition] = None
    season: Optional[Season] = None
    id: Optional[int] = None
    utcDate: Optional[datetime] = None
    status: Optional[str] = None
    matchday: Optional[int] = None
    stage: Optional[str] = None
    group: Optional[str] = None
    lastUpdated: Optional[datetime] = None
    homeTeam: Optional[Team] = None
    awayTeam: Optional[Team] = None