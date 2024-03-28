from email.message import EmailMessage
import ssl
import sqlite3
import smtplib
import pyrebase
import time
import json
from templates import Template
from datetime import datetime


def createEmail(name: str, toEmailAddress: str, fromEmailAddress: str):
    
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = Template.from_file("./templates/emergency.txt")
    fields = {"[DATE-TIME]": str(current_datetime), "[USER]": name}

    message.customize(fields)

    subject = "HIGH PRIORITY: Fire Alarm Emergency Notification"

    em = EmailMessage()

    em['From'] = fromEmailAddress
    em['To'] = toEmailAddress
    em['Subject'] = subject
    em.set_content(str(message))

    return em


def sendemail(emailMessage, email, password):
    context = ssl.create_default_context()
    smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context)
    smtp.login(email, password)
    smtp.send_message(emailMessage)


def connectFirebase(config: dict):
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    return db


def getEmergencyValue(db):
    emergencyValue = db.child('emergency').get().val()
    return emergencyValue

def getUsers(db):
    users_raw = db.child('users').get().val()
    users = {}
    for key, value in users_raw.items():
        # Convert the key back to its original email format
        email = key.replace(',', '.')
        for name, detail in value.items():
            user_info = (name, detail)
            users[email] = user_info
    print(users)
    return users


def addUserToSQLite(cursor, email, name, password):
    # Try to insert the user into the SQLite table, including the password
    try:
        cursor.execute("INSERT OR IGNORE INTO users (email, name, password) VALUES (?, ?, ?)", (email, name, password))
    except sqlite3.IntegrityError:
        print(f"User {email} already exists in the database.")

def print_users_table(cursor):
    cursor.execute("SELECT email, name, password FROM users")
    rows = cursor.fetchall()  # Fetch all rows of the query result
    print("Contents of users table:")
    for row in rows:
        print(row)


def main():
    with open("./fans_credentials.json", "r") as file:
        credentials: dict[str, str] = json.load(file)

    config = {
        "apiKey": "AIzaSyDCrm-YWek1mShoftACTezFdzn8PoLSNrY",
        "authDomain": "fans-38702.firebaseapp.com",
        "databaseURL": "https://fans-38702-default-rtdb.firebaseio.com/",
        "storageBucket": "fans-38702.appspot.com"
    }

    db = connectFirebase(config)

    dbconnect = sqlite3.connect("FANS.db")

    cursor = dbconnect.cursor()

    while True:
        emergencyValue = getEmergencyValue(db)
        while emergencyValue:
            users = getUsers(db)
            for email, details in users.items():
                name = details[0]
                userPassword = details[1]
                addUserToSQLite(cursor, email, name, userPassword)
                print_users_table(cursor)
                emailMessage = createEmail(name, email, credentials["email"])
                username = credentials["email"]
                password = credentials["pass"]
                #sendemail(emailMessage, username, password)
                print("Email sent to " + name)
                time.sleep(1)

            dbconnect.commit()

        time.sleep(1)


if __name__ == "__main__":
    main()
