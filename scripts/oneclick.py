import subprocess
import os
import sys
import json
import re
import argparse

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
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {' '.join(cmd)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

# ---------- GIT ----------
def get_commits():
    result = run(
        ["git", "log", "--pretty=format:%h %s"],
        capture=True
    )

    commits = []

    for line in result.stdout.splitlines():
        parts = line.split(" ", 1)
        if len(parts) < 2:
            continue

        commit_hash, message = parts

        # Only keep dashboard versions like v1, v2, v10 etc
        if re.search(r"\bv\d+\b", message, re.IGNORECASE):
            commits.append(f"{commit_hash} {message}")

    return commits

# ---------- DASHBOARD ----------
def fetch_dashboard(commit):
    result = run(
        ["git", "show", f"{commit}:{DASHBOARD_FILE}"],
        capture=True
    )

    if not result.stdout.strip():
        print("Dashboard file not found in this commit.", file=sys.stderr)
        sys.exit(1)

    try:
        json.loads(result.stdout)
    except json.JSONDecodeError:
        print("Invalid dashboard JSON in commit.", file=sys.stderr)
        sys.exit(1)

    with open(TEMP_FILE, "w") as f:
        f.write(result.stdout)

def apply_dashboard():
    run(["python3", os.path.join("scripts", "apply_dashboard.py")])

def apply_version(commit):
    fetch_dashboard(commit)
    final_path = os.path.join(PROJECT_ROOT, DASHBOARD_FILE)
    os.replace(TEMP_FILE, final_path)
    apply_dashboard()

# ---------- CLI INTERACTIVE ----------
def choose_commit(commits):
    print("\nAvailable Dashboard Versions:\n")
    for i, c in enumerate(commits):
        print(f"{i+1}. {c}")

    try:
        choice = int(input("\nSelect version number: ")) - 1
        return commits[choice].split()[0]
    except Exception:
        print("Invalid selection.", file=sys.stderr)
        sys.exit(1)

def interactive_mode():
    print("\n--- Grafana One-Click Rollback ---")

    commits = get_commits()
    if not commits:
        print("No versioned dashboard commits found.")
        sys.exit(0)

    commit_id = choose_commit(commits)
    apply_version(commit_id)

    print("\nDashboard updated successfully.")

# ---------- ENTRY POINT ----------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Grafana GitOps Dashboard Manager")
    parser.add_argument("--list", action="store_true", help="List dashboard versions")
    parser.add_argument("--apply", type=str, help="Apply a dashboard version by commit hash")

    args = parser.parse_args()

    # Backend / API mode
    if args.list:
        commits = get_commits()
        for c in commits:
            print(c)
        sys.exit(0)

    if args.apply:
        apply_version(args.apply)
        print(f"Applied version {args.apply}")
        sys.exit(0)

    # CLI interactive fallback
    interactive_mode()
