import os
import dotenv
import json

dotenv.load_dotenv()
API_KEY = os.getenv("API_KEY")

URL = "https://www.robotevents.com/api/v2"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json"
}

TEAMS = {}

pushback = 197
year = 2026
v5rc = 1
