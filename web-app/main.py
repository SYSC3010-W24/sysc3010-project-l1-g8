import json
import datetime as dt
from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    url_for,
    session,
    redirect,
)
import pyrebase
import secrets
import string


PORT: int = 8000
FIREBASE_CONFIG: str = "firebase_config.json"
MAX_TIMEOUT: int = 14400  # Four hours, in seconds
MAX_TEMP_THRESH: int = 100  # Degrees Celsius
MAX_SMOKE_THRESH: int = 10000  # PPM
NUM_SAMPLES_PLOTTED: int = 10


alphabet = string.ascii_letters + string.digits + "!@#$%^&*(-_=+)"
secret_key = "".join(secrets.choice(alphabet) for _ in range(24))


# Initialize DB connection
with open(FIREBASE_CONFIG, "r") as file:
    config = json.load(file)
firebase = pyrebase.initialize_app(config)
db = firebase.database()

app = Flask(__name__)
app.secret_key = secret_key


def timestamp_just_time(timestamp: str) -> str:
    """Returns just the time portion of an ISO timestamp."""
    # Remove the last two fractions of a second as well
    return timestamp.split("T")[-1][:-2]


# HTML Pages
@app.route("/", methods=["GET"])
def home():
    """Renders the home page of the website."""
    # Get temperature data from Firebase

    latest_temperature = list(
        db.child("sensordata/temperature")
        .order_by_key()
        .limit_to_last(1)
        .get()
        .val()
        .values()
    )
    latest_smoke = list(
        db.child("sensordata/smoke")
        .order_by_key()
        .limit_to_last(1)
        .get()
        .val()
        .values()
    )

    # Get emergency flag from Firebase
    emergency_flag = db.child("emergency").get().val()

    # Check if the user is logged in
    if "email" in session:
        user_email = session["email"]
        user_ref = db.child("users").child(user_email.replace(".", ",")).get()
        user_data = user_ref.val()
        full_username = user_data["Name"] if "Name" in user_data else "User"

        # Extract the first part of the username before a space
        username_parts = full_username.split()
        username = username_parts[0] if username_parts else "User"

    # Takes the user to the home page upon login
    if "logged_in" in session:

        return render_template(
            "index.html",
            current_temperature=round(latest_temperature[-1], 2),
            emergency_flag=emergency_flag,
            current_smoke=round(latest_smoke[-1], 2),
            full_username=full_username,
            username=username,
            user_email=user_email,
        )

    else:
        return redirect(url_for("signup"))


