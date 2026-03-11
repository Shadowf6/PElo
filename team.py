import requests
import json
import consts
from consts import *

# 2 Requests
def searchTeam(number: str) -> None:
    response = requests.get(f"{URL}/teams", headers=HEADERS,
                            params={"number": number, "program": 1, "registered": True})
    data = response.json()

    if not data.get("data"):
        print("Invalid Team Number.")
        return

    team = data["data"][0]
    team_id = team["id"]

    place = sorted(consts.TEAMS, key=consts.TEAMS.get, reverse=True)
    try:
        p = place.index(number) + 1
    except ValueError:
        p = 99999

    response = requests.get(f"{OLD}/seasons/{SEASON}/skills", headers=HEADERS)
    data = response.json()

    total, driver, prog, rank = 0, 0, 0, 1
    for score in data:
        if score["team"]["id"] == team_id:
            total = score["scores"]["score"]
            driver = score["scores"]["driver"]
            prog = score["scores"]["programming"]
            break
        rank += 1

    print(f"\nTeam {number} {team['team_name']}")
    print(f"ID: {team_id}")
    print(f"Grade: {team['grade']}")
    print(f"Region: {team['location']['region']}")
    print(f"Elo: {consts.TEAMS.get(number, 1000)} (#{p})")
    print(f"Skills: {total} ({driver} Driver, {prog} Programming) (#{rank})")

def resetTeams() -> None:
    with open("teams.json", "w") as f:
        json.dump({}, f)
        consts.TEAMS = {}

    print("Elos have been reset.")

def updateTeams() -> None:
    with open("teams.json", "w") as f:
        json.dump(consts.TEAMS, f, indent=4)

    print("Elos have been updated.")

def sortTeams() -> None:
    consts.TEAMS = dict(reversed(sorted(consts.TEAMS.items(), key=lambda x: x[1])))
    updateTeams()
