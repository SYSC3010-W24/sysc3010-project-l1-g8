import unittest
import pyrebase
import json
from main import app, db

class TestDatabase(unittest.TestCase):

    def setUp(self):
        # Initialize DB connection
        with open("firebase_config.json", "r") as file:
            config = json.load(file)
        firebase = pyrebase.initialize_app(config)
        self.db = firebase.database()

        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_home_page(self):
        # Get current temperature and emergency flag from Firebase
        temperature_data = self.db.child("sensordata").child("temperature").get().val()
        latest_timestamp = max(temperature_data.keys())
        current_temperature = round(temperature_data[latest_timestamp], 2)
        emergency_flag = self.db.child("emergency").get().val()
        color_class = "fire" if emergency_flag else "no-fire"

        # Simulate a request to the home page
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(f"Current Temperature: {current_temperature}".encode(), response.data)
        self.assertIn(b'Status:', response.data)

    def test_settings_page(self):
        # Get temperature threshold from Firebase
        temperature_threshold = self.db.child("thresholds").child("temperature").get().val()

        # Simulate a request to the settings page
        response = self.app.get('/settings')
        self.assertEqual(response.status_code, 200)
        self.assertIn(f"Temperature Threshold: {temperature_threshold}".encode(), response.data)
        self.assertIn(b'Smoke Threshold:', response.data)

if __name__ == '__main__':
    unittest.main(verbosity=2)
# run using the command: python -m unittest tests.test_database