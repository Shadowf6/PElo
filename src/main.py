import requests
import json
import re
from consts import *
from team import *
from event import *

if __name__ == "__main__":
    response = requests.get(URL, headers=HEADERS)

    print("Starting...")
    print(f"Status Code: {response.status_code}")

    with open("../data/elos.json", "r") as f:
        consts.ELOS = json.load(f)

    if response.status_code == 200:
        while True:
            print("\nMenu:\n"
                  "1. Save and Leave\n"
                  "2. Search Team\n"
                  "3. Reset Elos\n"
                  "4. Process Events (Timestamp)\n"
                  "5. Process Event (by SKU)\n"
                  "6. Create Team Rankings\n"
                  "7. Simulate Match")

            option = int(input("Enter option: "))

            if option == 1:
                sortElos()
                exit(0)
            elif option == 2:
                num = input("Enter team number: ")
                searchTeam(num)
            elif option == 3:
                confirm = input("Enter \"Yes\" to confirm. ")
                if confirm == "Yes":
                    resetElos()
                else:
                    print("Cancelled.")
            elif option == 4:
                start = input("Enter start date (YYYY-MM-DD): ")
                end = input("Enter end date (YYYY-MM-DD): ")

                if ((start and not bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", start))) or
                        (end and not bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", end)))):
                    print("Invalid format.")
                    continue

                if start and end:
                    updateEvents(start, end)
                elif start and not end:
                    updateEvents(start, f"{YEAR}-12-31")
                elif end and not start:
                    updateEvents(f"{YEAR-1}-01-01", end)
                else:
                    updateEvents(f"{YEAR-1}-01-01", f"{YEAR}-12-31")
            elif option == 5:
                code = input("Enter event code: ")
                processEventByCode(code.strip())
            elif option == 6:
                createTeamRankings()
            elif option == 7:
                r1 = input("Red 1: ")
                r2 = input("Red 2: ")
                b1 = input("Blue 1: ")
                b2 = input("Blue 2: ")
                red_score = int(input("Red Score: "))
                blue_score = int(input("Blue Score: "))
                simulateMatch(r1, r2, b1, b2, red_score, blue_score)

            input("\nPress enter to continue.")
    else:
        print("API is currently down.")
        exit(0)
 