select 
    competition_id,
    competition_name,
    competition_code,
    competition_type,
    competition_emblem_url
from {{ source('footydata_eng_raw', 'dim_competition') }}
