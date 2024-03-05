from flask import Flask, render_template

PORT: int = 8000

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

if __name__ == "__main__":
    app.run("0.0.0.0", port=PORT)