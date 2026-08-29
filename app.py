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
        # 1. Ensure Admin Account exists with guaranteed password 'admin123'
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin = User(username='admin', email='admin@disasterapp.org', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("[Database Seed] Created default admin account (admin / admin123).")
        else:
            if not admin_user.check_password('admin123'):
                admin_user.set_password('admin123')
                admin_user.role = 'admin'
                db.session.commit()

        # 2. Check & Seed State-Wise Emergency Shelters
        if Shelter.query.count() < 6:
            Shelter.query.delete()
            db.session.commit()

            sample_shelters = [
                Shelter(
                    name="Central Disaster Relief & Rescue Complex",
                    address="Sector 14, Connaught Place Avenue, Central District",
                    district="Central Delhi",
                    state="Delhi NCR",
                    latitude=28.6139,
                    longitude=77.2090,
                    total_capacity=800,
                    available_beds=480,
                    has_food=True,
                    has_water=True,
                    has_medical=True,
                    contact_number="+91-9876543210"
                ),
                Shelter(
                    name="St. Mary Emergency High Ground Shelter",
                    address="88 Riverside Boulevard, Civil Lines",
                    district="North Delhi",
                    state="Delhi NCR",
                    latitude=28.7041,
                    longitude=77.1025,
                    total_capacity=450,
                    available_beds=195,
                    has_food=True,
                    has_water=True,
                    has_medical=True,
                    contact_number="+91-9876543211"
                ),
                Shelter(
                    name="Mumbai Central Flood Relief Refuge Camp",
                    address="Opposite Marine Lines Station, South Mumbai",
                    district="Mumbai City",
                    state="Maharashtra",
                    latitude=18.9438,
                    longitude=72.8229,
                    total_capacity=1200,
                    available_beds=850,
                    has_food=True,
                    has_water=True,
                    has_medical=True,
                    contact_number="+91-9876543220"
                ),
                Shelter(
                    name="Pune Disaster Evacuation Center",
                    address="Shivajinagar Relief Grounds, Pune",
                    district="Pune",
                    state="Maharashtra",
                    latitude=18.5308,
                    longitude=73.8474,
                    total_capacity=900,
                    available_beds=620,
                    has_food=True,
                    has_water=True,
                    has_medical=True,
                    contact_number="+91-9876543221"
                ),
                Shelter(
                    name="Kolkata Cyclone High-Ground Refuge Shelter",
                    address="Park Circus Indoor Complex, Salt Lake",
                    district="Kolkata",
                    state="West Bengal",
                    latitude=22.5726,
                    longitude=88.3639,
                    total_capacity=1500,
                    available_beds=1100,
                    has_food=True,
                    has_water=True,
                    has_medical=True,
                    contact_number="+91-9876543230"
                ),
                Shelter(
                    name="Sundarbans Coastal Evacuation Camp",
                    address="Canning Safety Highway, South 24 Parganas",
                    district="South 24 Parganas",
                    state="West Bengal",
                    latitude=22.3148,
                    longitude=88.6653,
                    total_capacity=750,
                    available_beds=290,
                    has_food=True,
                    has_water=True,
                    has_medical=False,
                    contact_number="+91-9876543231"
                ),
                Shelter(
                    name="Chennai Coastal Flood Relief Camp",
                    address="Marina Beach Road, Mylapore",
                    district="Chennai",
                    state="Tamil Nadu",
                    latitude=13.0405,
                    longitude=80.2707,
                    total_capacity=1000,
                    available_beds=720,
                    has_food=True,
                    has_water=True,
                    has_medical=True,
                    contact_number="+91-9876543240"
                ),
                Shelter(
                    name="Bengaluru Flood & Storm Refuge Hall",
                    address="M.G. Road Community Center, Indiranagar",
                    district="Bengaluru Urban",
                    state="Karnataka",
                    latitude=12.9716,
                    longitude=77.5946,
                    total_capacity=650,
                    available_beds=410,
                    has_food=True,
                    has_water=True,
                    has_medical=True,
                    contact_number="+91-9876543250"
                )
            ]
            db.session.bulk_save_objects(sample_shelters)
            db.session.commit()
            print("[Database Seed] Created state-wise emergency relief shelters.")

        # 3. Check Active Alerts Seed
        if DisasterAlert.query.count() == 0:
            sample_alerts = [
                DisasterAlert(
                    title="Heavy Rainfall & Severe Flash Flood Warning",
                    disaster_type="Flood",
                    severity="Critical",
                    location="Mumbai Coastal & North Haven Lowlands",
                    description="Severe precipitation exceeded 195mm. Water levels in local rivers approaching critical overflow marks. Citizens in low-lying sectors advised to move to designated shelters immediately.",
                    is_active=True
                ),
                DisasterAlert(
                    title="Cyclone Alert - High Wind Gusts (95 km/h)",
                    disaster_type="Cyclone",
                    severity="Warning",
                    location="Sundarbans & South Shore Belt",
                    description="Wind speeds recorded up to 95 km/h. Coastal communities urged to remain indoors, stay away from window glass, and secure emergency supplies.",
                    is_active=True
                ),
                DisasterAlert(
                    title="Heatwave Advisory - High Temperature Alert (44°C)",
                    disaster_type="Heatwave",
                    severity="Advisory",
                    location="Central Plains & Delhi NCR",
                    description="Extreme temperatures reaching 44°C. Stay hydrated, avoid outdoor activity between 12:00 PM and 4:00 PM, and keep emergency fluids ready.",
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
