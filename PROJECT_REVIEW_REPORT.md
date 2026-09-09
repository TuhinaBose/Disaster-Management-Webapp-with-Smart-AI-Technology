# ACADEMIC PROJECT REVIEW REPORT

---

## **PROJECT TITLE**
### **RADAR - Smart AI Disaster Management System**
*(Web-Based AI Emergency Assistance, Live Shelter Locator & Real-Time Disaster Risk Prediction System)*

---

| Project Metadata | Information |
| :--- | :--- |
| **Project Name** | RADAR - Smart AI Disaster Management System |
| **Repository URL** | [GitHub Repository](https://github.com/TuhinaBose/Disaster-Management-Webapp-with-Smart-AI-Technology) |
| **Target Domain** | Artificial Intelligence, Machine Learning, Web Technologies, Geographic Information Systems (GIS), Emergency Telemetry |
| **Primary Stack** | Python (Flask), Scikit-Learn, Leaflet.js, OpenStreetMap Overpass & Nominatim APIs, SQLite/MySQL (SQLAlchemy), Bootstrap 5 |
| **Document Purpose** | Comprehensive College Project Review Report (Review Phase / Mid-Term / Final Submission) |

---

## 1. ABSTRACT & PROJECT OVERVIEW

Disaster management requires rapid, accurate, and accessible information dissemination to minimize loss of life and coordinate relief operations efficiently. **RADAR** is an end-to-end, full-stack disaster management web platform integrated with Smart AI technology and real-time Geographic Information Systems (GIS). 

The application empowers citizens during natural calamities (floods, cyclones, earthquakes, heatwaves, and landslides) by providing:
1. **AI-driven Real-Time Disaster Risk Prediction**: Utilizing a trained Scikit-Learn Machine Learning classifier to analyze environmental telemetry (rainfall, river level, wind speed, temperature, humidity, and seismic magnitude).
2. **Cascading State & Village-Level Shelter Locator**: A 4-tier hierarchical location engine (**State &rarr; District &rarr; City/Village &rarr; Facility Type**) covering all 28 Indian States, Union Territories, Hill Stations, and landslide-prone mountain belts.
3. **Live OpenStreetMap Overpass API Integration**: Real-time automated discovery of local schools, colleges, hospitals, and emergency public buildings on an interactive dark-themed Leaflet map.
4. **GPS Telemetry & Emergency SOS System**: One-click distress signal broadcasting live GPS coordinates to the Admin Operations Control Room.
5. **RescuBot 24/7 AI Assistant**: Natural language processing chatbot for immediate emergency guidance, helpline access, and shelter telemetry.
6. **Centralized Admin Operations Control Room**: Role-Based Access Control (RBAC) portal for relief shelter management, active alert broadcasts, and SOS request queue dispatching.

---

## 2. SYSTEM ARCHITECTURE & TECHNICAL STACK

The platform is engineered using the Model-View-Controller (MVC) Architectural Pattern with modular Flask Blueprints:

```
                  ┌──────────────────────────────────────────────┐
                  │                 CLIENT / UI                  │
                  │   HTML5, CSS3, Bootstrap 5, JS ES6+, Leaflet  │
                  └──────────────────────┬───────────────────────┘
                                         │ HTTP / JSON REST APIs
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │           FLASK APPLICATION SERVER           │
                  │           (Gunicorn / WSGI Engine)           │
                  └──────┬───────────────┼───────────────┬───────┘
                         │               │               │
      ┌──────────────────┴──┐  ┌─────────┴─────────┐  ┌──┴──────────────────┐
      │     AUTH & MAIN     │  │   ADMIN OPERATIONS│  │   FEATURE & AI ML    │
      │  (User / Admin RBAC)│  │ (Shelters/SOS/Alert) │ (ML/OSM/RescuBot)  │
      └──────────┬──────────┘  └─────────┬─────────┘  └──┬──────────────────┘
                 │                       │               │
                 ▼                       ▼               ▼
      ┌──────────────────────────────────────────────────────────┐
      │          DATABASE LAYER (Flask-SQLAlchemy ORM)           │
      │              (SQLite / MySQL Relational Schema)          │
      └──────────────────────────────────────────────────────────┘
```

### **Tech Stack Breakdown**

| Layer | Component | Description / Function |
| :--- | :--- | :--- |
| **Frontend** | HTML5, Jinja2, Bootstrap 5, Custom CSS3 | Responsive dark-mode user interface optimized for mobile and desktop screens. |
| **Mapping & GIS** | Leaflet.js, OpenStreetMap, CartoDB Tiles | Interactive mapping layer with dynamic marker clustering and GPS location tracking. |
| **Backend Framework**| Python 3.x, Flask, Flask-SQLAlchemy | Modular MVC architecture organized into logical Blueprints (`main`, `admin`, `feature`). |
| **Machine Learning** | Scikit-Learn, Joblib, NumPy | `RandomForestClassifier` trained on multi-variate environmental factors for disaster risk assessment. |
| **Live External APIs**| OpenStreetMap Overpass & Nominatim APIs | Real-time geocoding and live spatial query engine for schools, colleges, hospitals, and shelters. |
| **Database** | SQLite (Dev) / MySQL (Prod) | Object-Relational Mapping (ORM) storing `User`, `Shelter`, `DisasterAlert`, and `EmergencyRequest` models. |

---

## 3. CORE MODULES & WORK ACCOMPLISHED

### **Module 1: Machine Learning Disaster Risk Predictor**
- **Algorithm**: Scikit-Learn `RandomForestClassifier` (100 estimators, max depth 12).
- **Features Analyzed**:
  - Rainfall Intensity ($mm$)
  - River / Water Level ($m$)
  - Wind Velocity ($km/h$)
  - Ambient Temperature ($^\circ C$)
  - Humidity Percentage ($\%$)
  - Seismic Richter Scale Magnitude
- **Performance**: Achieved **$97.5\%$ accuracy** on synthetic environmental validation data.
- **Output**: Returns real-time Risk Classification (**Low**, **Medium**, **High**) along with actionable safety recommendations.

### **Module 2: Cascading Administrative Location Engine**
- Implemented a 4-tier cascading hierarchy:
  $$\text{State / UT} \longrightarrow \text{District} \longrightarrow \text{City / Village / Tehsil} \longrightarrow \text{Facility Type}$$
- **Facility Classifications**:
  - 🏫 **School** (e.g. *St. Mary Emergency High School*)
  - 🎓 **College** (e.g. *Loyola College Relief Center*)
  - 🏥 **Hospital** (e.g. *Apex Medical Relief Annex*)
  - 🏛️ **Community Center** (e.g. *Central Relief Complex*)
  - 🏟️ **Stadium** (e.g. *Salt Lake Indoor Stadium Refuge*)
  - 🏢 **Building** (e.g. *Andheri Municipal Refuge*)
- **Nationwide Coverage**: Comprehensive geographic dataset covering all 28 Indian States, UTs, and specialized Hill Station & Landslide-prone regions (*Darjeeling, Shimla, Manali, Munnar, Ooty, Gangtok, Wayanad, Cherrapunji, Mussoorie, Nainital*).
- **Editable Datalist Auto-Complete**: Combines structured dropdowns with free-text typing support.

### **Module 3: Live OpenStreetMap Overpass & Nominatim API Integration**
- Built custom backend API `/api/search_facilities` and `/api/osm_facilities`.
- When a user filters by any city, village, or town (e.g. *Habra*, *Ashoknagar*, *Civil Lines*, *Canning*), the system:
  1. Performs multi-candidate reverse geocoding via OpenStreetMap Nominatim.
  2. Executes an Overpass API spatial query (`node["amenity"="school"](around:15000, lat, lon)`).
  3. Returns live local schools, colleges, hospitals, and public buildings directly onto the Leaflet map and search list—even if they are not pre-stored in the local database!

### **Module 4: Real-Time GPS Positioning & Telemetry**
- **Haversine Distance Formula**: Computes exact geodesic distance ($km$) between the user's live mobile GPS position and all relief centers:
  $$d = 2R \cdot \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta \lambda}{2}\right)}\right)$$
