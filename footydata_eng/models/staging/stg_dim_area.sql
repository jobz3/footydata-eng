select 
    area_id,
    area_name,
    area_code,
    area_flag_url
from {{ source('footydata_eng_raw', 'dim_area') }}
