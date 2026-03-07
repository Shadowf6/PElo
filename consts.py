import os
import dotenv
import json

dotenv.load_dotenv()
API_KEY = os.getenv("API_KEY")

URL = "https://www.robotevents.com/api/v2"
OLD = "https://www.robotevents.com/api"

HEADERS = {"Authorization": f"Bearer {API_KEY}", "Accept": "application/json"}

TEAMS = {}

SEASON = 197
YEAR = 2026
