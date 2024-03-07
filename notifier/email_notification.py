from email.message import EmailMessage
import ssl
import smtplib
import pyrebase 
import time
from datetime import datetime

def sendemail(to_emails: list) -> None:
    # Define sender's email and password
    FROM = 'sysc3010.l1g8@gmail.com'
    PASSWORD = 'iahv wbgh zxmt obdt'
    
    for TO in to_emails:
        # Attempt to extract user name from the email address
        try:
            user_name = TO.split('@')[0]
            user_name = user_name.replace('.', ' ')
            user_name = user_name.title()
        except IndexError:
            user_name = TO.split('@')[0]  # Default name if parsing fails
        
        # Email subject and body
        SUBJECT = "HIGH PRIORITY: Fire Alarm Emergency Notification"
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        BODY = f"Dear {user_name},\nThis is an emergency notification. Please exit the building.\nEmergency detected: {current_datetime}"
        
        # Prepare the email message
        em = EmailMessage()
        em['From'] = FROM
        em['To'] = TO  # This needs to be a single email address string, not a list
        em['Subject'] = SUBJECT
        em['X-Priority'] = '1'  # High priority
        em.set_content(BODY)
        
        # Create secure SSL connection for sending emails
        context = ssl.create_default_context()
        
        # Sending the email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(FROM, PASSWORD)
            smtp.send_message(em)
            
        print('Email sent to ' + TO)

def main() -> None:
    # Firebase configuration
    config = {
        "apiKey": "AIzaSyDCrm-YWek1mShoftACTezFdzn8PoLSNrY",     
        "authDomain": "fans-38702.firebaseapp.com",     
        "databaseURL": "https://fans-38702-default-rtdb.firebaseio.com/",     
        "storageBucket": "fans-38702.appspot.com" 
    }
    
    # Connect to Firebase using the configuration 
    firebase = pyrebase.initialize_app(config) 
    db = firebase.database()     
    
    # Constantly poll for emergency
    while True:
        emergencyValue = db.child('emergency').get().val()
        print(emergencyValue)
        while emergencyValue:
            to_emails = ['saja.fawagreh@gmail.com', 'javeria1228@gmail.com']
            sendemail(to_emails)
            time.sleep(1)

        time.sleep(1)  # Poll DB every second

if __name__ == "__main__":
    main()

