select 
    player_id,
    player_name,
    player_position,
    player_date_of_birth,
    player_nationality
from {{ source('footydata_eng_raw', 'dim_player') }}