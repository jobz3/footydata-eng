select 
    cast(club_id as integer) as club_id,
    club_name,
    club_short_name,
    club_tla,
    club_crest_url,
    team_address,
    team_website,
    team_founded,
    club_club_colors,
    club_venue
from {{ source('footydata_eng_raw', 'clubs') }}
