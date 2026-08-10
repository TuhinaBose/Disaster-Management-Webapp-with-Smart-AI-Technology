import os
from flask import Flask
from config import Config
from database import db, init_db
from routes import register_blueprints
from models import User, Shelter, DisasterAlert

def create_app():
    """
    Application Factory Pattern for Flask.
    Creates and configures Flask app instance.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Database
    init_db(app)

    # Register Route Blueprints
    register_blueprints(app)

    # Seed Initial Default Admin and Sample Data if empty
    with app.app_context():
        seed_database()

    return app

def seed_database():
    """Seeds initial admin account and sample data if tables are empty."""
    try:
        # Check Admin Account
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin = User(username='admin', email='admin@disasterapp.org', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("[Database Seed] Created default admin account (admin / admin123).")

        # Check Shelters Seed
        if Shelter.query.count() == 0:
            sample_shelters = [
                Shelter(
                    name="Central Relief & Rescue Community Hall",
                    address="124 Station Road, Central District",
                    district="Central",
                    latitude=28.6139,
                    longitude=77.2090,
                    total_capacity=500,
                    available_beds=320,
                    has_food=True,
                    has_water=True,
                    has_medical=True,
                    contact_number="+91-9876543210"
                ),
                Shelter(
                    name="St. Mary High School Emergency Complex",
                    address="88 Riverside Drive, North Haven",
                    district="North Haven",
                    latitude=28.7041,
                    longitude=77.1025,
                    total_capacity=300,
                    available_beds=145,
                    has_food=True,
                    has_water=True,
                    has_medical=True,
                    contact_number="+91-9876543211"
                ),
                Shelter(
                    name="Metro Indoor Stadium Shelter",
                    address="45 Sports City Boulevard, East Zone",
                    district="East Zone",
                    latitude=28.5355,
                    longitude=77.3910,
                    total_capacity=1200,
                    available_beds=890,
                    has_food=True,
                    has_water=True,
                    has_medical=True,
                    contact_number="+91-9876543212"
                ),
                Shelter(
                    name="Coastal High Ground Refuge Camp",
                    address="12 Beach Safety Highway, South Shore",
                    district="South Shore",
                    latitude=28.4595,
                    longitude=77.0266,
                    total_capacity=400,
                    available_beds=50,
                    has_food=True,
                    has_water=True,
                    has_medical=False,
                    contact_number="+91-9876543213"
                )
            ]
            db.session.bulk_save_objects(sample_shelters)
            db.session.commit()
            print("[Database Seed] Created sample emergency shelters.")

        # Check Active Alerts Seed
        if DisasterAlert.query.count() == 0:
            sample_alerts = [
                DisasterAlert(
                    title="Heavy Rainfall & Flash Flood Warning",
                    disaster_type="Flood",
                    severity="Critical",
                    location="Riverside & North Haven",
                    description="Severe precipitation exceeded 180mm. Water levels in local rivers approaching critical marks. Citizens advised to move to higher ground.",
                    is_active=True
                ),
                DisasterAlert(
                    title="Cyclone Alert - Strong Gusts Expected",
                    disaster_type="Cyclone",
                    severity="Warning",
                    location="South Shore Coastal Belt",
                    description="Wind speeds recorded up to 95 km/h. Coastal communities urged to remain indoors and secure emergency supplies.",
                    is_active=True
                ),
                DisasterAlert(
                    title="Heatwave Advisory - Extreme Temperatures",
                    disaster_type="Heatwave",
                    severity="Advisory",
                    location="Central Plains",
                    description="Temperatures reaching 44°C. Stay hydrated and avoid outdoor exposure during mid-day hours.",
                    is_active=True
                )
            ]
            db.session.bulk_save_objects(sample_alerts)
            db.session.commit()
            print("[Database Seed] Created sample active disaster alerts.")

    except Exception as e:
        print(f"[Database Seed Error]: {e}")

app = create_app()

if __name__ == '__main__':
    print("\n========================================================")
    print(" 🚀 RADAR - DISASTER MANAGEMENT WEB APPLICATION RUNNING")
    print(" Project: RADAR - Disaster Management Web Application with Smart AI Technology")
    print(" Access on Laptop: http://127.0.0.1:5000")
    print(" Access on Mobile: http://10.183.89.85:5000")
    print(" Admin Login at: http://127.0.0.1:5000/admin/login")
    print(" Default Admin: admin / admin123")
    print("========================================================\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
