import requests
import json

import consts
from consts import *
from eval import *
from team import *
from event import *

if __name__ == "__main__":
    response = requests.get(URL, headers=HEADERS)
    print(f"Status Code: {response.status_code}")

    if response.status_code != 200:
        print("API is currently down.")
        exit(0)

    with open("../data/elos.json", "r") as f:
        consts.elos = json.load(f)

    with open("../data/active.json", "r") as f:
        consts.active = json.load(f)

    while True:
        print("\nMenu:\n"
              "1. Save and Leave\n"
              "2. Search Team\n"
              "3. Analyze Team\n"
              "4. Reset Elos\n"
              "5. Process Events (Timestamp)\n"
              "6. Process Event (by SKU)\n"
              "7. Create Team Rankings\n"
              "8. Simulate Match")

        option = int(input("Enter option: "))

        match option:
            case 1:
                sortElos()
                exit(0)
            case 2:
                num = input("Enter team number: ")
                searchTeam(num)
            case 3:
                num = input("Enter team number: ")
                evaluateTeam(num)
            case 4:
                confirm = input("Enter \"Yes\" to confirm. ")
                if confirm == "Yes":
                    resetElos()
                else:
                    print("Cancelled.")
            case 5:
                start = input("Enter start date (YYYY-MM-DD): ")
                end = input("Enter end date (YYYY-MM-DD): ")

                if start and end:
                    updateEvents(start, end)
                elif start and not end:
                    updateEvents(start, f"{YEAR}-12-31")
                elif end and not start:
                    updateEvents(f"{YEAR-1}-01-01", end)
                else:
                    updateEvents(f"{YEAR-1}-01-01", f"{YEAR}-12-31")
            case 6:
                code = input("Enter event code: ")
                processEventByCode(code.strip())
            case 7:
                createTeamRankings()
            case 8:
                r1 = input("Red 1: ")
                r2 = input("Red 2: ")
                b1 = input("Blue 1: ")
                b2 = input("Blue 2: ")
                red_score = int(input("Red Score: "))
                blue_score = int(input("Blue Score: "))
                simulateMatch(r1, r2, b1, b2, red_score, blue_score)
            case _:
                print("Invalid number.")

        input("\nPress enter to continue.")
