import subprocess
import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(BASE_DIR, "..")
DASHBOARD_FILE = "dashboards/node-exporter.json"
TEMP_FILE = os.path.join(PROJECT_ROOT, "dashboards", "temp.json")

def run(cmd, capture=False):
    try:
        if capture:
            return subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True)
        else:
            subprocess.run(cmd, cwd=PROJECT_ROOT, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\nCommand failed: {' '.join(cmd)}")
        sys.exit(1)

def get_commits():
    result = run(["git", "log", "--pretty=format:%h %s"], capture=True)
    return result.stdout.splitlines()

def choose_commit(commits):
    print("\nAvailable Versions:\n")
    for i, c in enumerate(commits):
        print(f"{i+1}. {c}")

    choice = int(input("\nSelect version number: ")) - 1
    return commits[choice].split()[0]

def fetch_dashboard(commit):
    print(f"\nFetching dashboard from {commit}...")

    result = run(
        ["git", "show", f"{commit}:{DASHBOARD_FILE}"],
        capture=True
    )

    if result.returncode != 0 or not result.stdout:
        print("Dashboard file not found in this commit.")
        sys.exit(1)

    with open(TEMP_FILE, "w") as f:
        f.write(result.stdout)

def apply_dashboard():
    print("Applying dashboard...")
    run(["python3", os.path.join("scripts", "apply_dashboard.py")])

def main():
    print("\n--- Grafana One-Click Rollback ---")

    commits = get_commits()
    commit_id = choose_commit(commits)

    fetch_dashboard(commit_id)

    # Replace current dashboard JSON safely
    final_path = os.path.join(PROJECT_ROOT, DASHBOARD_FILE)
    os.replace(TEMP_FILE, final_path)

    apply_dashboard()

    print("\nDashboard updated successfully.")

if __name__ == "__main__":
    main()
