"""
Unit tests for the emergency notification system, covering message creation,
email and SMS sending, database interactions for user management,
and network communication for emergency signal handling.
Tests validate functionality such as dynamic message content,
communication protocol adherence, and data integrity in user management.
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from email.message import EmailMessage
import re
from email_notification_system import (
    createMessage, createEmail, sendEmail, sendMessage,
    connectFirebase, getUsers, addUserToSQLite, wait_for_message
)


class TestScript(unittest.TestCase):

    def test_createMessage(self):
        name = "TestUser"
        result = createMessage(name)
        expected_content = ("Dear TestUser,\n\nThis is an emergency notification."
                            " Please exit the building.\n\nEmergency detected:")
        self.assertIn(expected_content, result)

        date_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
        match = re.search(date_pattern, result)
        self.assertIsNotNone(match, "The email content should include a date and time.")

        if match:
            extracted_date = datetime.strptime(
                match.group(), "%Y-%m-%d %H:%M:%S")
            now = datetime.now()
            time_difference = now - extracted_date

            self.assertGreaterEqual(time_difference, timedelta(0),
                                    "The extracted datetime is in the future.")

            self.assertLessEqual(time_difference, timedelta(hours=1),
                                 "The extracted datetime is more than an hour in the past.")

    def test_createEmail(self):
        message = "This is a test message."
        toEmail = "to@example.com"
        fromEmail = "from@example.com"
        emailMessage = createEmail(message, toEmail, fromEmail)
        self.assertIsInstance(emailMessage, EmailMessage)
        self.assertEqual(emailMessage['To'], toEmail)
        self.assertEqual(emailMessage['From'], fromEmail)
        self.assertIn(message, emailMessage.get_content())

    @patch('smtplib.SMTP_SSL')
    def test_sendEmail(self, mock_smtp):
        emailMessage = EmailMessage()
        emailMessage['To'] = "to@example.com"
        emailMessage['From'] = "from@example.com"
        emailMessage.set_content("This is a test message.")
        sendEmail(emailMessage, "email@example.com", "password")
        instance = mock_smtp.return_value

        mock_smtp.assert_called_with(
            'smtp.gmail.com', 465, context=unittest.mock.ANY)

        instance.login.assert_called_with("email@example.com", "password")
        instance.send_message.assert_called_with(emailMessage)

    @patch('twilio.rest.Client')
    def test_sendMessage(self, mock_client):
        mock_messages = MagicMock()
        mock_client.return_value.messages = mock_messages

        client = mock_client.return_value
        sendMessage(client, "This is a test message.", "+1234567890")

        mock_messages.create.assert_called_once_with(
            from_='+16506678309',
            body="This is a test message.",
            to='+1234567890'
        )

    @patch('email_notification_system.pyrebase')
    def test_connectFirebase(self, mock_pyrebase):
        config = {
            "apiKey": "testKey",
            "authDomain": "testDomain",
            "databaseURL": "testURL",
            "storageBucket": "testBucket"
        }
        mock_db = MagicMock()
        mock_pyrebase.initialize_app.return_value.database.return_value = mock_db
        db = connectFirebase(config)
        mock_pyrebase.initialize_app.assert_called_once_with(config)
        self.assertEqual(db, mock_db)

    @patch('pyrebase.pyrebase.Database')
    def test_getUsers(self, mock_database):
        db = MagicMock()

        db.child.return_value.get.return_value.val.return_value = {
            "test@example.com": {
                'Name': 'Test User',
                'Password': 'password',
                'Phone Number': '6132225555'
            }
        }

        users = getUsers(db)

        self.assertEqual(len(users), 1)
        self.assertIn("test@example.com", users)

        self.assertEqual(users.get("test@example.com"), {
                         'Name': 'Test User',
                         'Password': 'password',
                         'Phone Number': '6132225555'})

    def test_addUserToSQLite(self):
        cursor = MagicMock()
        addUserToSQLite(cursor, "test@example.com",
                        "Test User", "6132225555", "password")

    def test_wait_for_message(self):
        mock_socket = MagicMock()
        mock_socket.recvfrom.return_value = (b'\x00\x01', ('127.0.0.1', 12345))
        result = wait_for_message(mock_socket)
        self.assertEqual(result, 1)


if __name__ == '__main__':
    unittest.main()
