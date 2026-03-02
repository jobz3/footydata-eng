select 
    --id 
    cast(competition_id as integer) as competition_id,
    competition_code,
    competition_name,
    cast(season_id as integer) as season_id,
    standing_type,
    standing_group,
    standing_stage,
    position,
    team_id,
    team_name,
    team_short_name,
    team_tla,
    team_crest_url,
    played_games,
    won,
    draw,
    lost,
    points,
    goals_for,
    goals_against,
    goal_difference
from {{ source('footydata_eng_raw', 'league_standings') }}
