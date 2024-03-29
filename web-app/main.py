from flask import Flask, jsonify, render_template
import pyrebase
import json

PORT: int = 8000
FIREBASE_CONFIG: str = "firebase_config.json"

# Initialize DB connection
with open(FIREBASE_CONFIG, "r") as file:
    config = json.load(file)
firebase = pyrebase.initialize_app(config)
db = firebase.database()

app = Flask(__name__)


# HTML Pages
@app.route("/", methods=["GET"])
def home():
    """Renders the home page of the website."""
    # Get temperature data from Firebase

    latest_temperature = list(db.child("sensordata/temperature").order_by_key().limit_to_last(10).get().val().values())
    latest_smoke = list(db.child("sensordata/smoke").order_by_key().limit_to_last(10).get().val().values())

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
    return jsonify(success=True)


if __name__ == "__main__":
    app.run("0.0.0.0", port=PORT, debug=True)
