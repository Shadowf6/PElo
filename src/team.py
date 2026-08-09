import requests
import json
import time

import consts
from consts import *


def createTeamRankings():
    teams = []
    page = 1

    while True:
        i = 0
        data = {}

        while True:
            response = requests.get(f"{URL}/teams", headers=HEADERS,
                                    params={"program": 1, "per_page": 250, "page": page})

            if response.status_code != 200:
                time.sleep(30 + i)
                i += 10
                continue

            try:
                data = response.json()
                i = 0
                break
            except json.decoder.JSONDecodeError:
                time.sleep(30 + i)
                i += 10

        if not data.get("data"):
            break

        for team in data["data"]:
            if team["number"] in consts.elos:
                teams.append({"number": team["number"], "name": team["team_name"], "grade": team["grade"],
                              "region": f"{f"{team["location"]["region"]}, " if team["location"]["region"] is not None else ""}{team["location"]["country"]}",
                              "elo": consts.elos.get(team["number"], DEFAULT_ELO)})

        if page >= data["meta"]["last_page"]:
            break

        print(f"{250 * page}/{data["meta"]["total"]} Done")
        page += 1

    with open("../data/teams.json", "w") as f:
        json.dump(teams, f, indent=4)

    print("Done!")


def searchTeam(number: str):
    response = requests.get(f"{URL}/teams", headers=HEADERS,
                            params={"number": number, "program": 1, "registered": True})
    data = response.json()

    if not data.get("data"):
        print("Invalid Team Number.")
        return

    team = data["data"][0]
    team_id = team["id"]

    place = sorted(consts.elos, key=consts.elos.get, reverse=True)
    try:
        p = place.index(number) + 1
    except ValueError:
        p = 0

    total, driver, prog, rank = 0, 0, 0, 1
    if team["grade"] == "High School":
        response = requests.get(f"https://events.vex.com/api/seasons/{SEASON}/skills/?search=&grade_level=High+School", headers=HEADERS)
    else:
        response = requests.get(
            f"https://events.vex.com/api/seasons/{SEASON}/skills/?search=&grade_level=Middle+School", headers=HEADERS)

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
    print(f"Region: {f"{team["location"]["region"]}, " if team["location"]["region"] is not None else ""}{team["location"]["country"]}")
    print(f"Elo: {consts.elos.get(number, DEFAULT_ELO)} (#{p})")
    print(f"Skills: {total} ({driver} Driver, {prog} Programming) (#{rank})")


def resetElos():
    with open("../data/elos.json", "w") as f:
        json.dump({}, f)
        consts.elos = {}

    with open("../data/active.json", "w") as f:
        json.dump({"last": "2026-01-01", "teams": {}}, f)
        consts.active = {"last": "2026-01-01", "teams": {}}

    print("Elos have been reset.")


def updateElos():
    with open("../data/elos.json", "w") as f:
        json.dump(consts.elos, f, indent=4)

    with open("../data/active.json", "w") as f:
        json.dump(consts.active, f, indent=4)

    print("Elos have been updated.")


def sortElos():
    consts.elos = dict(reversed(sorted(consts.elos.items(), key=lambda x: x[1])))
    consts.active["teams"] = dict(sorted(consts.active["teams"].items(), key=lambda x: x[1]))
    updateElos()
