import sqlite3

import requests
from flask import Flask, g, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = "secret_delas"

app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


DATABASE = "database/participants.db"


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


@app.route("/")
def index():
    cur = get_db().cursor()
    cur.execute("SELECT * FROM participants")
    participants = cur.fetchall()
    return render_template("index.html", participants=participants)


@app.route("/register", methods=["POST"])
def register():
    print("registering participant")
    # get the reCAPTCHA response data
    recaptcha_response = request.form.get("g-recaptcha-response")

    # verify reCAPTCHA
    payload = {
        "secret": "6LcTNQYoAAAAAEWJKUs1eNIzNdUECS3ciTLP2dQR",
        "response": recaptcha_response,
    }
    response = requests.post(
        "https://www.google.com/recaptcha/api/siteverify", data=payload
    )
    result = response.json()

    if not result.get("success"):
        return redirect(url_for("index"))

    db = get_db()
    phone = request.form.get("phone")
    skills = request.form.get("skills")

    db.execute(
        "INSERT INTO participants (phone, skills) VALUES (?, ?)", (phone, skills)
    )
    db.commit()

    return redirect(url_for("index"))


# if __name__ == "__main__":
#     app.run(debug=True)
