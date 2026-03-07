import requests
import json
import sys
import consts
from consts import *
from team import *

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
            events.append(event["id"])

            ratio = i / total
            filled = int(50 * ratio)
            bar = "█" * filled + "-" * (50 - filled)
            sys.stdout.write(f"\r|{bar}| {min(total,i)}/{total}")
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
        sys.stdout.write(f"\r|{bar}| {e+1}/{len(events)}")
        sys.stdout.flush()

    print()
    updateTeams()

def processEventByCode(event_code: str) -> None:
    response = requests.get(f"{URL}/events", headers=HEADERS, params={"sku": event_code})
    data = response.json()

    if data.get("data"):
        processEventByID(data["data"][0]["id"])
        updateTeams()

def processEventByID(event_id: int) -> None:
    response = requests.get(f"{URL}/events/{event_id}/teams", headers=HEADERS,
                            params={"page": 1, "per_page": 250})
    data = response.json()

    if not data.get("data"):
        return

    for team in data["data"]:
        if team["number"] not in consts.TEAMS:
            consts.TEAMS[team["number"]] = 1000
