import os
import dotenv
import math
import json

dotenv.load_dotenv()
API_KEY = os.getenv("API_KEY")

URL = "https://www.robotevents.com/api/v2"
OLD = "https://www.robotevents.com/api"

HEADERS = {"Authorization": f"Bearer {API_KEY}", "Accept": "application/json"}

TEAMS = {}

SEASON = 197
YEAR = 2026

SIG_MULTIPLIER = 1.3
LEAGUE_MULTIPLIER = 0.6
EVENT = {
    1: 1,
    2: SIG_MULTIPLIER,
    3: LEAGUE_MULTIPLIER
}

ELIM_MULTIPLIER = 0.9
MATCH = {
    1: 0,
    2: 1,
    3: ELIM_MULTIPLIER,
    4: ELIM_MULTIPLIER,
    5: ELIM_MULTIPLIER,
    6: ELIM_MULTIPLIER
}

B = 40  # Base elo gain/loss
T = 103  # Performance threshold
D = 400 / math.log(1.5, 10)  # +400 elo difference = 1.5:1 odds of winning
