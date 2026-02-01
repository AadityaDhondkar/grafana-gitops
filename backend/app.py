from flask import Flask, jsonify, request
import subprocess
import os
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ======================
# Environment variables
# ======================
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
PYTHON_BIN = os.getenv("PYTHON_BIN", "python3")

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

EXPORT_SCRIPT = "scripts/export_dashboard.py"
ONECLICK_SCRIPT = "scripts/oneclick.py"

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

# ======================
# Routes
# ======================

@app.route("/api/export", methods=["POST"])
def export_dashboard():
    ok, out = run_script([PYTHON_BIN, EXPORT_SCRIPT])

    if not ok:
        return jsonify({
            "status": "error",
            "message": out
        }), 500

    # Detect no-change signal from script
    if "No changes detected" in out:
        return jsonify({
            "status": "no_change",
            "message": "No changes detected. Dashboard already up to date."
        })

    return jsonify({
        "status": "exported",
        "message": "Dashboard exported and versioned successfully."
    })


@app.route("/api/versions", methods=["GET"])
def versions():
    ok, out = run_script([PYTHON_BIN, ONECLICK_SCRIPT, "--list"])

    if not ok:
        return jsonify({
            "status": "error",
            "message": out
        }), 500

    versions = [line.strip() for line in out.splitlines() if line.strip()]

    return jsonify(versions)


@app.route("/api/rollback", methods=["POST"])
def rollback():
    data = request.get_json(silent=True) or {}
    version = data.get("version")

    if not version:
        return jsonify({
            "status": "error",
            "message": "Version is required"
        }), 400

    ok, out = run_script(
        [PYTHON_BIN, ONECLICK_SCRIPT, "--apply", version]
    )

    if not ok:
        return jsonify({
            "status": "error",
            "message": out
        }), 500

    return jsonify({
        "status": "success",
        "message": f"Rolled back to {version}"
    })


# ======================
# Entry point
# ======================
if __name__ == "__main__":
    app.run(host=FLASK_HOST, port=FLASK_PORT)
