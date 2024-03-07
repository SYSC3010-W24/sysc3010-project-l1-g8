import smtplib
import ssl
import json
from templates import Template
import datetime as dt

PORT: int = 465  # For SSL
FANS_CREDENTIALS: str = "./fans_credentials.json"
TEST_EMAILS: list[str] = ["matteo.golin@gmail.com"]
SMTP_SERVER: str = "smtp.gmail.com"


def main() -> None:

    # Load email credentials for notification system
    with open(FANS_CREDENTIALS, "r") as file:
        credentials: dict[str, str] = json.load(file)

    # Create email template
    message = Template.from_file("./templates/emergency.txt")
    fields = {"[DATE-TIME]": dt.datetime.today(), "[USER]": ""}

    # Create secure SSL connection for sending emails
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(SMTP_SERVER, PORT, context=context) as server:
        server.login(credentials["email"], credentials["pass"])

        for email in TEST_EMAILS:

            message.reset()  # Rest to default

            # Update email with correct fields
            fields["[USER]"] = email
            message.customize(fields)

            server.sendmail(credentials["email"], email, str(message))


if __name__ == "__main__":
    main()
