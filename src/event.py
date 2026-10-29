import copy
import requests
import json
import os
import sys
import re
import time
from datetime import date, datetime

import consts
from consts import *
from team import *
from match import *

round_order = {"Qual": 0, "R32": 1, "R16": 2, "QF": 3, "SF": 4, "Final": 5}


def apiGet(url: str, cache: str = None, use_cache: bool = False, **kwargs) -> dict:
    if use_cache and os.path.exists(cache):
        try:
            with open(cache) as f:
                return json.load(f)
        except json.decoder.JSONDecodeError:
            pass

    delay = 1
    while True:
        started = time.monotonic()
        response = requests.get(url, headers=HEADERS, **kwargs)
        try:
            if response.status_code == 200:
                data = response.json()
                if cache:
                    os.makedirs(os.path.dirname(cache), exist_ok=True)
                    with open(f"{cache}.tmp", "w") as f:
                        json.dump(data, f)
                    os.replace(f"{cache}.tmp", cache)
                remaining = response.headers.get("x-ratelimit-remaining")
                gap = 10 if remaining is not None and int(remaining) < 7 else 0.6
                time.sleep(max(0.0, gap - (time.monotonic() - started)))
                return data
        except json.decoder.JSONDecodeError:
            pass

        time.sleep(delay)
        delay = min(delay * 2, 120)


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
        data = apiGet(f"{URL}/events",
                      params={"season": SEASON, "page": page, "start": start, "end": end, "per_page": 250})

        if not data.get("data"):
            print("Invalid time period.")
            return

        total = data["meta"]["total"]
        for event in data["data"]:
            events.append(event)

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
        processEvent(events[e])

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
    data = apiGet(f"{URL}/events", params={"sku": event_code})

    if not data.get("data"):
        print("Invalid event code.")
        return

    active, inactive = copy.deepcopy(consts.active), copy.deepcopy(consts.inactive)
    processEvent(data["data"][0])
    consts.active, consts.inactive = active, inactive
    updateElos()


def processEvent(data: dict):
    event_id = data["id"]
    event = {
        "Name": "",
        "Link": "",
        "Date": "",
        "Region": "",
        "Type": "",
        "Divisions": []
    }

    consts.inactive.clear()

    event["Name"] = data["name"]
    event["Link"] = f"https://events.vex.com/robot-competitions/vex-robotics-competition/{data["sku"]}.html"
    event["Date"] = f"{data["start"][:10]} to {data["end"][:10]}"
    event["Region"] = f"{f"{data["location"]["region"]}, " if data["location"]["region"] is not None else ""}{data["location"]["country"]}"

    if data["event_type"] == "league":
        event["Type"] = "League"
    elif data["level"] == "Other":
        event["Type"] = "Local Event"
    elif data["level"] == "Signature":
        event["Type"] = "Signature Event"
    elif data["level"] == "State" or data["level"] == "Regional":
        event["Type"] = "Regional Championship"
    elif data["level"] == "National" or data["level"] == "USO":
        event["Type"] = "National Championship"
    elif data["level"] == "Spotlight":
        event["Type"] = "Spotlight Event"
    elif data["level"] == "World":
        event["Type"] = "World Championship"

    finished = data["end"][:10] < date.today().isoformat()
    divisions = [(d["id"], d["name"]) for d in data.get("divisions") or []] or [(1, "")]

    event_type = 1
    if data["level"] != "Other":
        event_type = 2
    elif data["event_type"] == "league":
        event_type = 3

    start_date = data["start"][:10]
    start = datetime.strptime(start_date, "%Y-%m-%d")

    last = datetime.strptime(consts.active["last"], "%Y-%m-%d")
    since = (start - last).days

    r = []

    for t in consts.active["teams"]:
        consts.active["teams"][t] += since
        if consts.active["teams"][t] >= INACTIVITY:
            r.append(t)

    for t in r:
        del consts.active["teams"][t]

    consts.active["last"] = start_date

    for div, div_name in divisions:
        page = 1
        division = {"Name": div_name, "Matches": []}
        pending = []

        while True:
            data = apiGet(f"{URL}/events/{event_id}/divisions/{div}/matches",
                          cache=f"cache/{event_id}_{div}_{page}.json", use_cache=finished,
                          params={"page": page, "per_page": 250})

            if not data.get("data"):
                break

            for match in data["data"]:
                red = match["alliances"][1]
                blue = match["alliances"][0]

                if match["round"] == 1 or (len(red["teams"]) != 2 or len(blue["teams"]) != 2):
                    continue

                evaluate = not (3 <= match["round"] <= 7 and (red["score"] == 0 or blue["score"] == 0))

                teams = [red["teams"][0]["team"]["name"], red["teams"][1]["team"]["name"],
                         blue["teams"][0]["team"]["name"], blue["teams"][1]["team"]["name"]]
                if "Missing" in teams:
                    continue

                num, instance = match["matchnum"], match["instance"]
                name = ""
                match match["round"]:
                    case 2:
                        name = f"Qual {num}"
                    case 3:
                        name = f"QF {instance}-{num}"
                    case 4:
                        name = f"SF {instance}-{num}"
                    case 5:
                        name = f"Final {instance}-{num}"
                    case 6:
                        name = f"R16 {instance}-{num}"
                    case 7:
                        name = f"R32 {instance}-{num}"

                pending.append((teams, red["score"], blue["score"], event_type, match["round"], name, evaluate))

            if page >= data["meta"]["last_page"]:
                break
            page += 1

        pending.sort(key=lambda p: (round_order.get(p[5].split()[0], 99), *map(int, p[5].split()[1].split("-"))))

        for p in pending:
            division["Matches"].append(processMatch(*p))

        if division["Matches"]:
            event["Divisions"].append(division)

    if len(event["Divisions"]) != 0:
        consts.events.append(event)
