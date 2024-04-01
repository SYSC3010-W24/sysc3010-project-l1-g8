import unittest
from unittest.mock import patch, MagicMock
from haptic_alarm import control_alarm, connectFirebase


class TestFirebaseConnection(unittest.TestCase):

    @patch("haptic_alarm.pyrebase")
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
            "storageBucket": "testBucket",
        }

        # Set up the mock to simulate Firebase app initialization
        mock_db = MagicMock()
        mock_pyrebase.initialize_app.return_value.database.return_value = (
            mock_db
        )

        # Execute and verify function behavior
        db = connectFirebase(config)
        mock_pyrebase.initialize_app.assert_called_once_with(config)
        self.assertEqual(db, mock_db)

    @patch("haptic_alarm.pyrebase")
    def test_connect_firebase_exception(self, mock_pyrebase):
        """
        Test that the correct exception is raised when there's an error connecting to Firebase.
        This simulates a failure in initializing the Firebase app and ensures the exception
        is properly propagated or handled.
        """
        # Simulate a failure in Firebase app initialization
        mock_pyrebase.initialize_app.side_effect = Exception(
            "Failed to initialize Firebase"
        )

        config = {
            "apiKey": "testKey",
            "authDomain": "testDomain",
            "databaseURL": "testURL",
            "storageBucket": "testBucket",
        }

        # Attempt to connect to Firebase and verify that an exception is raised
        with self.assertRaises(Exception) as context:
            connectFirebase(config)

        # Optionally, assert the exception message if specific error handling is expected
        self.assertTrue(
            "Failed to initialize Firebase" in str(context.exception)
        )


class TestControlAlarm(unittest.TestCase):

    @patch("haptic_alarm.GPIO")
    @patch("time.sleep", MagicMock())
    @patch("haptic_alarm.pyrebase")
    def test_alarm_triggered(self, mock_pyrebase, mock_GPIO):
        # Mocking Firebase database to return True for emergency flag
        mock_db = MagicMock()
        mock_db.child.return_value.get.return_value.val.return_value = True
        mock_pyrebase.initialize_app.return_value.database.return_value = (
            mock_db
        )

        # Call control_alarm
        control_alarm()

        # Assert GPIO interactions
        mock_GPIO.output.assert_called_with(17, mock_GPIO.HIGH)

    @patch("haptic_alarm.GPIO")
    @patch("time.sleep", MagicMock())
    @patch("haptic_alarm.pyrebase")
    def test_alarm_not_triggered(self, mock_pyrebase, mock_GPIO):
        # Mocking Firebase database to return False for emergency flag
        mock_db = MagicMock()
        mock_db.child.return_value.get.return_value.val.return_value = False
        mock_pyrebase.initialize_app.return_value.database.return_value = (
            mock_db
        )

        # Call control_alarm
        control_alarm()

        # Assert GPIO interactions
        mock_GPIO.output.assert_called_with(17, mock_GPIO.LOW)


if __name__ == "__main__":
    unittest.main()
