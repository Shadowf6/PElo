import requests
import json
import sys
import time
import consts
from consts import *
from team import *
from match import *

# 1 Request
def updateEvents(start: str, end: str) -> None:
    print("\nGetting events....")

    events = []
    page = 1
    i = 1

    while True:
        response = requests.get(f"{URL}/events", headers=HEADERS,
                                params={"season": SEASON, "page": page, "start": start, "end": end, "per_page": 250})
        data = response.json()

        if not data.get("data"):
            print("Invalid time period.")
            return

        total = data["meta"]["total"]
        for event in data["data"]:
            if event["ongoing"]:
                i += 1
                continue

            events.append(event["id"])

            ratio = i / total
            filled = int(50 * ratio)
            bar = "█" * filled + "-" * (50 - filled)
            sys.stdout.write(f"\r|{bar}| {min(total, i)}/{total}")
            sys.stdout.flush()
            i += 1

        if page >= data["meta"]["last_page"]:
            break

        page += 1

    events = events[:total]

    print("\nProcessing events....")

    for e in range(len(events)):
        processEventByID(events[e])

        ratio = (e + 1) / len(events)
        filled = int(50 * ratio)
        bar = "█" * filled + "-" * (50 - filled)
        sys.stdout.write(f"\r|{bar}| {e + 1}/{len(events)}")
        sys.stdout.flush()

    print()
    updateTeams()

# 1 Request
def processEventByCode(event_code: str) -> None:
    response = requests.get(f"{URL}/events", headers=HEADERS, params={"sku": event_code})
    data = response.json()

    if not data.get("data"):
        print("Invalid event code.")
        return

    processEventByID(data["data"][0]["id"])
    updateTeams()

# 2 Requests
def processEventByID(event_id: int) -> None:
    response = requests.get(f"{URL}/events/{event_id}", headers=HEADERS)
    data = response.json()

    divisions = []
    for div in data["divisions"]:
        divisions.append(div["id"])

    event_type = 1
    if data["level"] != "Other":
        event_type = 2
    elif data["event_type"] == "league":
        event_type = 3

    for div in divisions:
        page = 1

        while True:
            response = requests.get(f"{URL}/events/{event_id}/divisions/{div}/matches", headers=HEADERS,
                                    params={"page": page, "per_page": 250})
            data = response.json()

            if not data.get("data"):
                return

            for match in data["data"]:
                red = match["alliances"][1]
                blue = match["alliances"][0]

                if (3 <= match["round"] < 6 and (red["score"] == 0 or blue["score"] == 0)
                        or match["round"] == 1
                        or (len(red["teams"]) != 2 or len(blue["teams"]) != 2)):
                    continue

                processMatch([red["teams"][0]["team"]["name"], red["teams"][1]["team"]["name"],
                              blue["teams"][0]["team"]["name"], blue["teams"][1]["team"]["name"]],
                             red["score"] - blue["score"], event_type, match["round"])

            if page >= data["meta"]["last_page"]:
                break

            page += 1
