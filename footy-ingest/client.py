import httpx
import time 
from loguru import logger
from typing import Optional
import os 
from dotenv import load_dotenv

load_dotenv()

class FootballDataAPIClient:
    BASE_URL = os.getenv("FOOTBALL_DATA_API_BASE_URL")
    RATE_LIMIT_DELAY = 6.5  # seconds, TO WORK AROUND THE 10 REQUESTS PER MINUTE LIMIT
    HEADERS = {"X-Auth-Token": os.getenv("FOOTBALL_DATA_API_KEY")}
    def __init__(self):
        api_key = os.getenv("FOOTBALL_DATA_API_KEY")
        if not api_key:
            raise ValueError("API key not found in the environment variables.")    

        self._client = httpx.Client(headers = self.HEADERS, base_url = self.BASE_URL)

        # request tracker 
        self._last_request_time: float = 0.0

    def _get(self, endpoint: str, params: Optional[dict] = {}) -> dict:
        request_time_elapsed = time.time() - self._last_request_time
        request_time_wait = self.RATE_LIMIT_DELAY - request_time_elapsed
        if (request_time_wait > 0):
            logger.debug(f"The rate limit waiting period: {request_time_wait:.2f} seconds")
            time.sleep(request_time_wait)
        
        logger.info(f"GET {endpoint} | Params: {params}")
        response = self._client.get(endpoint, params=params)
        self._last_request_time = time.time()

        if response.status_code == 429:
            retry_after = int(response.headers.get("x-requestcounter-reset", 60))
            logger.warning(f"429 Too Many Requests detected. Retry after {retry_after} seconds")
            time.sleep(retry_after)
            return self._get(endpoint=endpoint, params=params)

        response.raise_for_status()
        return response.json()
    
    def get_competitions(self) -> dict:
        """Fetches a list of all available competitions."""
        return self._get("competitions")
    def get_standings(self, competition_id: int) -> dict:
        """Fetches the current standings for a specific competition."""
        return self._get(f"competitions/{competition_id}/standings")
    def get_matches(self, competition_id: int, season: Optional[int] = None) -> dict:
        """Fetches matches for a specific competition, optionally filtered by season."""
        params = {"season": season} if season else {}
        return self._get(f"competitions/{competition_id}/matches", params=params)
    def get_teams(self, competition_id: int) -> dict:
        """Fetches a list of teams for a specific competition."""
        return self._get(f"competitions/{competition_id}/teams")
    
    def close(self):
        """Closes the underlying HTTP client session."""
        self._client.close()

    #this allows the use as context manager, ensuring proper cleanup of resources
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()