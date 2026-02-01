import subprocess
import os
import sys
import json
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(BASE_DIR, "..")
DASHBOARD_FILE = "dashboards/node-exporter.json"
TEMP_FILE = os.path.join(PROJECT_ROOT, "dashboards", "temp.json")

# ---------- UTILS ----------
def run(cmd, capture=False):
    try:
        if capture:
            return subprocess.run(
                cmd,
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True
            )
        else:
            subprocess.run(cmd, cwd=PROJECT_ROOT, check=True)
    except subprocess.CalledProcessError:
        print(f"\nCommand failed: {' '.join(cmd)}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)

# ---------- GIT ----------
def get_commits():
    result = run(
        ["git", "log", "--pretty=format:%h %s"],
        capture=True
    )

    if result.returncode != 0:
        print("Failed to read git history.")
        sys.exit(1)

    commits = []

    for line in result.stdout.splitlines():
        # line example: "88e7c73 v4 Dashboard update"
        parts = line.split(" ", 1)
        if len(parts) < 2:
            continue

        commit_hash = parts[0]
        message = parts[1]

        # keep only messages containing v<number>
        if re.search(r'\bv\d+\b', message, re.IGNORECASE):
            commits.append(f"{commit_hash} {message}")

    if not commits:
        print("No versioned dashboard commits found.")
        sys.exit(1)

    return commits

# ---------- INPUT ----------
def choose_commit(commits):
    print("\nAvailable Dashboard Versions:\n")
    for i, c in enumerate(commits):
        print(f"{i+1}. {c}")

    try:
        choice = int(input("\nSelect version number: ")) - 1
        if choice < 0 or choice >= len(commits):
            raise ValueError
        return commits[choice].split()[0]
    except ValueError:
        print("Invalid selection. Exiting.")
        sys.exit(1)

# ---------- FETCH ----------
def fetch_dashboard(commit):
    print(f"\nFetching dashboard from {commit}...")

    result = run(
        ["git", "show", f"{commit}:{DASHBOARD_FILE}"],
        capture=True
    )

    if result.returncode != 0 or not result.stdout.strip():
        print("Dashboard file not found in this version.")
        sys.exit(1)

    try:
        json.loads(result.stdout)  # Validate JSON
    except json.JSONDecodeError:
        print("Corrupted dashboard JSON in this commit.")
        sys.exit(1)

    try:
        with open(TEMP_FILE, "w") as f:
            f.write(result.stdout)
    except IOError:
        print("Failed to write temporary dashboard file.")
        sys.exit(1)

# ---------- APPLY ----------
def apply_dashboard():
    print("Applying dashboard...")
    run(["python3", os.path.join("scripts", "apply_dashboard.py")])

# ---------- MAIN ----------
def main():
    print("\n--- Grafana One-Click Rollback ---")

    commits = get_commits()
    commit_id = choose_commit(commits)

    fetch_dashboard(commit_id)

    final_path = os.path.join(PROJECT_ROOT, DASHBOARD_FILE)

    if not os.path.exists(TEMP_FILE):
        print("Temporary dashboard file missing.")
        sys.exit(1)

    try:
        os.replace(TEMP_FILE, final_path)
    except IOError:
        print("Failed to replace dashboard file.")
        sys.exit(1)

    apply_dashboard()

    print("\nDashboard updated successfully.")

if __name__ == "__main__":
    main()
