import requests
import json
import sys
import re
import time
from datetime import datetime

import consts
from consts import *
from team import *
from match import *


def updateEvents(start: str, end: str):
    if ((start and not bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", start)))
            or (end and not bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", end)))):
        print("Invalid format.")
        return

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
    updateElos()

    with open("config.txt", "w") as f:
        consts.last_updated = end
        f.write(end)


def processEventByCode(event_code: str):
    response = requests.get(f"{URL}/events", headers=HEADERS, params={"sku": event_code})
    data = response.json()

    if not data.get("data"):
        print("Invalid event code.")
        return

    processEventByID(data["data"][0]["id"])
    updateElos()


def processEventByID(event_id: int):
    i = 0
    data = {}

    while True:
        response = requests.get(f"{URL}/events/{event_id}", headers=HEADERS)
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

    if not data.get("divisions"):
        return

    divisions = []
    for div in data["divisions"]:
        divisions.append(div["id"])

    event_type = 1
    if data["level"] != "Other":
        event_type = 2
    elif data["event_type"] == "league":
        event_type = 3

    start_date = data["start"][:10]
    end_date = data["end"][:10]

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    last = datetime.strptime(consts.active["last"], "%Y-%m-%d")
    since = (start - last).days

    remove = []

    for t in consts.active["teams"]:
        consts.active["teams"][t] += since
        if consts.active["teams"][t] >= INACTIVITY:
            remove.append(t)

    for t in remove:
        del consts.active["teams"][t]

    consts.active["last"] = start_date

    for div in divisions:
        page = 1

        while True:
            i = 0
            data = {}

            while True:
                response = requests.get(f"{URL}/events/{event_id}/divisions/{div}/matches", headers=HEADERS,
                                        params={"page": page, "per_page": 250})
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

            for match in data["data"]:
                red = match["alliances"][1]
                blue = match["alliances"][0]

                if ((3 <= match["round"] <= 7 and (red["score"] == 0 or blue["score"] == 0)
                        or match["round"] == 1
                        or (len(red["teams"]) != 2 or len(blue["teams"]) != 2))):
                    continue

                teams = [red["teams"][0]["team"]["name"], red["teams"][1]["team"]["name"],
                         blue["teams"][0]["team"]["name"], blue["teams"][1]["team"]["name"]]

                if "Missing" in teams:
                    continue

                processMatch(teams, red["score"], blue["score"], event_type, match["round"])

            if page >= data["meta"]["last_page"]:
                break

            page += 1
