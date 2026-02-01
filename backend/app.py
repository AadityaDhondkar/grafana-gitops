from flask import Flask, jsonify, request
import subprocess
import os
from dotenv import load_dotenv
from flask_cors import CORS

# ======================
# Init
# ======================
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ======================
# Environment
# ======================
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
PYTHON_BIN = os.getenv("PYTHON_BIN", "python3")

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

EXPORT_SCRIPT = "scripts/export_dashboard.py"
ONECLICK_SCRIPT = "scripts/oneclick.py"

STATE_DIR = os.path.join(PROJECT_ROOT, "backend", "state")
STATE_FILE = os.path.join(STATE_DIR, "current_version.txt")
os.makedirs(STATE_DIR, exist_ok=True)

# ======================
# Helpers
# ======================
def run_script(args):
    result = subprocess.run(
        args,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return False, result.stderr.strip()

    return True, result.stdout.strip()


def get_current_version():
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE, "r") as f:
        return f.read().strip()


def set_current_version(version):
    with open(STATE_FILE, "w") as f:
        f.write(version)

# ======================
# Routes
# ======================

@app.route("/api/export", methods=["POST"])
def export_dashboard():
    ok, out = run_script([PYTHON_BIN, EXPORT_SCRIPT])

    if not ok:
        return jsonify({"status": "error", "message": out}), 500

    if "No changes detected" in out:
        return jsonify({
            "status": "no_change",
            "message": "No changes detected. Dashboard already up to date."
        })

    ok, head = run_script(["git", "rev-parse", "HEAD"])
    if ok:
        set_current_version(head.strip())

    return jsonify({
        "status": "exported",
        "message": "Dashboard exported and versioned successfully."
    })


@app.route("/api/versions", methods=["GET"])
def versions():
    ok, out = run_script([PYTHON_BIN, ONECLICK_SCRIPT, "--list"])

    if not ok:
        return jsonify({"status": "error", "message": out}), 500

    versions = []
    for line in out.splitlines():
        parts = line.strip().split(" ", 1)
        versions.append({
            "hash": parts[0],
            "label": line.strip()
        })

    return jsonify(versions)


@app.route("/api/current", methods=["GET"])
def current():
    return jsonify({"current": get_current_version()})


@app.route("/api/rollback", methods=["POST"])
def rollback():
    data = request.get_json(silent=True) or {}
    version = data.get("version")

    if not version:
        return jsonify({"status": "error", "message": "Version is required"}), 400

    ok, out = run_script([PYTHON_BIN, ONECLICK_SCRIPT, "--apply", version])

    if not ok:
        return jsonify({"status": "error", "message": out}), 500

    set_current_version(version)

    return jsonify({
        "status": "success",
        "message": f"Rolled back to {version}",
        "current": version
    })


# ======================
# Entry
# ======================
if __name__ == "__main__":
    app.run(host=FLASK_HOST, port=FLASK_PORT)