- **Live Distance Badges**: Displays distance badges (e.g. `📍 2.4 km from your live position`) on shelter cards.

### **Module 5: Emergency SOS Dispatch System**
- One-click SOS emergency button on mobile/desktop.
- Automatically captures current GPS latitude and longitude coordinates, emergency situation description, and contact info.
- Transmits distress calls directly to the Admin Operations Control Room in real-time.

### **Module 6: RescuBot 24/7 AI Assistant**
- Automated NLP rule-based AI assistant.
- Handles queries regarding open shelters, flood/earthquake/cyclone/fire/landslide safety advice, emergency helplines (108, 1078, 100, 101, 112), and user authentication guidance.
- Directly queries database telemetry to report live available shelter bed counts.

### **Module 7: Admin Operations & Role-Based Access Control (RBAC)**
- **Authentication**: Supports login using Username OR Email address.
- **Admin Interactive Map Location Picker**: Modal map allowing Admins to click anywhere on a Leaflet map to automatically populate exact Latitude, Longitude, and reverse-geocoded street addresses.
- **Full CRUD Management**: Admin interface to add, edit, or delete shelters, create active disaster warnings, and manage emergency request resolution states (*Pending*, *In Progress*, *Resolved*).

---

## 4. DATABASE SCHEMA & ENTITY-RELATIONSHIP ARCHITECTURE

