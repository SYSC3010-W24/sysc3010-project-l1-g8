"""
This file implements an emergency notification system. It sends email and SMS
notifications, manages user information with Firebase and SQLite, and listens
for UDP signals to trigger or stop notifications depending on the emergency
status.
Author: Saja Fawagreh
"""

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
from twilio.rest import Client

RECEIVE_PORT: int = 2003
BUFFER_SIZE: int = 100


def create_message(name: str) -> str:
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = Template.from_file("./templates/emergency.txt")
    fields = {"[DATE-TIME]": str(current_datetime), "[USER]": name}

    message.customize(fields)

    return str(message)


def create_email(message: str, toEmail: str, fromEmail: str) -> EmailMessage:
    subject = "HIGH PRIORITY: Fire Alarm Emergency Notification"

    em = EmailMessage()

    em["From"] = fromEmail
    em["To"] = toEmail
    em["Subject"] = subject
    em.set_content(str(message))

    return em


def send_email(emailMessage: EmailMessage, email: str, password: str) -> None:
    context = ssl.create_default_context()
    smtp = smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context)
    smtp.login(email, password)
    smtp.send_message(emailMessage)


def send_message(client, message: str, phoneNumber: str) -> None:
    message = client.messages.create(
        from_="+16506678309", body=message, to=phoneNumber
        )


def connect_to_firebase(config: dict):
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    return db


def get_users(db) -> dict:
    users_raw = db.child("users").get().val()
    users = {}
    for key, value in users_raw.items():
        email = key.replace(",", ".")
        users[email] = users_raw[key]
    return users


def add_user_to_SQLite(
    cursor, email: str, name: str, phoneNumber: str, password: str
) -> None:
    cursor.execute(
        "REPLACE INTO users (Email, Name, PhoneNumber, Password) "
        "VALUES (?, ?, ?, ?)",
        (email, name, phoneNumber, password),
    )


def wait_for_message(channel: socket.socket) -> Messages:
    data, _ = channel.recvfrom(BUFFER_SIZE)
    return Messages(int.from_bytes(data))


def main():
    with open("twilio_credentials.json", "r") as file:
        credentials = json.load(file)

    account_sid = credentials["account_sid"]
    auth_token = credentials["auth_token"]

    client = Client(account_sid, auth_token)

    with open("./fans_credentials.json", "r") as file:
        credentials = json.load(file)

    with open("./firebase_config.json", "r") as file:
        config = json.load(file)

    username = credentials["email"]
    password = credentials["pass"]

    db = connect_to_firebase(config)

    dbconnect = sqlite3.connect("FANS.db")

    cursor = dbconnect.cursor()

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        Email TEXT PRIMARY KEY,
        Name TEXT NOT NULL,
        PhoneNumber TEXT NOT NULL,
        Password TEXT NOT NULL
    );
    """

    cursor.execute(create_table_sql)

    dbconnect.commit()

    emails_sent = False

    ip_addr = ni.ifaddresses("wlan0")[ni.AF_INET][0]["addr"]
    db.child("devices").child("notifier").set(ip_addr)

    channel = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    channel.bind((ip_addr, RECEIVE_PORT))

    while True:
        msg = wait_for_message(channel)

        match msg:
            case Messages.EMERGENCY:
                if not emails_sent:
                    users = get_users(db)
                    for email, detail in users.items():
                        name = detail.get("Name")
                        userPassword = detail.get("Password")
                        phoneNumber = detail.get("Phone Number")
                        add_user_to_SQLite(
                            cursor, email, name, phoneNumber, userPassword
                        )
                        message = create_message(name)
                        emailMessage = create_email(message, email, username)
                        send_email(emailMessage, username, password)
                        send_message(client, message, phoneNumber)
                        print("Email sent to " + name)
                        time.sleep(2)

                    emails_sent = True
                    dbconnect.commit()

            case Messages.EMERGENCY_OVER:
                emails_sent = False

        time.sleep(2)


if __name__ == "__main__":
    main()
