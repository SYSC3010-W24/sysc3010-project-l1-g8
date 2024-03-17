import unittest
from unittest.mock import patch, MagicMock
from email_notification_system import createEmail, sendemail, connectFirebase, getEmergencyValue 
from email.message import EmailMessage
import re
from datetime import datetime
import json
import smtplib

class TestCreateEmail(unittest.TestCase):

    def test_create_email(self):
        """
        Test the createEmail function to ensure it returns a properly formatted EmailMessage object.
        This includes verifying the recipient, sender, subject, and the presence of expected content,
        as well as ensuring the included date-time is not in the future.
        """
        # Set up email addresses for the test
        to_email = "test.user@gmail.com"
        from_email = "noreply@example.com"
        email_message = createEmail(to_email, from_email)
        email_content = email_message.get_content()
        
        # Assert basic EmailMessage structure and headers
        self.assertIsInstance(email_message, EmailMessage)
        self.assertEqual(email_message['To'], to_email)
        self.assertEqual(email_message['From'], from_email)
        self.assertEqual("HIGH PRIORITY: Fire Alarm Emergency Notification", email_message['Subject'])

        # Check for expected content in the body
        expected_content = "Dear Test User,\n\nThis is an emergency notification. Please exit the building.\n\nEmergency detected:"
        self.assertIn(expected_content, email_content)

        # Validate the presence and format of the datetime in the email content
        date_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
        match = re.search(date_pattern, email_content)
        self.assertIsNotNone(match, "The email content should include a date and time.")

        if match:
            extracted_date = datetime.strptime(match.group(), "%Y-%m-%d %H:%M:%S")
            now = datetime.now()
            
            # Ensure date-time components match current time and are not in the future
            self.assertEqual(extracted_date.year, now.year)
            self.assertEqual(extracted_date.month, now.month)
            self.assertEqual(extracted_date.day, now.day)
            self.assertEqual(extracted_date.hour, now.hour)
            
            self.assertTrue((extracted_date.minute < now.minute) or 
                            (extracted_date.minute == now.minute and extracted_date.second <= now.second),
                            "The extracted time should be less than or equal to the current time.")

@patch('email_notification_system.pyrebase')
class TestFirebaseConnection(unittest.TestCase):

    def test_connect_firebase(self, mock_pyrebase):
        """
        Test the connectFirebase function to verify it correctly initializes the Firebase app
        and returns a database object.
        """
        # Define a dummy Firebase config
        config = {
            "apiKey": "testKey",
            "authDomain": "testDomain",
            "databaseURL": "testURL",
            "storageBucket": "testBucket"
        }
        
        # Set up the mock to simulate Firebase app initialization
        mock_db = MagicMock()
        mock_pyrebase.initialize_app.return_value.database.return_value = mock_db
        
        # Execute and verify function behavior
        db = connectFirebase(config)
        mock_pyrebase.initialize_app.assert_called_once_with(config)
        self.assertEqual(db, mock_db)

    def test_connect_firebase_exception(self, mock_pyrebase):
        """
        Test that the correct exception is raised when there's an error connecting to Firebase.
        This simulates a failure in initializing the Firebase app and ensures the exception
        is properly propagated or handled.
        """
        # Simulate a failure in Firebase app initialization
        mock_pyrebase.initialize_app.side_effect = Exception("Failed to initialize Firebase")
        
        config = {
            "apiKey": "testKey",
            "authDomain": "testDomain",
            "databaseURL": "testURL",
            "storageBucket": "testBucket"
        }
        
        # Attempt to connect to Firebase and verify that an exception is raised
        with self.assertRaises(Exception) as context:
            connectFirebase(config)
        
        # Optionally, assert the exception message if specific error handling is expected
        self.assertTrue("Failed to initialize Firebase" in str(context.exception))

class TestGetEmergencyValue(unittest.TestCase):

    @patch('email_notification_system.connectFirebase')
    def test_get_emergency_value(self, mock_connect):
        """
        Test the getEmergencyValue function to confirm it retrieves the correct emergency value from Firebase.
        """
        # Set up the mock Firebase database object
        mock_db = MagicMock()
        mock_db.child.return_value.get.return_value.val.return_value = True
        mock_connect.return_value = mock_db
        
        # Execute and assert expected emergency value
        emergency_value = getEmergencyValue(mock_db)
        mock_db.child.assert_called_once_with('emergency')
        self.assertTrue(emergency_value)

@patch('email_notification_system.smtplib.SMTP_SSL')
class TestSendEmail(unittest.TestCase):

    def test_send_email_success(self, mock_smtp):
        """
        Test successful email sending, ensuring SMTP_SSL is called with correct parameters and methods.
        """
        email = "noreply@example.com"
        password = "password"
        email_message = createEmail("test.user@gmail.com", email)
        
        # Attempt to send email and verify SMTP interactions
        try:
            sendemail(email_message, email, password)
        except Exception as e:
            self.fail(f"sendemail raised an exception: {e}")
        
        # Assert correct SMTP setup and method calls
        mock_smtp.assert_called_with('smtp.gmail.com', 465, context=unittest.mock.ANY)
        mock_smtp.return_value.login.assert_called_with(email, password)
        mock_smtp.return_value.send_message.assert_called_with(email_message)
    
    def test_send_email_exception(self, mock_smtp):
        """
        Test the handling of SMTP exceptions when attempting to send an email. This test ensures that
        if an SMTPAuthenticationError occurs during the login process, it is correctly raised by the sendemail
        function, allowing for appropriate error handling in the application.
        """
        # Configure the mock to raise an SMTPAuthenticationError on login attempt
        mock_smtp.return_value.login.side_effect = smtplib.SMTPAuthenticationError(421, 'Failed')
        
        email = "noreply@example.com"
        password = "wrongpassword"
        email_message = createEmail("test.user@gmail.com", email)
        
        # Verify that attempting to send an email with incorrect credentials raises the expected exception
        with self.assertRaises(smtplib.SMTPAuthenticationError):
            sendemail(email_message, email, password)

if __name__ == '__main__':
    unittest.main()