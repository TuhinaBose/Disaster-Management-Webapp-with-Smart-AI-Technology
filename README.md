# Disaster Management Web Application with Smart AI Technology

A full-stack emergency response and disaster management web platform built using **Flask (Python)**, **Scikit-Learn Machine Learning**, **Bootstrap 5**, **JavaScript**, **Leaflet Maps**, and **MySQL / SQLite**.

---

## 🌟 Project Features Overview

1. **Home Page**: Hero section, live disaster awareness bulletin ticker, core action tiles, and real-time operational metric counters.
2. **AI Disaster Prediction**: Input rainfall, river gauge level, wind speed, temperature, humidity, and earthquake magnitude. Evaluated by a trained Scikit-Learn **Random Forest Classifier** to compute Low, Medium, or High risk with dynamic threat gauges and safety recommendations.
3. **Nearby Shelter Locator**: Filter emergency shelters by district or location, check total capacity and live bed availability, view amenities (Food, Water, Medical Desk), call shelters, and inspect live locations on **Leaflet interactive map**.
4. **Live Weather & Disaster Alerts**: Weather overview card and active warning cards categorized by severity levels (*Critical*, *Warning*, *Advisory*).
5. **Emergency SOS System**: One-click SOS trigger capturing browser GPS coordinates, dispatching emergency rescue requests, and providing direct access to national helpline numbers (108 Ambulance, 100 Police, 101 Fire, 1078 NDRF).
6. **Safety Guidelines**: Interactive survival guides and step-by-step checklists for Floods, Earthquakes, Cyclones, Fires, and Heatwaves, plus an interactive printable Emergency Survival Kit checklist.
7. **Admin Operations Control Room**: Authenticated admin dashboard (`admin` / `admin123`) to manage shelters, publish disaster alerts, update emergency SOS request statuses (*Pending* $\rightarrow$ *In Progress* $\rightarrow$ *Resolved*), and monitor AI prediction logs.
8. **Interactive RescuBot AI Assistant**: Floating AI assistant available on every page to answer disaster safety queries, locate shelters, and guide emergency actions.

---

## 📁 Directory Structure

```text
disaster_management_app/
├── app.py                      # Main Flask application entry point
├── config.py                   # Application configuration & MySQL/SQLite setup
├── database.py                 # SQLAlchemy database setup
├── schema.sql                  # Raw MySQL schema & seed data script
├── train_model.py              # ML Model training script (Random Forest)
├── requirements.txt            # Python dependencies
├── README.md                   # Setup guide and documentation
│
├── models/                     # Database Data Models & AI Engine
│   ├── __init__.py
│   ├── user.py                 # User & Admin account model
│   ├── shelter.py              # Shelter details & bed capacity model
│   ├── alert.py                # Disaster alert model
│   ├── request.py              # Emergency SOS request model
│   ├── prediction.py           # AI prediction history model
│   └── ai_model.py             # ML inference engine & recommendation logic
│
├── routes/                     # Modular Controllers (Flask Blueprints)
│   ├── __init__.py
│   ├── main_routes.py          # Public home, safety & weather routes
│   ├── feature_routes.py       # AI Predict, Shelters, SOS & Chatbot API
│   └── admin_routes.py         # Admin authentication & CRUD control routes
│
├── static/                     # Assets & Client Scripts
│   ├── css/
│   │   └── style.css           # Custom emergency dark slate & glassmorphism theme
│   ├── js/
│   │   ├── main.js             # General UI scripts
│   │   ├── predict.js          # AI Risk Prediction AJAX & score gauge
│   │   ├── shelter_map.js      # Leaflet map pins & capacity script
│   │   ├── sos.js              # Geolocation API capture script
│   │   └── chatbot.js          # RescuBot floating widget handler
│   └── model/
│       └── disaster_model.joblib # Serialized Scikit-learn model
│
└── templates/                  # Jinja2 HTML Templates
    ├── base.html               # Main layout skeleton & navigation bar
    ├── index.html              # Home page
    ├── predict.html            # AI Prediction tool
    ├── shelters.html           # Shelter locator & Leaflet map
    ├── alerts.html             # Weather & severe disaster alerts
    ├── sos.html                # SOS dispatch & helpline directory
    ├── safety.html             # Safety guidelines & emergency kit
    └── admin/
        ├── login.html          # Admin login page
        ├── dashboard.html      # Admin operations control room
        ├── shelters_mgmt.html  # Shelter manager (Add/Edit/Delete)
        ├── alerts_mgmt.html    # Disaster alert publisher
        └── sos_mgmt.html       # SOS request queue manager
```

---

## 🛠️ Step-by-Step Installation & Setup Guide

### 1. Prerequisites
- **Python 3.8+** installed on your system.
- *(Optional)* **MySQL Server** (If you wish to use MySQL instead of default SQLite).

### 2. Open Project in VSCode
Open VSCode and navigate to the project directory:
```bash
cd C:\Users\91914\.gemini\antigravity\scratch\disaster_management_app
```

### 3. Create & Activate Virtual Environment
```bash
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🧠 Step 5: Train the AI Machine Learning Model

Run the training script to generate the Scikit-learn model (`static/model/disaster_model.joblib`):
```bash
python train_model.py
```
*Expected Output:*
> Model Training Complete! Accuracy: 98.50%  
> Model saved successfully to `static/model/disaster_model.joblib`

---

## 🗄️ Step 6: Database Configuration (SQLite vs MySQL)

### Option A: Standard SQLite Execution (Default Zero-Config Setup)
The application is pre-configured to automatically create `disaster_app.db` with all tables and sample seed data (shelters, alerts, admin user) on first run! No MySQL server setup is required.

### Option B: Switching to MySQL Server
If you prefer running on MySQL:
1. Open your MySQL client (phpMyAdmin, Workbench, or terminal) and execute `schema.sql`:
   ```bash
   mysql -u root -p < schema.sql
   ```
2. Edit `config.py` (or set environment variables):
   ```python
   USE_MYSQL = True
   SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:your_password@localhost:3306/disaster_db'
   ```

---

## 🚀 Step 7: Running the Web Application

Launch the Flask server:
```bash
python app.py
```

Open your browser and visit:
- **Public App**: `http://127.0.0.1:5000`
- **Admin Login Portal**: `http://127.0.0.1:5000/admin/login`

### 🔑 Default Admin Credentials:
- **Username**: `admin`
- **Password**: `admin123`

---

## 🔮 Future Enhancements
- **Live OpenWeather API Integration**: Connect real live location weather telemetry.
- **SMS Distress Broadcasting**: Integrate Twilio API to automatically send SMS to emergency contacts when SOS is triggered.
- **Deep Learning Flood Severity Mapping**: High-resolution GIS elevation map overlays.
