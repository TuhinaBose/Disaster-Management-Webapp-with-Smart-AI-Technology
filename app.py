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
            # Re-verify password hash to ensure admin123 always works
            if not admin_user.check_password('admin123'):
                admin_user.set_password('admin123')
                admin_user.role = 'admin'
                db.session.commit()
                print("[Database Seed] Reset admin password to admin123.")

        # 2. Check & Seed Rich Realistic Emergency Shelters
        if Shelter.query.count() < 4:
            # Clear old vague shelters if any
            Shelter.query.delete()
            db.session.commit()

            sample_shelters = [
                Shelter(
                    name="Central Disaster Relief & Rescue Complex",
                    address="Sector 14, Connaught Place Avenue, Central District",
                    district="Central Delhi",
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
                    address="88 Riverside Boulevard, Civil Lines, North District",
                    district="North Delhi",
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
                    name="Metro Indoor Sports Stadium Relief Camp",
                    address="45 Sports City Boulevard, Laxmi Nagar, East District",
                    district="East Delhi",
                    latitude=28.5355,
                    longitude=77.3910,
                    total_capacity=1500,
                    available_beds=1120,
                    has_food=True,
                    has_water=True,
                    has_medical=True,
                    contact_number="+91-9876543212"
                ),
                Shelter(
                    name="Coastal High Ground Evacuation Refuge",
                    address="12 Beach Safety Highway, South Shore Zone",
                    district="South Shore",
                    latitude=28.4595,
                    longitude=77.0266,
                    total_capacity=600,
                    available_beds=85,
                    has_food=True,
                    has_water=True,
                    has_medical=False,
                    contact_number="+91-9876543213"
                ),
                Shelter(
                    name="Green Valley Community Relief Center",
                    address="Plot 52, Ring Road Bypass, West District",
                    district="West Delhi",
                    latitude=28.6500,
                    longitude=77.0800,
                    total_capacity=700,
                    available_beds=510,
                    has_food=True,
                    has_water=True,
                    has_medical=True,
                    contact_number="+91-9876543214"
                ),
                Shelter(
                    name="National Red Cross Flood Evacuation Camp",
                    address="Old Cantonment Road, Riverbank Ward",
                    district="North Haven",
                    latitude=28.7500,
                    longitude=77.1500,
                    total_capacity=1000,
                    available_beds=730,
                    has_food=True,
                    has_water=True,
                    has_medical=True,
                    contact_number="+91-9876543215"
                ),
                Shelter(
                    name="Sunrise High School Typhoon Shelter",
                    address="44 Ocean View Avenue, Coastal Belt",
                    district="South Shore",
                    latitude=28.4200,
                    longitude=77.0500,
                    total_capacity=350,
                    available_beds=40,
                    has_food=True,
                    has_water=True,
                    has_medical=False,
                    contact_number="+91-9876543216"
                ),
                Shelter(
                    name="Apex Medical Center Relief Annex",
                    address="10 Hospital Expressway, Knowledge Park",
                    district="Greater Noida",
                    latitude=28.4700,
                    longitude=77.5000,
                    total_capacity=500,
                    available_beds=310,
                    has_food=True,
                    has_water=True,
                    has_medical=True,
                    contact_number="+91-9876543217"
                )
            ]
            db.session.bulk_save_objects(sample_shelters)
            db.session.commit()
            print("[Database Seed] Created 8 detailed emergency relief shelters.")

        # 3. Check Active Alerts Seed
        if DisasterAlert.query.count() == 0:
            sample_alerts = [
                DisasterAlert(
                    title="Heavy Rainfall & Severe Flash Flood Warning",
                    disaster_type="Flood",
                    severity="Critical",
                    location="North Haven & Riverside Lowlands",
                    description="Severe precipitation exceeded 195mm. Water levels in local rivers approaching critical overflow marks. Citizens in low-lying sectors advised to move to designated shelters immediately.",
                    is_active=True
                ),
                DisasterAlert(
                    title="Cyclone Warning - High Wind Gusts (95 km/h)",
                    disaster_type="Cyclone",
                    severity="Warning",
                    location="South Shore Coastal Belt",
                    description="Wind speeds recorded up to 95 km/h. Coastal communities urged to remain indoors, stay away from window glass, and secure emergency supplies.",
                    is_active=True
                ),
                DisasterAlert(
                    title="Heatwave Advisory - High Temperature Alert (44°C)",
                    disaster_type="Heatwave",
                    severity="Advisory",
                    location="Central Plains & West District",
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
