select 
    season_id,
    season_start_date,
    season_end_date,
    season_current_matchday,
    season_winner
from {{ source('footydata_eng_raw', 'dim_season') }}
