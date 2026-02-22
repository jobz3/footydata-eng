from loguru import logger
from client import FootballDataAPIClient
from storage.bronze_storage import BronzeStorage
from models.models import Team, Match, Standing, Competition
from typing import Optional

#TODO: replaces this with get_competitons method from the client and extracting the league code from the output, rather than hardcoding the league codes here.
COMPETITIONS = ["PL", "BL1", "CL", "PD", "SA", "FL1"]

def ingest_standings(client: FootballDataAPIClient, storage: BronzeStorage):
    for league in COMPETITIONS:
        logger.info(f"Fetching standings for {league}")
        standings = client.get_standings(league)

        try:
            valid_standings = [Standing(**s) for s in standings["standings"]]
            logger.info(f"Successfully validated standings data, {league} : {len(valid_standings)} entries")
        except Exception as e:
            logger.error(f"Error validating standings data for {league}: {e}")
            raise

        storage.write(league, "standings", standings)

def ingest_matches(client: FootballDataAPIClient, storage: BronzeStorage, season: Optional[int] = None):
    for league in COMPETITIONS:
        logger.info(f"Fetching matches for league: {league} for season; {season if season else 'current'}")
        matches = client.get_matches(league, season)
        try:
            valid_matches = [Match(**m) for m in matches["matches"]]
            logger.info(f"Successfully validated matches data , {league} : {len(valid_matches)} entries")
        except Exception as e:
            logger.error(f"Error validating matches data for {league}: {e}")
            raise

        storage.write(league, "matches", matches)

def ingest_teams(client: FootballDataAPIClient, storage: BronzeStorage):
    for league in COMPETITIONS:
        logger.info(f"Fetching teams for league: {league}")
        teams = client.get_teams(league)
        try:
            valid_teams = [Team(**t) for t in teams["teams"]]
            logger.info(f"Successfully validated teams data, {league} : {len(valid_teams)} entries")
        except Exception as e:
            logger.error(f"Error validating teams data for {league}: {e}")
            raise

        storage.write(league, "teams", teams)

#TODO: add ingest_competitions method to fetch and store the metadata about the competitions themselves, which is useful for the API layer to have access to. This can be done by calling the get_competitions method from the client and storing the output in the bronze storage as well.
def ingest_competitions(client: FootballDataAPIClient, storage: BronzeStorage):
    return None

def run():
    logger.info("Starting data ingestion process")
    with FootballDataAPIClient() as client:
        storage = BronzeStorage()
        ingest_standings(client, storage)
        ingest_matches(client, storage)
        ingest_teams(client, storage)
    
    logger.info("Data ingestion process completed successfully")

if __name__ == "__main__":
    run()
    