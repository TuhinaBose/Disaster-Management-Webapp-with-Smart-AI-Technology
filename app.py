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

        # 2. Check & Seed State -> District -> City/Village -> Facility Type Shelters
        if Shelter.query.count() < 10:
            Shelter.query.delete()
            db.session.commit()

            sample_shelters = [
                # ===== DELHI NCR =====
                Shelter(
                    name="Central Disaster Relief & Rescue Complex",
                    address="Sector 14, Connaught Place Avenue, Central District",
                    state="Delhi NCR",
                    district="Central Delhi",
                    city_village="Connaught Place",
                    facility_type="Community Center",
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
                    name="St. Mary Emergency High School Shelter",
                    address="88 Riverside Boulevard, Civil Lines",
                    state="Delhi NCR",
                    district="North Delhi",
                    city_village="Civil Lines",
                    facility_type="School",
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
                    address="45 Sports City Boulevard, Laxmi Nagar",
                    state="Delhi NCR",
                    district="East Delhi",
                    city_village="Laxmi Nagar",
                    facility_type="Stadium",
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
                    name="Apex Medical Relief Facility",
                    address="10 District Hospital Road, Saket",
                    state="Delhi NCR",
                    district="South Delhi",
                    city_village="Saket",
                    facility_type="Hospital",
                    latitude=28.5244,
                    longitude=77.2100,
                    total_capacity=500,
                    available_beds=310,
                    has_food=True,
                    has_water=True,
                    has_medical=True,
                    contact_number="+91-9876543213"
                ),

                # ===== MAHARASHTRA =====
                Shelter(
                    name="Mumbai National College Evacuation Center",
                    address="Opposite Marine Lines Station, South Mumbai",
                    state="Maharashtra",
                    district="Mumbai City",
                    city_village="Marine Lines",
                    facility_type="College",
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
                    name="Andheri Municipal Relief Building",
                    address="SV Road, Andheri West",
                    state="Maharashtra",
                    district="Mumbai Suburban",
                    city_village="Andheri West",
                    facility_type="Building",
                    latitude=19.1197,
                    longitude=72.8464,
                    total_capacity=700,
                    available_beds=410,
                    has_food=True,
                    has_water=True,
                    has_medical=True,
                    contact_number="+91-9876543221"
                ),
                Shelter(
                    name="Pune Model High School Relief Camp",
                    address="Shivajinagar Relief Grounds, Pune",
                    state="Maharashtra",
                    district="Pune",
                    city_village="Shivajinagar",
                    facility_type="School",
                    latitude=18.5308,
                    longitude=73.8474,
                    total_capacity=900,
                    available_beds=620,
                    has_food=True,
                    has_water=True,
                    has_medical=True,
                    contact_number="+91-9876543222"
                ),

                # ===== WEST BENGAL =====
                Shelter(
                    name="Salt Lake Indoor Stadium Refuge Center",
                    address="Park Circus Indoor Complex, Salt Lake",
                    state="West Bengal",
                    district="Kolkata",
                    city_village="Salt Lake City",
                    facility_type="Stadium",
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
                    name="Sundarbans Coastal Village Primary School Shelter",
                    address="Canning Safety Highway, South 24 Parganas",
                    state="West Bengal",
                    district="South 24 Parganas",
                    city_village="Canning Village",
                    facility_type="School",
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
                    name="Howrah Engineering College Relief Refuge",
                    address="Grand Trunk Road, Bally Town",
                    state="West Bengal",
                    district="Howrah",
                    city_village="Bally Town",
                    facility_type="College",
                    latitude=22.6500,
                    longitude=88.3400,
                    total_capacity=600,
                    available_beds=380,
                    has_food=True,
                    has_water=True,
                    has_medical=True,
                    contact_number="+91-9876543232"
                ),

                # ===== TAMIL NADU =====
                Shelter(
                    name="Chennai Loyola College Flood Relief Center",
                    address="Marina Beach Road, Mylapore",
                    state="Tamil Nadu",
                    district="Chennai",
                    city_village="Mylapore",
                    facility_type="College",
                    latitude=13.0405,
                    longitude=80.2707,
                    total_capacity=1000,
                    available_beds=720,
                    has_food=True,
                    has_water=True,
                    has_medical=True,
                    contact_number="+91-9876543240"
                ),

                # ===== KARNATAKA =====
                Shelter(
                    name="Bengaluru Urban Relief Operations Building",
                    address="M.G. Road Community Center, Indiranagar",
                    state="Karnataka",
                    district="Bengaluru Urban",
                    city_village="Indiranagar",
                    facility_type="Building",
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
            print("[Database Seed] Created 12 state/district/city/facility structured shelters.")

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
