from email.message import EmailMessage
import ssl
import smtplib
import pyrebase 
import time
import json
from templates import Template
from datetime import datetime

def createEmail(toEmailAddress: str, fromEmailAddress: str):

    try:
        user_name = toEmailAddress.split('@')[0]
        user_name = user_name.replace('.', ' ')
        user_name = user_name.title()
    except IndexError:
        user_name = toEmailAddress.split('@')[0]
    
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = Template.from_file("./templates/emergency.txt")
    fields = {"[DATE-TIME]": str(current_datetime), "[USER]": user_name}
    
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
        
def getEmergencyValue(db) -> bool:
    emergencyValue = db.child('emergency').get().val()
    return emergencyValue

def main() -> None:

    with open("./fans_credentials.json", "r") as file:
        credentials: dict[str, str] = json.load(file)
        
    # Firebase configuration
    config = {
        "apiKey": "AIzaSyDCrm-YWek1mShoftACTezFdzn8PoLSNrY",     
        "authDomain": "fans-38702.firebaseapp.com",     
        "databaseURL": "https://fans-38702-default-rtdb.firebaseio.com/",     
        "storageBucket": "fans-38702.appspot.com" 
    }     
        
    db = connectFirebase(config)
    
    emails = ['saja.fawagreh@gmail.com']

    # Constantly poll for emergency
    while True:    
        emergencyValue = getEmergencyValue(db)
        while emergencyValue:
            for email in emails:
                emailMessage = createEmail(email, credentials["email"])
                sendemail(emailMessage, credentials["email"], credentials["pass"])
                print("Email sent to " + email)
                time.sleep(1)

        time.sleep(1)  # Poll DB every second

if __name__ == "__main__":
    main()

