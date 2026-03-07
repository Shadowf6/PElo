import requests
import json
import consts
from consts import *

def searchTeam(number: str) -> None:
    response = requests.get(f"{URL}/teams", headers=HEADERS,
                            params={"number": number, "program": 1, "registered": True})
    data = response.json()

    if not data.get("data"):
        print("Invalid Team Number.")
        return

    team = data["data"][0]
    team_id = team["id"]

    response = requests.get(f"{OLD}/seasons/{SEASON}/skills", headers=HEADERS)
    data = response.json()

    total, driver, prog = 0, 0, 0
    for score in data:
        if score["team"]["id"] == team_id:
            total = score["scores"]["score"]
            driver = score["scores"]["driver"]
            prog = score["scores"]["programming"]
            break

    print(f"\nTeam {number} {team['team_name']}")
    print(f"ID: {team_id}")
    print(f"Grade: {team['grade']}")
    print(f"Region: {team['location']['region']}")
    print(f"Elo: {consts.TEAMS.get(number, 1000)}")
    print(f"Skills: {total} ({driver} Driver, {prog} Programming)")


def resetTeams() -> None:
    with open("teams.json", "w") as f:
        json.dump({}, f)

    print("All elos have been reset.")

def updateTeams() -> None:
    with open("teams.json", "w") as f:
        json.dump(consts.TEAMS, f, indent=4)

    print("Elos have been updated.")

def sort(team: str) -> tuple[int, str]:
    i = 0
    while i < len(team) and team[i].isdigit():
        i += 1
    return int(team[:i]), team[i:]

def sortTeams() -> None:
    consts.TEAMS = dict(sorted(consts.TEAMS.items(), key=lambda x: sort(x[0])))
    updateTeams()
