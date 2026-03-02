select 
    team_id,
    team_name,
    team_short_name,
    team_tla,
    team_crest_url
from {{ source('footydata_eng_raw', 'dim_team') }}
