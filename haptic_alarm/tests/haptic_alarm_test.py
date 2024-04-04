import unittest
from unittest.mock import patch, MagicMock
from haptic_alarm import control_alarm, connectFirebase


class TestFirebaseConnection(unittest.TestCase):

    @patch("haptic_alarm.pyrebase")
    def test_connect_firebase(self, mock_pyrebase):
        """
        Test connectFirebase to verify correct initialization of Firebase app
        and return of database object.
        """
        # Define dummy Firebase config
        config = {
            "apiKey": "testKey",
            "authDomain": "testDomain",
            "databaseURL": "testURL",
            "storageBucket": "testBucket",
        }

        # Setup mock for Firebase app initialization
        mock_db = MagicMock()
        init_app = mock_pyrebase.initialize_app
        init_app.return_value.database.return_value = mock_db

        # Execute function and verify behavior
        db = connectFirebase(config)
        init_app.assert_called_once_with(config)
        self.assertEqual(db, mock_db)

    @patch("haptic_alarm.pyrebase")
    def test_connect_firebase_exception(self, mock_pyrebase):
        """
        Test exception when there's an error connecting to Firebase.
        Simulates Firebase app initialization failure.
        """
        # Simulate Firebase app initialization failure
        mock_pyrebase.initialize_app.side_effect = Exception(
            "Failed to initialize Firebase"
        )

        config = {
            "apiKey": "testKey",
            "authDomain": "testDomain",
            "databaseURL": "testURL",
            "storageBucket": "testBucket",
        }

        # Attempt connection to Firebase and check for exception
        with self.assertRaises(Exception) as context:
            connectFirebase(config)

        # Check for specific exception message
        self.assertTrue(
            "Failed to initialize Firebase" in str(context.exception)
        )


class TestControlAlarm(unittest.TestCase):

    @patch("haptic_alarm.GPIO")
    @patch("time.sleep", MagicMock())
    @patch("haptic_alarm.pyrebase")
    def test_alarm_triggered(self, mock_pyrebase, mock_GPIO):
        # Mock Firebase db to return True for emergency flag
        mock_db = MagicMock()
        get_val = mock_db.child.return_value.get.return_value.val
        get_val.return_value = True
        init_app = mock_pyrebase.initialize_app
        init_app.return_value.database.return_value = mock_db

        # Call control_alarm and verify GPIO interactions
        control_alarm()
        mock_GPIO.output.assert_called_with(17, mock_GPIO.HIGH)

    @patch("haptic_alarm.GPIO")
    @patch("time.sleep", MagicMock())
    @patch("haptic_alarm.pyrebase")
    def test_alarm_not_triggered(self, mock_pyrebase, mock_GPIO):
        # Mock Firebase db to return False for emergency flag
        mock_db = MagicMock()
        get_val = mock_db.child.return_value.get.return_value.val
        get_val.return_value = False
        init_app = mock_pyrebase.initialize_app
        init_app.return_value.database.return_value = mock_db

        # Call control_alarm and verify GPIO interactions
        control_alarm()
        mock_GPIO.output.assert_called_with(17, mock_GPIO.LOW)


if __name__ == "__main__":
    unittest.main()

# Adding an extra newline at the end of the file
