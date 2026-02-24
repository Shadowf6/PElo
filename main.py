import os
import dotenv
import requests

dotenv.load_dotenv()
API_KEY = os.getenv("API_KEY")
URL = "https://www.robotevents.com/api/v2"

response = requests.get(URL)
print("Starting...")
print(f"Status Code: {response.status_code}")
