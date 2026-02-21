import httpx
from dotenv import load_dotenv
import os

load_dotenv()

HEADERS = {"X-Auth-Token": os.getenv("FOOTBALL_DATA_API_KEY")}

