"""
COMPREHENSIVE AUTOMATED TEST SUITE FOR RADAR SMART DISASTER MANAGEMENT WEB APP
Verifies database operations, shelter data reliability, capacity calculations,
independent location engine, weather API, Ask Gemini endpoint, and admin operations.
"""

import os
import unittest
import json
from app import create_app
from database import db
from models import User, Shelter, DisasterAlert, EmergencyRequest, RiskPrediction

class DisasterAppTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test Flask application client and clean test SQLite database."""
        os.environ['SECRET_KEY'] = 'test-secret-key-123'
        os.environ['USE_MYSQL'] = 'False'
        
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            self.seed_test_data()

    def tearDown(self):
        """Tear down database context."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def seed_test_data(self):
        """Seed minimal test data."""
        admin = User(username='admin_test', email='admin_test@test.org', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)

        shelter1 = Shelter(
            name="Test Verified Shelter",
            address="123 Test Street",
            state="Maharashtra",
            district="Pune",
            city_village="Shivajinagar",
            facility_type="Shelter",
            latitude=18.5204,
            longitude=73.8567,
            total_capacity=500,
            current_occupancy=200,
            available_capacity=300,
            contact="+91-9999999999",
            verification_status="Verified"
        )

        shelter2 = Shelter(
            name="Test Unverified Building",
            address="456 Unverified Ave",
            state="Maharashtra",
            district="Pune",
            city_village="Shivajinagar",
            facility_type="Building",
            latitude=18.5300,
            longitude=73.8600,
            total_capacity=100,
            current_occupancy=50,
            available_capacity=50,
            contact="+91-8888888888",
            verification_status="Unverified"
        )
        db.session.add_all([shelter1, shelter2])

        alert = DisasterAlert(
            title="Flash Flood Advisory",
            disaster_type="Flood",
            severity="Warning",
            location="Pune District",
            description="Rising water levels in Mula-Mutha river.",
            is_active=True
        )
        db.session.add(alert)
        db.session.commit()

    # ================= 1. SHELTER DATA & CAPACITY TESTS =================

    def test_shelter_capacity_recalculation(self):
        """Test shelter model capacity recalculation math."""
        with self.app.app_context():
            s = Shelter.query.filter_by(name="Test Verified Shelter").first()
            self.assertIsNotNone(s)
            self.assertEqual(s.total_capacity, 500)
            self.assertEqual(s.current_occupancy, 200)
            self.assertEqual(s.available_capacity, 300)

            # Test updating occupancy
            s.current_occupancy = 350
            s.recalculate_capacity()
            self.assertEqual(s.available_capacity, 150)
            self.assertEqual(s.available_beds, 150)

    def test_shelter_verification_separation(self):
        """Verify that shelter API only lists verified disaster shelters."""
        response = self.client.get('/api/shelters')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        # Should only contain verified shelters
        self.assertTrue(len(data) >= 1)
        for s in data:
            self.assertEqual(s['verification_status'], 'Verified')

    def test_shelter_occupancy_update_api(self):
        """Test POST /api/shelter/<id>/update_occupancy validation & state mutation."""
        with self.app.app_context():
            s = Shelter.query.filter_by(name="Test Verified Shelter").first()
            s_id = s.id

        # Valid update
        res = self.client.post(f'/api/shelter/{s_id}/update_occupancy', json={'current_occupancy': 400})
        self.assertEqual(res.status_code, 200)
        res_data = res.get_json()
        self.assertTrue(res_data['success'])
        self.assertEqual(res_data['shelter']['available_capacity'], 100)

        # Invalid update (exceeding total capacity)
        res_invalid = self.client.post(f'/api/shelter/{s_id}/update_occupancy', json={'current_occupancy': 600})
        self.assertEqual(res_invalid.status_code, 400)
        self.assertFalse(res_invalid.get_json()['success'])

    # ================= 2. LOCATION ENGINE TESTS =================

    def test_independent_location_options(self):
        """Test that /api/location_options uses INDIA_GEO_DATA independently of shelters."""
        res_states = self.client.get('/api/location_options')
        self.assertEqual(res_states.status_code, 200)
        data = res_states.get_json()
        self.assertIn('Maharashtra', data['states'])

        res_districts = self.client.get('/api/location_options?state=Maharashtra')
        self.assertEqual(res_districts.status_code, 200)
        dist_data = res_districts.get_json()
        self.assertTrue(any('Pune' in d for d in dist_data['districts']))

    # ================= 3. REAL-TIME WEATHER TESTS =================

    def test_realtime_weather_api(self):
        """Test real-time weather API endpoint."""
        res = self.client.get('/api/weather?location=Mumbai')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertIn('temperature', data)
        self.assertIn('humidity', data)
        self.assertIn('rainfall', data)
        self.assertIn('wind_speed', data)
        self.assertIn('weather_condition', data)
        self.assertIn('timestamp', data)

    # ================= 4. ASK GEMINI ASSISTANT TESTS =================

    def test_ask_gemini_chatbot_api(self):
        """Test 'Ask Gemini' chatbot API response and grounding."""
        res = self.client.post('/api/chatbot', json={'message': 'What shelters are available?'})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('reply', data)
        self.assertTrue(len(data['reply']) > 10)

    # ================= 5. MAIN & ADMIN ROUTE TESTS =================

    def test_homepage_route(self):
        """Test home page loads with HTTP 200."""
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'RADAR', res.data)

    def test_shelters_view_route(self):
        """Test shelters view page."""
        res = self.client.get('/shelters')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Verified Disaster Shelters', res.data)

    def test_alerts_view_route(self):
        """Test live weather & alerts view page."""
        res = self.client.get('/alerts')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Live Weather', res.data)

if __name__ == '__main__':
    unittest.main()
