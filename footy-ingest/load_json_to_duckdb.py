import duckdb
import json
from pathlib import Path
from loguru import logger
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_BRONZE_DATA_PATH = BASE_DIR / "data" / "bronze"
DUCKDB_PATH = BASE_DIR / "data" / "footy_data.duckdb"
COMPETITIONS = ["PL", "BL1", "CL", "PD", "SA", "FL1"]


def upsert_dataframe(
    con: duckdb.DuckDBPyConnection, df: pd.DataFrame, table_name: str, unique_key: str
):
    """Creates table if not exists already, and then inserts only new rows based on the primary key column"""
    con.register("_temp_df", df)
    try:
        con.execute(
            f""" CREATE TABLE IF NOT EXISTS {table_name} AS SELECT * FROM _temp_df WHERE 1=0 """
        )

        con.execute(
            f"""INSERT INTO {table_name} 
                    SELECT * FROM _temp_df 
                    WHERE {unique_key} NOT IN (SELECT {unique_key} FROM {table_name})"""
        )
        con.unregister("_temp_df")
        logger.success(
            f"Upserted data into {table_name} in DuckDB, with {len(df)} records, based on unique key: {unique_key}"
        )
        con.unregister("_temp_df")
    except Exception as e:
        con.unregister("_temp_df")
        logger.error(f"Error upserting data into {table_name} in DuckDB: {e}")

def load_standings(con: duckdb.DuckDBPyConnection):
    standings = []
    teams = []

    for league in COMPETITIONS:
        folder = DEFAULT_BRONZE_DATA_PATH / league / "standings"
        files = sorted(folder.glob("*.json"), reverse=True)
        if not files:
            logger.warning(f"No files found for standings in {league}")
            continue

        raw_standings = json.loads(files[0].read_text())
        competition_name = raw_standings["competition"]["name"]
        season_id = raw_standings["season"]["id"]
        for standing in raw_standings["standings"]:
            for team in standing["table"]:
                standings.append(
                    {
                        "competition_id": raw_standings["competition"]["id"],
                        "competition_code": league,
                        "competition_name": competition_name,
                        "season_id": season_id,
                        "standing_type": standing["type"],
                        "standing_group": standing.get("group", None),
                        "standing_stage": standing.get("stage", None),
                        "position": team.get("position", None),
                        "team_id": team.get("team", {}).get("id", None),
                        "team_name": team.get("team", {}).get("name", None),
                        "team_short_name": team.get("team", {}).get("shortName", None),
                        "team_tla": team.get("team", {}).get("tla", None),
                        "team_crest_url": team.get("team", {}).get("crest", None),
                        "played_games": team.get("playedGames", None),
                        "won": team.get("won", None),
                        "draw": team.get("draw", None),
                        "lost": team.get("lost", None),
                        "points": team.get("points", None),
                        "goals_for": team.get("goalsFor", None),
                        "goals_against": team.get("goalsAgainst", None),
                        "goal_difference": team.get("goalDifference", None),
                    }
                )

                teams.append(
                    {
                        "team_id": team.get("team", {}).get("id", None),
                        "team_name": team.get("team", {}).get("name", None),
                        "team_short_name": team.get("team", {}).get("shortName", None),
                        "team_tla": team.get("team", {}).get("tla", None),
                        "team_crest_url": team.get("team", {}).get("crest", None),
                    }
                )

    if len(standings) > 0:
        df_standings = pd.DataFrame(standings)
        con.execute(""" DROP TABLE IF EXISTS league_standings """)
        con.execute(""" CREATE TABLE league_standings AS SELECT * FROM df_standings """)
        logger.success(
            f"Loaded standings data for {league} into DuckDB, with {len(df_standings)} records"
        )

    if len(teams) > 0:
        df_teams = pd.DataFrame(teams).drop_duplicates(subset=["team_id"])
        upsert_dataframe(con, df_teams, "dim_team", "team_id")
        logger.success(
            f"Loaded teams data for {league} into DuckDB, with {len(df_teams)} records"
        )

    return None


