import os
import dotenv
import math
import json

dotenv.load_dotenv()
API_KEY = os.getenv("API_KEY")

URL = "https://events.vex.com/api/v2"

HEADERS = {"Authorization": f"Bearer {API_KEY}", "Accept": "application/json"}

elos = {}
DEFAULT_ELO = 1000

active = {}
inactive = {}
INACTIVITY = 60

SEASON = 197
YEAR = 2027

WQ_MULTIPLIER = 1.2
LEAGUE_MULTIPLIER = 0.6
EVENT_TYPES = {
    1: 1,
    2: WQ_MULTIPLIER,
    3: LEAGUE_MULTIPLIER
}

ELIM_MULTIPLIER = 0.8
MATCH_TYPES = {
    2: 1,
    3: ELIM_MULTIPLIER,
    4: ELIM_MULTIPLIER,
    5: ELIM_MULTIPLIER,
    6: ELIM_MULTIPLIER,
    7: ELIM_MULTIPLIER
}

BASE = 30
MAX_SCORE = 588
ODDS = 400 / math.log10(2)
