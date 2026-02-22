import httpx
from dotenv import load_dotenv
import os
import json
from models.models import Team, Match, Standing, Competition
    
load_dotenv()

HEADERS = {"X-Auth-Token": os.getenv("FOOTBALL_DATA_API_KEY")}

client = httpx.Client(headers=HEADERS, base_url=os.getenv("FOOTBALL_DATA_API_BASE_URL"))
api_endpoints = ["/competitions/PL/teams", "/competitions/PL/matches", "/competitions/PL/standings"]

def prettyify_json(response):
    return json.dumps(response.json(), indent = 2)

script_dir = os.path.dirname(__file__)
json_dir = os.path.join(script_dir, "json")
os.makedirs(json_dir, exist_ok=True)

for endpoint in api_endpoints:
    filename = 'api_response_' + endpoint.replace("/", "_").strip("_") + ".json"
    path = os.path.join(json_dir, filename)
    response = client.get(endpoint)
    with open(path, "w+", encoding="utf-8") as f:
        f.write(prettyify_json(response))