The application utilizes SQLAlchemy ORM with four primary entities:

```
  ┌───────────────────────────┐         ┌───────────────────────────┐
  │           USER            │         │          SHELTER          │
  ├───────────────────────────┤         ├───────────────────────────┤
  │ id (PK, Integer)          │         │ id (PK, Integer)          │
  │ username (String)         │         │ name (String)             │
  │ email (String)            │         │ address (Text)            │
  │ password_hash (String)    │         │ state (String)            │
  │ role ('user' | 'admin')   │         │ district (String)         │
  │ created_at (DateTime)     │         │ city_village (String)     │
  └─────────────┬─────────────┘         │ facility_type (String)    │
                │ 1                     │ latitude (Float)          │
                │                       │ longitude (Float)         │
                │                       │ total_capacity (Integer)  │
                │ N                     │ available_beds (Integer)  │
  ┌─────────────┴─────────────┐         │ has_food (Boolean)        │
  │     EMERGENCY_REQUEST     │         │ has_water (Boolean)       │
  ├───────────────────────────┤         │ has_medical (Boolean)     │
  │ id (PK, Integer)          │         │ contact_number (String)   │
  │ user_id (FK -> User.id)   │         └───────────────────────────┘
  │ contact_name (String)     │
  │ phone_number (String)     │         ┌───────────────────────────┐
  │ urgency_level (String)    │         │      DISASTER_ALERT       │
  │ situation_desc (Text)     │         ├───────────────────────────┤
  │ latitude (Float)          │         │ id (PK, Integer)          │
  │ longitude (Float)         │         │ title (String)            │
  │ status (Pending/Resolved) │         │ disaster_type (String)    │
  │ created_at (DateTime)     │         │ severity (Critical/Warn)  │
  └───────────────────────────┘         │ location (String)         │
                                        │ description (Text)        │
                                        │ is_active (Boolean)       │
                                        └───────────────────────────┘
```

---

## 5. RECENT UPDATES & ENHANCEMENTS SUMMARY

1. **State & Village-Level Expansion**: Integrated comprehensive administrative dataset covering 28 States, UTs, and specific sub-districts/villages (e.g., all 31 towns/tehsils of North 24 Parganas including *Habra*, *Ashoknagar*, *Barasat*, *Barrackpore*, *Bidhannagar*, *Madhyamgram*, *Bangaon*, *Basirhat*, *Naihati*, *Bhatpara*, etc.).
2. **Hill Station & Landslide Risk Module**: Expanded coverage to major Indian hill stations (*Darjeeling, Shimla, Manali, Munnar, Ooty, Gangtok, Wayanad, Cherrapunji, Mussoorie, Nainital*) with landslide warning capabilities.
3. **Live OpenStreetMap Overpass Search Engine**: Implemented real-time Overpass API query integration to auto-discover local schools, colleges, hospitals, and emergency refuge buildings on demand.
4. **Interactive Map Location Picker for Admins**: Created a map click coordinate capture tool inside the Admin modal.
5. **Unified Login System**: Updated authentication logic so users and admins can log in using either their registered Username or Email address seamlessly.

---

## 6. VERIFICATION & TESTING RESULTS

The platform underwent rigorous testing across unit, integration, and API layers:

- **Authentication Test**: Verified successful login for both Citizen (`/login`) and Admin (`/admin/login`) credentials via Username & Email.
- **Shelter API Test**: Validated `GET /api/shelters` and `GET /api/search_facilities`, confirming dynamic JSON payloads containing both DB entries and live OpenStreetMap POIs.
- **Cascading Filter Test**: Verified `GET /api/location_options?state=West%20Bengal&district=North%2024%20Parganas` correctly returns dynamic town/village options.
- **Live OSM Search Test**: Validated OpenStreetMap Overpass queries for *Habra* and *Ashoknagar*, successfully returning 30+ real-time local schools, colleges, and hospitals.
- **Deployment Build Test**: Verified application execution on host `0.0.0.0:5000` and compatibility with Gunicorn production WSGI servers.

---

## 7. CONCLUSION & FUTURE SCOPE

The **RADAR - Smart AI Disaster Management System** successfully demonstrates the integration of Machine Learning risk modeling, real-time GIS mapping, live spatial APIs, and emergency response management into a cohesive, user-friendly platform.

---
*Report Prepared for College Project Technical Review Submission.*
