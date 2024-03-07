from email.message import EmailMessage
import ssl
import smtplib
from datetime import datetime

FROM = 'sysc3010.l1g8@gmail.com'
PASSWORD = 'iahv wbgh zxmt obdt'
TO = 'saja.fawagreh@gmail.com'  # Assuming the format is <first name>.<last name>@domain

# Attempt to extract user name from the email address
try:
    user_name = TO.split('@')[0]  
    user_name = user_name.replace('.', ' ')  
    user_name = user_name.title() 
except IndexError:
    user_name = TO.split('@')[0]  # Default name if parsing fails

SUBJECT = "HIGH PRIORITY: Fire Alarm Emergency Notification"
current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

BODY = f"Dear {user_name},\nThis is an emergency notification. Please exit the building.\nEmergency detected: {current_datetime}"

# Prepare the email message
em = EmailMessage()
em['From'] = FROM
em['To'] = TO
em['Subject'] = SUBJECT
em['X-Priority'] = '1'  # High priority
em.set_content(BODY)

context = ssl.create_default_context()

# Sending the email
with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
    smtp.login(FROM, PASSWORD)
    smtp.send_message(em)

