import requests
import statistics
import datetime

import consts
from consts import *

WINRATE = 0.9
AWPRATE = 0.15
AUTONRATE = 0.8
MEDIAN = 140
AWARDRATE = 3
AUTONWIN = 12

AWARDS = {
    "Excellence": 10,
    "Design": 7,
    "Amaze": 5,
    "Innovate": 4,
    "Think": 4,
    "Build": 3,
    "Create": 3,
    "Judges": 3,
    "Inspire": 1,
    "Sportsmanship": 1,
    "Energy": 1,
    "Champion": 1
}


def evaluateAward(name: str, qual: list) -> int:
    value = 0

    for q in qual:
        if "World Championship" in q:
            value += 3

    if "WC" in name:
        value += 5

    for a in AWARDS.keys():
        if a in name:
            value += AWARDS[a]
            break

    return value


def evaluateTeam(number: str):
    response = requests.get(f"{URL}/teams", headers=HEADERS,
                            params={"number": number, "program": 1})
    data = response.json()

    if not data.get("data"):
        print("\nInvalid Team Number.")
        return

    team = data["data"][0]
    team_id = team["id"]


    rank = 0
    total = 1

    # Grade can be wrong for new teams, so check high school first, then middle school
    for level in ("High+School", "Middle+School"):
        response = requests.get(f"https://events.vex.com/api/seasons/{SEASON}/skills/?search=&grade_level={level}", headers=HEADERS)

        rank = 0
        total = 1
        for score in response.json():
            if score["team"]["id"] == team_id:
                rank = total
            total += 1

        if rank != 0:
            break

    print(f"\nSkills Rank: #{rank}")
    skills = round(100 * (total - rank + 1) / total) if rank != 0 else 0


    i = 0
    wins = 0
    total_quals = 0

    response = requests.get(f"{URL}/teams/{team_id}/matches", headers=HEADERS,
                            params={"season": SEASON, "round[]": [2, 3, 4, 5, 6, 7], "per_page": 250})
    data = response.json()

    if not data.get("data"):
        print("No matches found.")
        return

    total_matches = data["meta"]["total"]
    scores = []

    for match in data["data"]:
        i += 1

        if match["round"] == 2:
            total_quals += 1

        red = match["alliances"][1]
        blue = match["alliances"][0]

        if len(red["teams"]) != 2 or len(blue["teams"]) != 2:
            continue

        teams = [red["teams"][0]["team"]["id"], red["teams"][1]["team"]["id"],
                 blue["teams"][0]["team"]["id"], blue["teams"][1]["team"]["id"]]

        if "Missing" in teams:
            continue

        if teams.index(team_id) <= 1:
            wins += int(red["score"] > blue["score"])
            scores.append(red["score"])
        else:
            wins += int(red["score"] < blue["score"])
            scores.append(blue["score"])

    winrate = round(min(100.0, 100 * wins / total_matches / WINRATE))
    print(f"Wins: {wins} out of {total_matches} matches ({round(100 * wins / total_matches, 1)}%)")

    median_score = round(statistics.median(scores))
    print(f"Median Score: {median_score}")
    median_score = round(min(100.0, 100 * median_score / MEDIAN))


    awp = 0
    ap = 0.0

    response = requests.get(f"{URL}/teams/{team_id}/rankings", headers=HEADERS,
                            params={"season": SEASON})
    data = response.json()

    if not data.get("data"):
        print("No events found.")
        return

    for ranking in data["data"]:
        awp += ranking["wp"] - 2 * ranking["wins"] - ranking["ties"]
        ap += ranking["ap"] / AUTONWIN

    awp = min(total_quals, awp)
    print(f"AWP: {awp} over {total_quals} quals ({round(100 * awp / total_quals, 1)}%)")
    print(f"Auton Wins: {ap} over {total_quals} quals ({round(100 * ap / total_quals, 1)}%)")
    awp = round(min(100.0, 100 * awp / total_quals / AWPRATE))
    ap = round(min(100.0, 100 * ap / total_quals / AUTONRATE))
    auton = round(0.5 * ap + 0.5 * awp)


    awards = 0
    num = 0

    response = requests.get(f"{URL}/teams/{team_id}/awards", headers=HEADERS,
                            params={"season": SEASON})
    data = response.json()

    if data.get("meta").get("total") > 0:
        for award in data["data"]:
            num += 1
            awards += evaluateAward(award["title"], award["qualifications"])

    response = requests.get(f"{URL}/teams/{team_id}/events", headers=HEADERS,
                            params={"season": SEASON, "end": datetime.date.today().isoformat()})
    data = response.json()

    comps = data["meta"]["total"]

    print(f"Awards Won: {num}")
    print(f"Judged Awards Valuation: {awards} over {comps} competition{"s" if comps > 1 else ""}")
    awards = min(100, round(100 * awards / (comps * AWARDRATE)))


    print(f"\nSkills: {skills}")
    print(f"Matches: {winrate}")
    print(f"Driving: {median_score}")
    print(f"Auton: {auton}")
    print(f"Judging: {awards}")
    overall = round(0.4 * skills + 0.2 * winrate + 0.2 * median_score + 0.1 * auton + 0.1 * awards)
    print(f"\nOverall: {overall}")
