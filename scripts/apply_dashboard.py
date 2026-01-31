import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

GRAFANA_URL = os.getenv("GRAFANA_URL")
TOKEN = os.getenv("GRAFANA_API_TOKEN")

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Path to dashboard JSON
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dashboard_path = os.path.join(BASE_DIR, "..", "dashboards", "node-exporter.json")

with open(dashboard_path, "r") as f:
    data = json.load(f)

payload = {
    "dashboard": data["dashboard"],
    "overwrite": True
}

url = f"{GRAFANA_URL}/api/dashboards/db"

response = requests.post(url, headers=headers, json=payload)

if response.status_code in [200, 201]:
    print("Dashboard applied successfully.")
else:
    print("Error:", response.status_code, response.text)
