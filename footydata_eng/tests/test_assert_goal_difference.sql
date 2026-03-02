select
    competition_code,
    position,
    team_name,
    team_tla,
    team_crest_url,
    goal_difference,
    (goals_for - goals_against) as expected_goal_difference
from {{ ref('standings_pl') }}
where goal_difference != expected_goal_difference
order by competition_code, position