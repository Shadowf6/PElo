import requests
import json
import consts
from consts import *

def createTeamRankings() -> None:
    teams = []

    page = 1
    while True:
        response = requests.get(f"{URL}/teams", headers=HEADERS,
                                params={"program": 1, "registered": True, "per_page": 250, "page": page})
        data = response.json()

        if not data.get("data"):
            break

        for team in data["data"]:
            if team["number"] in consts.ELOS and team["grade"] == "High School":
                teams.append({"number": team["number"], "name": team["team_name"], "grade": team["grade"],
                              "region": f"{team["location"]["region"]}, {team["location"]["country"]}",
                              "elo": consts.ELOS.get(team["number"], 1000)})

        if page >= data["meta"]["last_page"]:
            break

        print(f"{250 * page}/{data["meta"]["total"]} Done")
        page += 1

    with open("../data/teams.json", "w") as f:
        json.dump(teams, f, indent=4)

    print("Done!")

def searchTeam(number: str) -> None:
    response = requests.get(f"{URL}/teams", headers=HEADERS,
                            params={"number": number, "program": 1, "registered": True})
    data = response.json()

    if not data.get("data"):
        print("Invalid Team Number.")
        return

    team = data["data"][0]
    team_id = team["id"]

    place = sorted(consts.ELOS, key=consts.ELOS.get, reverse=True)
    try:
        p = place.index(number) + 1
    except ValueError:
        p = 99999

    total, driver, prog, rank = 0, 0, 0, 1
    if team["grade"] == "High School":
        response = requests.get(f"https://events.vex.com/api/seasons/{SEASON}/skills/?search=&grade_level=High+School", headers=HEADERS)
    else:
        response = requests.get(f"https://events.vex.com/api/seasons/{SEASON}/skills/?search=&grade_level=Middle+School", headers=HEADERS)

    data = response.json()

    for score in data:
        if score["team"]["id"] == team_id:
            total = score["scores"]["score"]
            driver = score["scores"]["driver"]
            prog = score["scores"]["programming"]
            break
        rank += 1

    print(f"\nTeam {number} {team["team_name"]}")
    print(f"Grade: {team["grade"]}")
    print(f"Region: {team["location"]["region"]}")
    print(f"Elo: {consts.ELOS.get(number, 1000)} (#{p})")
    print(f"Skills: {total} ({driver} Driver, {prog} Programming) (#{rank})")

def resetElos() -> None:
    with open("../data/elos.json", "w") as f:
        json.dump({}, f)
        consts.ELOS = {}

    print("Elos have been reset.")

def updateElos() -> None:
    with open("../data/elos.json", "w") as f:
        json.dump(consts.ELOS, f, indent=4)

    print("Elos have been updated.")

def sortElos() -> None:
    consts.ELOS = dict(reversed(sorted(consts.ELOS.items(), key=lambda x: x[1])))
    updateElos()
