import requests
import json
import datetime
import re
import consts
from consts import *
from team import *
from event import *

response = requests.get(URL, headers=HEADERS)

if __name__ == "__main__":
    print("Starting...")
    print(f"Status Code: {response.status_code}")

    with open("teams.json", "r") as f:
        consts.TEAMS = json.load(f)

    if response.status_code == 200:
        while True:
            print("\nMenu:\n"
                  "1. Leave\n"
                  "2. Search Team\n"
                  "3. Reset Elos\n"
                  "4. Update Elos")

            option = int(input("Enter option: "))

            if option == 1:
                exit(0)
            elif option == 2:
                num = input("Enter team number: ")
                searchTeam(num)
            elif option == 3:
                confirm = input("Enter 'Yes' to confirm. ")
                if confirm == "Yes":
                    resetTeams()
            elif option == 4:
                start = input("Enter start date (YYYY-MM-DD): ")
                end = input("Enter end date (YYYY-MM-DD): ")

                if (start and not bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", start))) or (end and not bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", end))):
                    print("Invalid format.")
                    continue

                if start and end:
                    updateEvents(start, end)
                elif start and not end:
                    updateEvents(start, f"{year}-12-31")
                elif end and not start:
                    updateEvents(f"{year - 1}-1-1", end)
                else:
                    updateEvents(f"{year - 1}-1-1", f"{year}-12-31")

            input("\nPress enter to continue.")
    else:
        print("API is currently down.")
        exit(0)