def load_matches(con: duckdb.DuckDBPyConnection):
    matches = []
    area = []
    competition = []
    season = []

    for league in COMPETITIONS:
        folder = DEFAULT_BRONZE_DATA_PATH / league / "matches"
        files = sorted(folder.glob("*.json"), reverse=True)
        if not files:
            logger.warning(f"No files found for matches in {league}")
            continue

        raw_matches = json.loads(files[0].read_text())
        for match in raw_matches["matches"]:
            match_referees = match.get("referees") or []
            matches.append(
                {
                    "match_area_id": match.get("area", {}).get("id", None),
                    "match_area_name": match.get("area", {}).get("name", None),
                    "match_area_code": match.get("area", {}).get("code", None),
                    "match_competition_id": match.get("competition", {}).get(
                        "id", None
                    ),
                    "match_competition_name": match.get("competition", {}).get(
                        "name", None
                    ),
                    "match_competition_code": match.get("competition", {}).get(
                        "code", None
                    ),
                    "match_season_id": match.get("season", {}).get("id", None),
                    "match_season_start_date": match.get("season", {}).get(
                        "startDate", None
                    ),
                    "match_season_end_date": match.get("season", {}).get(
                        "endDate", None
                    ),
                    "match_season_current_matchday": match.get("season", {}).get(
                        "currentMatchday", None
                    ),
                    "match_season_winner": match.get("season", {}).get("winner", None),
                    "match_id": match.get("id", None),
                    "match_utc_date": match.get("utcDate", None),
                    "match_status": match.get("status", None),
                    "match_matchday": match.get("matchday", None),
                    "match_stage": match.get("stage", None),
                    "match_group": match.get("group", None),
                    "match_home_team_id": (match.get("homeTeam") or {}).get("id"),
                    "match_home_team_name": (match.get("homeTeam") or {}).get("name"),
                    "match_away_team_id": (match.get("awayTeam") or {}).get("id"),
                    "match_away_team_name": (match.get("awayTeam") or {}).get("name"),
                    "match_score_full_time_home": match.get("score", {})
                    .get("fullTime", {})
                    .get("home", None),
                    "match_score_full_time_away": match.get("score", {})
                    .get("fullTime", {})
                    .get("away", None),
                    "match_score_half_time_home": match.get("score", {})
                    .get("halfTime", {})
                    .get("home", None),
                    "match_score_half_time_away": match.get("score", {})
                    .get("halfTime", {})
                    .get("away", None),
                    "match_referee": (
                        match_referees[0].get("name") if match_referees else None
                    ),
                }
            )

            area.append(
                {
                    "area_id": match.get("area", {}).get("id", None),
                    "area_name": match.get("area", {}).get("name", None),
                    "area_code": match.get("area", {}).get("code", None),
                    "area_flag_url": match.get("area", {}).get("flag", None),
                }
            )

            competition.append(
                {
                    "competition_id": match.get("competition", {}).get("id", None),
                    "competition_name": match.get("competition", {}).get("name", None),
                    "competition_code": match.get("competition", {}).get("code", None),
                    "competition_type": match.get("competition", {}).get("type", None),
                    "competition_emblem_url": match.get("competition", {}).get(
                        "emblem", None
                    ),
                }
            )

            season.append(
                {
                    "season_id": match.get("season", {}).get("id", None),
                    "season_start_date": match.get("season", {}).get("startDate", None),
                    "season_end_date": match.get("season", {}).get("endDate", None),
                    "season_current_matchday": match.get("season", {}).get(
                        "currentMatchday", None
                    ),
                    "season_winner": match.get("season", {}).get("winner", None),
                }
            )

    # fact and dim tables
    # matches is the fact table with foreign keys to the dimension tables area, competition and season. This allows for more efficient querying and storage of the data, as well as better organization and separation of concerns between the different entities in the data model.

    if len(matches) > 0:
        try:
            df_matches = pd.DataFrame(matches)
            con.execute(""" DROP TABLE IF EXISTS matches """)
            con.execute(""" CREATE TABLE matches AS SELECT * FROM df_matches """)
            logger.success(
                f"Loaded matches data for {league} into DuckDB, with {len(df_matches)} records"
            )
        except Exception as e:
            logger.error(f"Error loading matches data for {league}: {e}")

    if len(area) > 0:
        try:
            df_area = pd.DataFrame(area).drop_duplicates(subset=["area_id"])
            upsert_dataframe(con, df_area, "dim_area", "area_id")
            logger.success(
                f"Upserted area data for {league} into DuckDB, with {len(df_area)} records"
            )
        except Exception as e:
            logger.error(f"Error inserting area data for {league}: {e}")

    if len(competition) > 0:
        try:
            df_competition = pd.DataFrame(competition).drop_duplicates(
                subset=["competition_id"]
            )
            upsert_dataframe(con, df_competition, "dim_competition", "competition_id")
            logger.success(
                f"Upserted competition data for {league} into DuckDB, with {len(df_competition)} records"
            )
        except Exception as e:
            logger.error(f"Error inserting competition data for {league}: {e}")

    if len(season) > 0:
        try:
            df_season = pd.DataFrame(season).drop_duplicates(subset=["season_id"])
            upsert_dataframe(con, df_season, "dim_season", "season_id")
            logger.success(
                f"Upserted season data for {league} into DuckDB, with {len(df_season)} records"
            )
        except Exception as e:
            logger.error(f"Error upserting season data for {league}: {e}")

    return None


