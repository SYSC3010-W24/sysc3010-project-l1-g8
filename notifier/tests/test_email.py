import pytest
import smtplib
import ssl
import json
import email
import imaplib
from templates import Template

PORT: int = 465  # For SSL
FANS_CREDENTIALS: str = "./fans_credentials.json"
GMAIL_IMAP_SERVER: str = "imap.gmail.com"
SMTP_SERVER: str = "smtp.gmail.com"


@pytest.fixture
def message() -> Template:
    return Template("This is a test message.")


def test_send_email(message: Template) -> None:

    with open(FANS_CREDENTIALS, "r") as file:
        credentials: dict[str, str] = json.load(file)

    # Create secure SSL connection for sending emails
    context = ssl.create_default_context()

    # Send message to self
    email_addr = credentials["email"]
    with smtplib.SMTP_SSL(SMTP_SERVER, PORT, context=context) as server:
        server.login(email_addr, credentials["pass"])
        server.sendmail(email_addr, email_addr, str(message))

    # Retrieve message
    mail = imaplib.IMAP4_SSL(GMAIL_IMAP_SERVER)
    mail.login(credentials["email"], credentials["pass"])
    mail.select("INBOX")

    # Extract text of message
    _, selected = mail.search(None, f'FROM "{email_addr}"')

    for num in selected[0].split():
        _, data = mail.fetch(num, "(RFC822)")
        _, bytes_data = data[0]  # type: ignore

    received = email.message_from_bytes(bytes_data)  # type: ignore
    print(received)  # Display received message for demonstration purposes

    for part in received.walk():
        if part.get_content_type() == "text/plain":
            text = part.get_payload().strip()  # type: ignore
            print(text)
            assert text == str(message)  # Check that test message matches
