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
def settings():
    """Renders the settings page of the website."""
    return render_template("settings.html")

@app.route("/login", methods=["GET"])
def login():
    """Renders the login page of the website."""
    return render_template("login.html")

@app.route("/signup", methods=["GET"])
def sign_up():
    """Renders the sign up page of the website."""
    return render_template("sign-up.html")

if __name__ == "__main__":
    app.run("0.0.0.0", port=PORT)
