from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from brain import think
from executor import execute
import datetime
import json
import os
import requests as req

app = Flask(__name__)
app.secret_key = "jarvis_secret_2025"

PERMS_FILE = "permissions.json"
USERS_FILE = "users.json"
commands_history = []

# ── Users load/save ────────────────────────────────────────

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {"riya": "riya1234", "admin": "admin123"}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

# ── Permissions load/save ─────────────────────────────────

def load_permissions():
    if os.path.exists(PERMS_FILE):
        with open(PERMS_FILE, "r") as f:
            return json.load(f)
    return {
        "file_system": False, "apps": False, "screenshot": False,
        "camera": False, "system_control": False, "web_search": False,
        "weather": True, "datetime": True, "reminders": False, "clipboard": False
    }

def save_permissions(data):
    with open(PERMS_FILE, "w") as f:
        json.dump(data, f)

# ── Routes ────────────────────────────────────────────────

@app.route("/")
def index():
    if "user" not in session:
        return redirect(url_for("login"))
    return redirect(url_for("dashboard"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "").strip()
        users = load_users()
        if username in users and users[username] == password:
            session["user"] = username
            perms = load_permissions()
            # Pehli baar login — permissions page dikhao
            if not any([perms["file_system"], perms["apps"], perms["screenshot"]]):
                return redirect(url_for("permissions"))
            return redirect(url_for("dashboard"))
        return render_template("login.html", error="Wrong username or password!")
    return render_template("login.html")

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username", "").strip().lower()
    password = data.get("password", "").strip()
    users = load_users()
    if not username or not password:
        return jsonify({"error": "Sab fields bharo!"}), 400
    if username in users:
        return jsonify({"error": "Username already exists!"}), 400
    if len(password) < 4:
        return jsonify({"error": "Password too short!"}), 400
    users[username] = password
    save_users(users)
    return jsonify({"success": True})

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/permissions", methods=["GET", "POST"])
def permissions():
    if "user" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        perms = {
            "file_system": "file_system" in request.form,
            "apps": "apps" in request.form,
            "screenshot": "screenshot" in request.form,
            "camera": "camera" in request.form,
            "system_control": "system_control" in request.form,
            "web_search": "web_search" in request.form,
            "weather": True,
            "datetime": True,
            "reminders": "reminders" in request.form,
            "clipboard": "clipboard" in request.form,
        }
        save_permissions(perms)
        return redirect(url_for("dashboard"))
    perms = load_permissions()
    return render_template("permissions.html", perms=perms)

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    perms = load_permissions()
    return render_template("dashboard.html", user=session["user"], perms=perms)

# ── Command Route ─────────────────────────────────────────

@app.route("/command", methods=["POST"])
def command():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.json
    user_input = data.get("text", "").lower().strip()
    perms = load_permissions()

    # ── Date & Time ──
    if any(w in user_input for w in ["time", "date", "day", "kitne baje", "aaj"]):
        now = datetime.datetime.now()
        response = f"Abhi {now.strftime('%I:%M %p')} baje hain aur aaj {now.strftime('%A, %d %B %Y')} hai!"
        _save_history(user_input, "datetime", response)
        return jsonify({"response": response, "action": "datetime"})

    # ── Weather ──
    if any(w in user_input for w in ["weather", "temperature", "mausam", "garmi", "sardi"]):
        try:
            r = req.get("https://wttr.in/Delhi?format=3", timeout=5)
            response = f"Delhi ka mausam: {r.text.strip()}"
        except:
            response = "Weather abhi nahi mil paya, internet check karo!"
        _save_history(user_input, "weather", response)
        return jsonify({"response": response, "action": "weather"})

    # ── Battery ──
    if any(w in user_input for w in ["battery", "charge"]) and perms.get("system_control"):
        try:
            import psutil
            battery = psutil.sensors_battery()
            plug = "charging" if battery.power_plugged else "not charging"
            response = f"Battery {round(battery.percent)}% hai aur {plug} hai!"
        except:
            response = "Battery info nahi mil paya!"
        _save_history(user_input, "battery", response)
        return jsonify({"response": response, "action": "battery"})

    # ── Reminder ──
    if any(w in user_input for w in ["remind", "timer", "minute", "minutes"]) and perms.get("reminders"):
        import re, threading
        nums = re.findall(r'\d+', user_input)
        minutes = int(nums[0]) if nums else 5
        def remind():
            import time
            time.sleep(minutes * 60)
        threading.Thread(target=remind, daemon=True).start()
        response = f"Theek hai! {minutes} minute mein remind karunga!"
        _save_history(user_input, "reminder", response)
        return jsonify({"response": response, "action": "reminder"})

    # ── Permission check & execute ──
    result = think(user_input)
    action = result.get("action", "unknown")
    params = result.get("params", {})
    response_text = result.get("response", "Ho gaya!")

    # Permission check
    perm_map = {
        "open_folder": "file_system", "create_file": "file_system", "delete_file": "file_system",
        "open_app": "apps", "take_screenshot": "screenshot",
        "open_camera": "camera", "close_camera": "camera",
        "volume_up": "system_control", "volume_down": "system_control", "mute": "system_control",
        "search_web": "web_search", "type_text": "clipboard",
    }

    required_perm = perm_map.get(action)
    if required_perm and not perms.get(required_perm):
        response_text = "Yeh kaam karne ki permission nahi hai! Dashboard mein Permissions se allow karo."
        return jsonify({"response": response_text, "action": "permission_denied"})

    if action != "unknown":
        execute(action, params)

    _save_history(user_input, action, response_text)
    return jsonify({"response": response_text, "action": action})

@app.route("/download/windows")
def download_windows():
    return jsonify({"message": "Coming soon! Executable build ho raha hai."})

@app.route("/history")
def history():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401
    return jsonify(commands_history)

@app.route("/get-permissions")
def get_permissions():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401
    return jsonify(load_permissions())

def _save_history(cmd, action, response):
    commands_history.append({
        "time": datetime.datetime.now().strftime("%H:%M:%S"),
        "command": cmd,
        "action": action,
        "response": response
    })
    if len(commands_history) > 20:
        commands_history.pop(0)

if __name__ == "__main__":
    app.run(debug=True, port=5000)