@app.route("/settings", methods=["GET"])
def settings():
    """Renders the settings page of the website."""
    # Get thresholds data from firebase
    temperature_threshold = (
        db.child("thresholds").child("temperature").get().val()
    )
    smoke_threshold = db.child("thresholds").child("smoke").get().val()

    # Check if the user is logged in
    if "email" in session:
        user_email = session["email"]
        user_ref = db.child("users").child(user_email.replace(".", ",")).get()
        user_data = user_ref.val()
        full_username = user_data["Name"] if "Name" in user_data else "User"

        # Extract the first part of the username before a space
        username_parts = full_username.split()
        username = username_parts[0] if username_parts else "User"

    return render_template(
        "settings.html",
        temperature_threshold=temperature_threshold,
        smoke_threshold=smoke_threshold,
        full_username=full_username,
        username=username,
        user_email=user_email,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    """Handles user login."""
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Replace dots with commas in the email for Firebase query
        email_key = email.replace(".", ",")

        # Check if the user exists and the password is correct
        user_ref = db.child("users").child(email_key).get()

        if user_ref.val():
            user_data = user_ref.val()
            if "Password" in user_data and user_data["Password"] == password:
                # Store user's email in the session and mark as logged in
                session["email"] = email
                session["logged_in"] = True
                # Redirect to the home page after successful login
                return redirect(url_for("home"))
            else:
                # Show an error message for incorrect password
                return render_template(
                    "login.html", error_message="Incorrect password"
                )
        else:
            # Show an error message for user not found
            return render_template("login.html", error_message="User not found")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Handles user signup"""

    if request.method == "POST":
        # Get account information from the form
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        phone_number = request.form.get("phone_number")

        # Check if all required fields are provided
        if not username or not email or not phone_number:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Account info required",
                    }
                ),
                400,
            )

        # Check if the username or email is already taken
        user_ref = db.child("users").child(email.replace(".", ",")).get().val()

        if user_ref:
            return (
                jsonify({"success": False, "message": "Email already taken"}),
                409,
            )

        # Create a new user in the database
        user_data = {
            "Name": username,
            "Password": password,
            "Phone Number": phone_number,
        }
        db.child("users").child(email.replace(".", ",")).set(user_data)

        # Redirect to home page after successful signup
        return redirect(url_for("home"))

    # Show signup page for GET requests
    return render_template("signup.html")


@app.route("/logout", methods=["GET"])
def logout():
    """
    Logs out the user by clearing the
    session and redirects to the login page."""
    session.clear()
    return redirect("/login")


@app.route("/api/deactivate", methods=["GET"])
def deactivate_alarm():
    """Deactivates the alarm flag in Firebase to
    signal the emergency is over."""
    db.child("emergency").set(False)
    return jsonify(success=True), 200


@app.route("/api/emergency", methods=["GET"])
def emergency_status():
    """
    Returns the status of the emergency flag in the Firebase database.
    """
    return {"status": db.child("emergency").get().val()}, 200


@app.route("/api/timeout/<duration>", methods=["GET"])
def set_timeout(duration: str):
    """Sets a timeout duration in Firebase."""
    # Convert duration number to an integer
    numeric_duration = int(duration)

    # Check if duration is within limit
    if numeric_duration > MAX_TIMEOUT:
        return (
            jsonify(
                success=False,
                message=f"Timeout must be less than {MAX_TIMEOUT} seconds!",
            ),
            400,
        )

    elif numeric_duration <= 0:
        return (
            jsonify(
                success=False, message="Timeout must be longer than 0 seconds!"
            ),
            400,
        )

    # Get timestamp for timeout
    # Remove . because Firebase doesn't allow it
    timestamp = dt.datetime.now().isoformat().replace(".", "+")
    db.child("timeout").child(timestamp).set(numeric_duration)

    return jsonify(success=True), 200


@app.route("/api/tempdata", methods=["GET"])
def get_temperature():
    """Gets the latest temperature time series data
    and returns it in JSON format."""
    temp_data = (
        db.child("sensordata/temperature")
        .order_by_key()
        .limit_to_last(10)
        .get()
        .val()
    )
    timestamps = list(temp_data.keys())
    values = list(temp_data.values())

    return {
        "timestamps": [timestamp_just_time(t) for t in timestamps],
        "vals": values,
    }, 200


@app.route("/api/smoke", methods=["GET"])
def get_smoke():
    """Gets the latest temperature time series data
    and returns it in JSON format."""
    smoke_data = (
        db.child("sensordata/smoke")
        .order_by_key()
        .limit_to_last(10)
        .get()
        .val()
    )
    timestamps = list(smoke_data.keys())
    values = list(smoke_data.values())

    return {
        "timestamps": [timestamp_just_time(t) for t in timestamps],
        "vals": values,
    }, 200


@app.route("/api/tempthresh/<degrees>", methods=["GET"])
def set_temperature_threshold(degrees: str):
    """Sets the temperature threshold in Firebase."""

    numeric_degrees = int(degrees)

    if numeric_degrees > MAX_TEMP_THRESH:
        return (
            jsonify(
                success=False,
                message=f"Temp. threshold must be < {MAX_TEMP_THRESH}°C",
            ),
            400,
        )

    elif numeric_degrees <= 0:
        return (
            jsonify(
                success=False,
                message="Temp threshold must be > 0 degrees!",
            ),
            400,
        )

    db.child("thresholds/temperature").set(numeric_degrees)

    return jsonify(success=True), 200


@app.route("/api/smokethresh/<ppm>", methods=["GET"])
def set_smoke_threshold(ppm: str):
    """Sets the smoke threshold in Firebase."""

    numeric_ppm = int(ppm)

    if numeric_ppm > MAX_SMOKE_THRESH:
        return (
            jsonify(
                success=False,
                message=f"Smoke threshold must be < {MAX_SMOKE_THRESH} ppm!",
            ),
            400,
        )

    elif numeric_ppm <= 0:
        return (
            jsonify(
                success=False,
                message="Smoke threshold must be higher than 0 ppm!",
            ),
            400,
        )

    db.child("thresholds/smoke").set(numeric_ppm)

    return jsonify(success=True), 200


@app.route("/add_user", methods=["POST"])
def add_user():
    """Adds a new user to the Firebase database."""
    user_data = {
        "Name": request.form.get("name"),
        "Password": request.form.get("password"),
        "Phone Number": request.form.get("phone_number"),
        "Email": request.form.get("email"),
    }
    email = request.form.get("email")

    db.child("users").child(email).set(user_data)

    return render_template("settings.html")


if __name__ == "__main__":
    app.run("0.0.0.0", port=PORT, debug=True)
