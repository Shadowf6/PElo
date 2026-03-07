import requests
import json
import consts
from consts import *

def searchTeam(number: str) -> None:
    response = requests.get(f"{URL}/teams", headers=HEADERS, params={"number": number, "program": v5rc, "registered": True})
    data = response.json()

    if not data["data"]:
        print("Invalid Team Number.")
        return

    team = data["data"][0]

    print(f"\nTeam {number} {team['team_name']}")
    print(f"Grade: {team['grade']}")
    print(f"Region: {team['location']['region']}")
    print(f"Elo: {consts.TEAMS.get(number, 1000)}")

def resetTeams() -> None:
    with open("teams.json", "w") as f:
        json.dump({}, f)

    print("All elos have been reset.")

def updateTeams() -> None:
    with open("teams.json", "w") as f:
        json.dump(consts.TEAMS, f, indent=4)

    print("Elos have been updated.")
