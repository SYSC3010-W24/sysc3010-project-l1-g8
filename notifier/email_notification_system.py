from email.message import EmailMessage
import ssl
import sqlite3
import smtplib
import pyrebase
import time
import json
from templates import Template
from datetime import datetime
import netifaces as ni
import socket
from messages import Messages

RECEIVE_PORT: int = 2003
BUFFER_SIZE: int = 100

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

def sendEmail(emailMessage, email, password):
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
    return users

def addUserToSQLite(cursor, email, name, password):
    cursor.execute("REPLACE INTO users (email, name, password) VALUES (?, ?, ?)", (email, name, password))

def print_users_table(cursor):
    cursor.execute("SELECT email, name, password FROM users")
    rows = cursor.fetchall()  # Fetch all rows of the query result
    print("Contents of users table:")
    for row in rows:
        print(row)

def wait_for_message(channel: socket.socket) -> Messages:
    """Waits for a message over UDP."""
    data, _ = channel.recvfrom(BUFFER_SIZE)
    return Messages(int.from_bytes(data))

def main():
    with open("./fans_credentials.json", "r") as file:
        credentials: dict[str, str] = json.load(file)

    with open("./firebase_config.json", "r") as file:
        config = json.loads(file.read())

    db = connectFirebase(config)

    dbconnect = sqlite3.connect("FANS.db")

    cursor = dbconnect.cursor()

    emails_sent = False  # Flag to control email sending

    # Send current IP address for LAN communication between nodes
    ip_addr = ni.ifaddresses("wlan0")[ni.AF_INET][0]["addr"]
    db.child("devices").child("notifier").set(ip_addr)

    # Set up socket
    channel = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    channel.bind((ip_addr, RECEIVE_PORT))

    while True:
        msg = wait_for_message(channel)

        # Forward the received message as an FSM event
        match msg:
            case Messages.EMERGENCY:
                if not emails_sent:
                    users = getUsers(db)
                    for email, detail in users.items():
                        name = detail[0]
                        userPassword = detail[1]
                        addUserToSQLite(cursor, email, name, userPassword)
                        username = credentials["email"]
                        password = credentials["pass"]
                        emailMessage = createEmail(name, email, username)
                        sendEmail(emailMessage, username, password)
                        print("Email sent to " + name)
                        time.sleep(2) 

                    emails_sent = True
                    dbconnect.commit()

                elif not emergencyValue:
                    emails_sent = False

                time.sleep(2)


if __name__ == "__main__":
    main()
