select 
    coach_id,
    coach_first_name,
    coach_last_name,
    coach_name,
    coach_nationality
from {{ source('footydata_eng_raw', 'dim_coach') }}
