select
    {{ dbt_utils.generate_surrogate_key([
        'competition_id', 
        'season_id', 
        'team_id', 
        'standing_type', 
        'standing_group', 
        'standing_stage'
    ]) }} as standing_sk,
    competition_code,
    position,
    team_name,
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
from {{ ref('stg_league_standings') }}