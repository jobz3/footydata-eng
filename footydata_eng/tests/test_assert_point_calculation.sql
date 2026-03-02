select
    competition_code,
    position,
    team_name,
    team_tla,
    team_crest_url,
    points,
    (won * 3 + draw) as expected_points
from {{ ref('standings_pl') }}
where points != expected_points