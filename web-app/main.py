from flask import Flask, render_template
import pyrebase
import json

PORT: int = 8000
CREDENTIALS: str = "./firebase_config.json"

# Initialize DB connection
with open(CREDENTIALS, "r") as file:
    config = json.load(file)
firebase = pyrebase.initialize_app(config)
db = firebase.database()

app = Flask(__name__)


# HTML Pages
@app.route("/", methods=["GET"])
def home():
    """Renders the home page of the website."""
    return render_template("index.html")


@app.route("/settings", methods=["GET"])
def reading():
    """Renders the settings page of the website."""
    return render_template("settings.html")


@app.route("/api/temperature", methods=["GET"])
def temperature_api():
    """Gets the latest temperature from Firebase."""

    temperature_data = db.child("sensordata/temperature").get().each()
    if temperature_data is None:
        return []

    return [{t.key(): t.val()} for t in temperature_data]


if __name__ == "__main__":
    app.run("0.0.0.0", port=PORT)
