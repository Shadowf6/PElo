import requests
import json
import sys
import consts
from consts import *

def updateEvents(start: str, end: str) -> None:
    print("\nGetting events....")

    events = []
    page = 1
    i = 1
    total = 0
    while True:
        response = requests.get(f"{URL}/events", headers=HEADERS, params={"season": pushback, "page": 1, "start": start, "end": end, "per_page": 250})
        data = response.json()

        if not data["data"]:
            print("Invalid time period.")
            return

        total = data["meta"]["total"]
        for event in data["data"]:
            events.append(event["id"])

            ratio = i / total
            filled = int(40 * ratio)
            bar = "█" * filled + "-" * (40 - filled)
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
        filled = int(40 * ratio)
        bar = "█" * filled + "-" * (40 - filled)
        sys.stdout.write(f"\r|{bar}| {e + 1}/{len(events)}")
        sys.stdout.flush()
    print("\nDone!")

def processEvent(event_id: int) -> None:
    pass
