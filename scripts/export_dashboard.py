import os
import requests
from dotenv import load_dotenv

load_dotenv()

GRAFANA_URL = os.getenv("GRAFANA_URL")
TOKEN = os.getenv("GRAFANA_API_TOKEN")

DASHBOARD_UID = "rYdddlPWk"
print("TOKEN:", TOKEN)
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

url = f"{GRAFANA_URL}/api/dashboards/uid/{DASHBOARD_UID}"

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()

    with open("../dashboards/node-exporter.json", "w") as f:
        import json
        json.dump(data, f, indent=2)

    print("Dashboard exported successfully.")
else:
    print("Error:", response.status_code, response.text)
