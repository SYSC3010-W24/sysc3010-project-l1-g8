import json
import datetime as dt
from flask import Flask, jsonify, render_template
import pyrebase

PORT: int = 8000
FIREBASE_CONFIG: str = "firebase_config.json"
MAX_TIMEOUT: int = 14400  # Four hours, in seconds
NUM_SAMPLES_PLOTTED: int = 10

# Initialize DB connection
with open(FIREBASE_CONFIG, "r") as file:
    config = json.load(file)
firebase = pyrebase.initialize_app(config)
db = firebase.database()

app = Flask(__name__)


def timestamp_just_time(timestamp: str) -> str:
    """Returns just the time portion of an ISO timestamp."""
    # Remove the last two fractions of a second as well
    return timestamp.split("T")[-1][:-2]


# HTML Pages
@app.route("/", methods=["GET"])
def home():
    """Renders the home page of the website."""
    # Get temperature data from Firebase

    latest_temperature = list(db.child("sensordata/temperature").order_by_key().limit_to_last(1).get().val().values())
    latest_smoke = list(db.child("sensordata/smoke").order_by_key().limit_to_last(1).get().val().values())

    # Get emergency flag from Firebase
    emergency_flag = db.child("emergency").get().val()
    color_class = "fire" if emergency_flag else "no-fire"
    return render_template(
        "index.html",
        current_temperature=round(latest_temperature[-1], 2),
        emergency_flag=emergency_flag,
        color_class=color_class,
        current_smoke=round(latest_smoke[-1], 2),
    )


@app.route("/settings", methods=["GET"])
def settings():
    """Renders the settings page of the website."""
    # Get thresholds data from firebase
    temperature_threshold = db.child("thresholds").child("temperature").get().val()
    smoke_threshold = db.child("thresholds").child("smoke").get().val()
    return render_template(
        "settings.html", temperature_threshold=temperature_threshold, smoke_threshold=smoke_threshold
    )


@app.route("/login", methods=["GET"])
def login():
    """Renders the login page of the website."""
    return render_template("login.html")


@app.route("/signup", methods=["GET"])
def sign_up():
    """Renders the sign up page of the website."""
    return render_template("sign-up.html")


@app.route("/api/deactivate", methods=["GET"])
def deactivate_alarm():
    """Deactivates the alarm flag in Firebase to signal the emergency is over."""
    db.child("emergency").set(False)
    return jsonify(success=True), 200


@app.route("/api/timeout/<duration>", methods=["GET"])
def set_timeout(duration: str):
    """Sets a timeout duration in Firebase."""

    numeric_duration = int(duration)

    if numeric_duration > MAX_TIMEOUT:
        return jsonify(success=False, message=f"Timeout must be less than {MAX_TIMEOUT} seconds!"), 400

    elif numeric_duration <= 0:
        return jsonify(success=False, message="Timeout must be longer than 0 seconds!"), 400

    timestamp = dt.datetime.now().isoformat().replace(".", "+")  # Remove . because Firebase doesn't allow it
    db.child("timeout").child(timestamp).set(numeric_duration)

    return jsonify(success=True), 200


@app.route("/api/tempdata", methods=["GET"])
def get_temperature():
    """Gets the latest temperature time series data and returns it in JSON format."""
    temp_data = db.child("sensordata/temperature").order_by_key().limit_to_last(10).get().val()
    timestamps = list(temp_data.keys())
    values = list(temp_data.values())

    return {"timestamps": [timestamp_just_time(t) for t in timestamps], "vals": values}, 200


@app.route("/api/smoke", methods=["GET"])
def get_smoke():
    """Gets the latest temperature time series data and returns it in JSON format."""
    smoke_data = db.child("sensordata/smoke").order_by_key().limit_to_last(10).get().val()
    timestamps = list(smoke_data.keys())
    values = list(smoke_data.values())

    return {"timestamps": [timestamp_just_time(t) for t in timestamps], "vals": values}, 200


if __name__ == "__main__":
    app.run("0.0.0.0", port=PORT, debug=True)
