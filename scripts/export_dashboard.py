import os
import requests
import json
import subprocess
import hashlib
import re
from dotenv import load_dotenv

load_dotenv()

# ---------- PATH SETUP ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(BASE_DIR, "..")
DASHBOARD_PATH = os.path.join(PROJECT_ROOT, "dashboards", "node-exporter.json")

# ---------- ENV ----------
GRAFANA_URL = os.getenv("GRAFANA_URL")
TOKEN = os.getenv("GRAFANA_API_TOKEN")
DASHBOARD_UID = "rYdddlPWk"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# ---------- HELPERS ----------
def file_hash(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def run_git(cmd):
    subprocess.run(cmd, cwd=PROJECT_ROOT, check=True)

def get_next_version():
    result = subprocess.run(
        ["git", "log", "--pretty=%s"],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT
    )
    versions = re.findall(r'v(\d+)', result.stdout)
    if versions:
        return f"v{int(versions[0]) + 1}"
    return "v1"

# ---------- EXPORT ----------
url = f"{GRAFANA_URL}/api/dashboards/uid/{DASHBOARD_UID}"
response = requests.get(url, headers=headers)

if response.status_code != 200:
    print("Error:", response.status_code, response.text)
    exit(1)

data = response.json()

old_hash = file_hash(DASHBOARD_PATH)

with open(DASHBOARD_PATH, "w") as f:
    json.dump(data, f, indent=2)

new_hash = file_hash(DASHBOARD_PATH)

# ---------- VERSIONING ----------
if old_hash != new_hash:
    print("Change detected. Creating new version...")

    version = get_next_version()

    try:
        run_git(["git", "add", DASHBOARD_PATH])
        run_git(["git", "commit", "-m", f"{version} Dashboard update"])
        run_git(["git", "tag", version])
        print(f"Committed as {version}")
    except Exception as e:
        print("Git commit failed:", e)
else:
    print("No dashboard changes detected.")
