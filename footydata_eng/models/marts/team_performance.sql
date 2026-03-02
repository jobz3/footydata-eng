with matches_unpivoted as (
    -- Give each team one row per match (home and away)
    select
        match_id,
        match_utc_date,
        match_matchday,
        match_home_team_id  as team_id,
        match_home_team_name as team_name,
        match_away_team_name as opponent_name,
        'home'               as venue,
        match_score_full_time_home as goals_for,
        match_score_full_time_away as goals_against
    from {{ ref('stg_matches') }}
    where match_status = 'FINISHED'

    union all

    select
        match_id,
        match_utc_date,
        match_matchday,
        match_away_team_id   as team_id,
        match_away_team_name as team_name,
        match_home_team_name as opponent_name,
        'away'               as venue,
        match_score_full_time_away as goals_for,
        match_score_full_time_home as goals_against
    from {{ ref('stg_matches') }}
    where match_status = 'FINISHED'
),

ranked as (
    select
        *,
        {{ get_result_type('goals_for', 'goals_against') }} as result,
        row_number() over (
            partition by team_id
            order by match_utc_date desc
        ) as match_rank
    from matches_unpivoted
)

select * from ranked
where match_rank <= 5
order by team_name, match_rank