def load_clubs(con: duckdb.DuckDBPyConnection):
    clubs = []
    coach = []
    squad = []
    staffs = []

    for league in COMPETITIONS:
        folder = DEFAULT_BRONZE_DATA_PATH / league / "teams"
        files = sorted(folder.glob("*.json"), reverse=True)
        if not files:
            logger.warning(f"No files found for teams in {league}")
            continue

        raw_teams = json.loads(files[0].read_text())
        for team in raw_teams["teams"]:
            clubs.append(
                {
                    "club_id": team.get("id", None),
                    "club_name": team.get("name", None),
                    "club_short_name": team.get("shortName", None),
                    "club_tla": team.get("tla", None),
                    "club_crest_url": team.get("crest", None),
                    "team_address": team.get("address", None),
                    "team_website": team.get("website", None),
                    "team_founded": team.get("founded", None),
                    "club_club_colors": team.get("clubColors", None),
                    "club_venue": team.get("venue", None),
                }
            )

            coach.append(
                {
                    "coach_id": team.get("coach", {}).get("id", None),
                    "coach_first_name": team.get("coach", {}).get("firstName", None),
                    "coach_last_name": team.get("coach", {}).get("lastName", None),
                    "coach_name": team.get("coach", {}).get("name", None),
                    "coach_nationality": team.get("coach", {}).get("nationality", None),
                }
            )

            for player in team.get("squad", []):
                squad.append(
                    {
                        "player_id": player.get("id", None),
                        "player_name": player.get("name", None),
                        "player_position": player.get("position", None),
                        "player_date_of_birth": player.get("dateOfBirth", None),
                        "player_nationality": player.get("nationality", None),
                    }
                )

            for staff in team.get("staff", []):
                staffs.append(
                    {
                        "staff_id": staff.get("id", None),
                        "staff_name": staff.get("name", None),
                        "staff_role": staff.get("role", None),
                    }
                )

    if len(clubs) > 0:
        df_clubs = pd.DataFrame(clubs).drop_duplicates(subset = ["club_id"])
        con.register("_temp_clubs", df_clubs)
        try:
            con.execute(
                """ CREATE TABLE IF NOT EXISTS clubs AS SELECT * FROM _temp_clubs WHERE 1=0 """
            )
            con.execute(
                """DELETE FROM clubs WHERE club_id IN (SELECT club_id FROM _temp_clubs)"""
            )
            con.execute("""INSERT INTO clubs SELECT * FROM _temp_clubs""")
            con.unregister("_temp_clubs")
            logger.success(
                f"Upserted clubs data for {league} into DuckDB, with {len(df_clubs)} records, based on unique key: club_id"
            )
        except Exception as e:
            con.unregister("_temp_clubs")
            logger.error(f"Error loading clubs data for {league}: {e}")

    if len(coach) > 0:
        try:
            df_coach = pd.DataFrame(coach).drop_duplicates(subset=["coach_id"])
            upsert_dataframe(con, df_coach, "dim_coach", "coach_id")
            logger.success(
                f"Upserted coach data for {league} into DuckDB, with {len(df_coach)} records"
            )
        except Exception as e:
            logger.error(f"Error upserting coach data for {league}: {e}")

    if len(squad) > 0:
        try:
            df_squad = pd.DataFrame(squad).drop_duplicates(subset=["player_id"])
            upsert_dataframe(con, df_squad, "dim_player", "player_id")
            logger.success(
                f"Upserted squad data for {league} into DuckDB, with {len(df_squad)} records"
            )
        except Exception as e:
            logger.error(f"Error upserting squad data for {league}: {e}")

    if len(staffs) > 0:
        try:
            df_staff = pd.DataFrame(staffs).drop_duplicates(subset=["staff_id"])
            upsert_dataframe(con, df_staff, "dim_staff", "staff_id")
            logger.success(
                f"Upserted staff data for {league} into DuckDB, with {len(df_staff)} records"
            )
        except Exception as e:
            logger.error(f"Error inserting staff data for {league}: {e}")

    return None


def run() -> None:
    with duckdb.connect(DUCKDB_PATH) as con:
        load_standings(con)
        load_matches(con)
        load_clubs(con)


if __name__ == "__main__":
    run()
