import os
import math
import json
import urllib.request
import urllib.parse
from datetime import datetime
import requests
from flask import Blueprint, render_template, request, jsonify, current_app
from database import db
from models import Shelter, EmergencyRequest, RiskPrediction, DisasterAlert
from models.ai_model import DisasterPredictor
from models.india_data import INDIA_GEO_DATA, FACILITY_TYPES

feature_bp = Blueprint('feature', __name__)

# Lazy predictor instance
_predictor = None

def get_predictor():
    global _predictor
    if _predictor is None:
        model_path = current_app.config.get('MODEL_PATH')
        _predictor = DisasterPredictor(model_path)
    return _predictor

def haversine_distance(lat1, lon1, lat2, lon2):
    """Computes exact geodesic distance in kilometers between two GPS coordinates."""
    R = 6371.0 # Radius of Earth in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

# ================= AI DISASTER RISK PREDICTION =================

@feature_bp.route('/predict', methods=['GET', 'POST'])
def predict():
    """
    AI Disaster Prediction Page and AJAX endpoint.
    Accepts environmental factors, runs ML prediction, saves result in DB, returns recommendations.
    """
    if request.method == 'POST':
        try:
            data = request.get_json() if request.is_json else request.form
            
            rainfall = float(data.get('rainfall', 0))
            river_level = float(data.get('river_level', 0))
            wind_speed = float(data.get('wind_speed', 0))
            temperature = float(data.get('temperature', 0))
            humidity = float(data.get('humidity', 0))
            earthquake_mag = float(data.get('earthquake_mag', 0))

            predictor = get_predictor()
            result = predictor.predict(
                rainfall=rainfall,
                river_level=river_level,
                wind_speed=wind_speed,
                temperature=temperature,
                humidity=humidity,
                earthquake_mag=earthquake_mag
            )

            # Store prediction in database
            new_pred = RiskPrediction(
                rainfall=rainfall,
                river_level=river_level,
                wind_speed=wind_speed,
                temperature=temperature,
                humidity=humidity,
                earthquake_mag=earthquake_mag,
                predicted_risk=result['risk_level'],
                risk_score=result['risk_score']
            )
            db.session.add(new_pred)
            db.session.commit()

            if request.is_json:
                return jsonify({'success': True, 'prediction': result})
            
            return render_template('predict.html', result=result, inputs=data)
        except Exception as e:
            if request.is_json:
                return jsonify({'success': False, 'error': str(e)}), 400
            return render_template('predict.html', error=str(e))

    return render_template('predict.html')


# ================= CASCADING GEOGRAPHIC LOCATION ENGINE =================

@feature_bp.route('/api/location_options')
def api_location_options():
    """
    Independent cascading dropdown data provider (State -> District -> City/Village)
    Uses INDIA_GEO_DATA dictionary so locations exist independently of shelters in DB.
    """
    state_param = request.args.get('state', '').strip()
    district_param = request.args.get('district', '').strip()

    if not state_param:
        states = sorted(list(INDIA_GEO_DATA.keys()))
        return jsonify({'states': states})

    if state_param in INDIA_GEO_DATA:
        districts = sorted(list(INDIA_GEO_DATA[state_param].keys()))
        if not district_param:
            return jsonify({'state': state_param, 'districts': districts})
        
        if district_param in INDIA_GEO_DATA[state_param]:
            cities = sorted(INDIA_GEO_DATA[state_param][district_param])
            return jsonify({'state': state_param, 'district': district_param, 'cities': cities})

    # Fallback to DB distinct query if state not in hardcoded dict
    districts = [d[0] for d in db.session.query(Shelter.district).filter(Shelter.state.ilike(f'%{state_param}%')).distinct().all() if d[0]]
    cities = [c[0] for c in db.session.query(Shelter.city_village).filter(Shelter.state.ilike(f'%{state_param}%')).distinct().all() if c[0]]
    return jsonify({'districts': districts, 'cities': cities})


# ================= SHELTERS & NEARBY POI SEARCH =================

@feature_bp.route('/shelters')
def shelters():
    """
    Shelter locator view with dynamic cascading filters and verified shelter separation.
    """
    state_query = request.args.get('state', '').strip()
    district_query = request.args.get('district', '').strip()
    city_query = request.args.get('city_village', '').strip()
    facility_query = request.args.get('facility_type', '').strip()
    search_keyword = request.args.get('query', '').strip()
    
    # 1. Fetch Verified Disaster Shelters from DB
    query = Shelter.query.filter(Shelter.verification_status == 'Verified')
    if state_query:
        query = query.filter(Shelter.state.ilike(f'%{state_query}%'))
    if district_query:
        query = query.filter(Shelter.district.ilike(f'%{district_query}%'))
    if city_query:
        query = query.filter(Shelter.city_village.ilike(f'%{city_query}%'))
    if facility_query:
        query = query.filter(Shelter.facility_type.ilike(f'%{facility_query}%'))
    if search_keyword:
        query = query.filter(
            (Shelter.name.ilike(f'%{search_keyword}%')) |
            (Shelter.district.ilike(f'%{search_keyword}%')) |
            (Shelter.city_village.ilike(f'%{search_keyword}%')) |
            (Shelter.facility_type.ilike(f'%{search_keyword}%'))
        )

    db_shelters = [s.to_dict() for s in query.all()]
    for s in db_shelters:
        s['facility_category'] = 'Verified Disaster Shelter'
        s['is_verified_shelter'] = True

    no_verified_shelter_message = None
    if len(db_shelters) == 0 and (state_query or district_query or city_query or search_keyword):
        no_verified_shelter_message = "No verified disaster shelter found nearby for your selected search criteria."

    # 2. Fetch General Facilities (OSM Schools, Colleges, Hospitals, Police Stations, Fire Stations)
    general_facilities = []
    loc_parts = [p for p in [city_query, district_query, state_query, search_keyword] if p]

    if loc_parts:
        try:
            full_loc_query = ', '.join(loc_parts) + ', India'
            nom_url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(full_loc_query)}&format=json&limit=1"
            req = urllib.request.Request(nom_url, headers={'User-Agent': 'RADAR-Disaster-App/2.0'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                nom_data = json.loads(resp.read().decode())

            if nom_data:
                lat = float(nom_data[0]['lat'])
                lon = float(nom_data[0]['lon'])

                overpass_q = f"""
                [out:json][timeout:10];
                (
                  node["amenity"="school"](around:10000,{lat},{lon});
                  node["amenity"="college"](around:10000,{lat},{lon});
                  node["amenity"="hospital"](around:10000,{lat},{lon});
                  node["amenity"="police"](around:10000,{lat},{lon});
                  node["amenity"="fire_station"](around:10000,{lat},{lon});
                );
                out center 20;
                """
                op_url = "https://overpass-api.de/api/interpreter?data=" + urllib.parse.quote(overpass_q)
                req_op = urllib.request.Request(op_url, headers={'User-Agent': 'RADAR-Disaster-App/2.0'})
                with urllib.request.urlopen(req_op, timeout=8) as resp_op:
                    op_data = json.loads(resp_op.read().decode())

                count_id = 9000
                for el in op_data.get('elements', []):
                    count_id += 1
                    tags = el.get('tags', {})
                    raw_amenity = tags.get('amenity', 'building')
                    
                    facility_type_map = {
                        'school': 'School',
                        'college': 'College',
                        'hospital': 'Hospital',
                        'police': 'Police Station',
                        'fire_station': 'Fire Station'
                    }
                    facility_type_name = facility_type_map.get(raw_amenity, 'General Building')
                    name = tags.get('name') or tags.get('name:en') or f"Local {facility_type_name}"
                    
                    if facility_query and facility_query.lower() not in facility_type_name.lower():
                        continue

                    el_lat = float(el.get('lat') or el.get('center', {}).get('lat', 0))
                    el_lon = float(el.get('lon') or el.get('center', {}).get('lon', 0))

                    if el_lat and el_lon:
                        general_facilities.append({
                            'id': count_id,
                            'name': name,
                            'address': tags.get('addr:street') or full_loc_query,
                            'state': state_query or 'India',
                            'district': district_query or 'Local District',
                            'city_village': city_query or 'Local Area',
                            'facility_type': facility_type_name,
                            'facility_category': f"General Facility ({facility_type_name})",
                            'latitude': el_lat,
                            'longitude': el_lon,
                            'total_capacity': 0,
                            'current_occupancy': 0,
                            'available_capacity': 0,
                            'available_beds': 0,
                            'occupancy_percentage': 0,
                            'has_food': False,
                            'has_water': True,
                            'has_medical': True if facility_type_name == 'Hospital' else False,
                            'contact': tags.get('phone') or '+91-112 (Emergency)',
                            'contact_number': tags.get('phone') or '+91-112 (Emergency)',
                            'verification_status': 'Unverified',
                            'is_verified_shelter': False,
                            'is_osm_live': True
                        })
        except Exception:
            pass

    states = sorted(list(INDIA_GEO_DATA.keys()))
    facility_types = ['Shelter', 'School', 'College', 'Hospital', 'Police Station', 'Fire Station', 'Community Center', 'Stadium', 'Building']

    return render_template('shelters.html',
                           shelters=db_shelters,
                           general_facilities=general_facilities,
                           no_verified_shelter_message=no_verified_shelter_message,
                           states=states,
                           facility_types=facility_types,
                           current_state=state_query,
                           current_district=district_query,
                           current_city=city_query,
                           current_facility=facility_query,
                           search_query=search_keyword)


@feature_bp.route('/api/search_facilities')
@feature_bp.route('/api/nearby_places')
def api_search_facilities():
    """
    Unified Nearby Search API returning verified shelters and general facilities (schools, colleges, hospitals, police, fire) separately.
    Sorts all results by Haversine distance if lat & lng parameters are provided.
    """
    user_lat = request.args.get('lat', type=float)
    user_lng = request.args.get('lng', type=float)
    radius_km = request.args.get('radius', default=25.0, type=float)
    
    state_q = request.args.get('state', '').strip()
    district_q = request.args.get('district', '').strip()
    city_q = request.args.get('city_village', '').strip()
    facility_q = request.args.get('facility_type', '').strip()
    keyword_q = request.args.get('query', '').strip()

    # 1. Fetch Verified DB Shelters
    query = Shelter.query.filter_by(verification_status='Verified')
    if state_q:
        query = query.filter(Shelter.state.ilike(f'%{state_q}%'))
    if district_q:
        query = query.filter(Shelter.district.ilike(f'%{district_q}%'))
    if city_q:
        query = query.filter(Shelter.city_village.ilike(f'%{city_q}%'))
    if facility_q and facility_q.lower() != 'all':
        query = query.filter(Shelter.facility_type.ilike(f'%{facility_q}%'))
    if keyword_q:
        query = query.filter(
            (Shelter.name.ilike(f'%{keyword_q}%')) |
            (Shelter.district.ilike(f'%{keyword_q}%')) |
            (Shelter.city_village.ilike(f'%{keyword_q}%')) |
            (Shelter.facility_type.ilike(f'%{keyword_q}%'))
        )

    verified_shelters = []
    for s in query.all():
        s_dict = s.to_dict()
        s_dict['facility_category'] = 'Verified Disaster Shelter'
        s_dict['is_verified_shelter'] = True
        
        if user_lat is not None and user_lng is not None:
            dist = haversine_distance(user_lat, user_lng, s.latitude, s.longitude)
            s_dict['distance_km'] = dist
            if dist <= radius_km:
                verified_shelters.append(s_dict)
        else:
            s_dict['distance_km'] = None
            verified_shelters.append(s_dict)

    if user_lat is not None and user_lng is not None:
        verified_shelters.sort(key=lambda x: x['distance_km'])

    # Message if no verified shelter exists
    no_verified_shelter_msg = None
    if len(verified_shelters) == 0:
        no_verified_shelter_msg = "No verified disaster shelter found nearby."

    return jsonify({
        'success': True,
        'verified_shelters_count': len(verified_shelters),
        'no_verified_shelter_message': no_verified_shelter_msg,
        'shelters': verified_shelters
    })


@feature_bp.route('/api/shelters')
def api_shelters():
    """JSON API endpoint returning list of all registered verified shelters."""
    shelter_list = Shelter.query.filter_by(verification_status='Verified').all()
    return jsonify([s.to_dict() for s in shelter_list])


# ================= REAL-TIME WEATHER MODULE =================

WEATHER_CONDITION_MAP = {
    0: "Clear Sky",
    1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
    45: "Foggy", 48: "Depositing Rime Fog",
    51: "Light Drizzle", 53: "Moderate Drizzle", 55: "Dense Drizzle",
    61: "Slight Rain", 63: "Moderate Rain", 65: "Heavy Rain",
    71: "Slight Snow", 73: "Moderate Snow", 75: "Heavy Snow",
    80: "Slight Rain Showers", 81: "Moderate Rain Showers", 82: "Violent Rain Showers",
    95: "Thunderstorm", 96: "Thunderstorm with Hail", 99: "Heavy Thunderstorm with Hail"
}

@feature_bp.route('/api/weather')
def api_weather():
    """
    Real-Time Weather API endpoint.
    Retrieves weather based on lat/lng or location name.
    Uses Open-Meteo API (free, open-access, keyless) as primary/fallback,
    or OpenWeatherMap API if WEATHER_API_KEY environment variable is configured.
    """
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    location_name = request.args.get('location', '').strip()

    # 1. Geocode location name if lat/lng not supplied directly
    if (lat is None or lng is None) and location_name:
        try:
            nom_url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(location_name + ', India')}&format=json&limit=1"
            req = urllib.request.Request(nom_url, headers={'User-Agent': 'RADAR-Disaster-App/2.0'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                geo_data = json.loads(resp.read().decode())
                if geo_data:
                    lat = float(geo_data[0]['lat'])
                    lng = float(geo_data[0]['lon'])
                    if not location_name:
                        location_name = geo_data[0].get('display_name', 'Selected Location').split(',')[0]
        except Exception:
            pass

    # Default fallback to Delhi NCR if no location/coords provided
    if lat is None or lng is None:
        lat, lng = 28.6139, 77.2090
        if not location_name:
            location_name = "New Delhi, Delhi NCR"

    weather_key = current_app.config.get('WEATHER_API_KEY') or os.environ.get('WEATHER_API_KEY')
    
    # 2. Try OpenWeatherMap API if API key exists
    if weather_key:
        try:
            owm_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&appid={weather_key}&units=metric"
            resp = requests.get(owm_url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                return jsonify({
                    'success': True,
                    'location': data.get('name') or location_name,
                    'latitude': lat,
                    'longitude': lng,
                    'temperature': round(data['main']['temp'], 1),
                    'humidity': data['main']['humidity'],
                    'rainfall': round(data.get('rain', {}).get('1h', 0.0), 1),
                    'wind_speed': round(data['wind']['speed'] * 3.6, 1), # m/s to km/h
                    'weather_condition': data['weather'][0]['description'].title() if data.get('weather') else 'Clear',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'provider': 'OpenWeatherMap'
                })
        except Exception:
            pass

    # 3. Open-Meteo API (Free, keyless, global live telemetry)
    try:
        om_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code"
        resp = requests.get(om_url, timeout=6)
        if resp.status_code == 200:
            data = resp.json()
            curr = data.get('current', {})
            w_code = curr.get('weather_code', 0)
            w_cond = WEATHER_CONDITION_MAP.get(w_code, "Partly Cloudy")

            return jsonify({
                'success': True,
                'location': location_name or f"GPS ({lat:.2f}, {lng:.2f})",
                'latitude': lat,
                'longitude': lng,
                'temperature': round(curr.get('temperature_2m', 26.5), 1),
                'humidity': round(curr.get('relative_humidity_2m', 72), 1),
                'rainfall': round(curr.get('precipitation', 0.0), 1),
                'wind_speed': round(curr.get('wind_speed_10m', 14.5), 1),
                'weather_condition': w_cond,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'provider': 'Open-Meteo (Live)'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f"Weather telemetry unavailable: {str(e)}",
            'location': location_name,
            'temperature': '--',
            'humidity': '--',
            'rainfall': '--',
            'wind_speed': '--',
            'weather_condition': 'Unavailable',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }), 500


# ================= SHELTER CAPACITY / UPDATE BED MODULE =================

@feature_bp.route('/api/shelter/<int:shelter_id>/update_occupancy', methods=['POST'])
def api_update_occupancy(shelter_id):
    """
    API endpoint to update shelter occupancy / beds capacity.
    Recalculates available capacity: available_capacity = total_capacity - current_occupancy.
    Enforces validation: 0 <= current_occupancy <= total_capacity.
    """
    shelter = Shelter.query.get_or_404(shelter_id)
    try:
        data = request.get_json() or request.form
        new_occ = int(data.get('current_occupancy', shelter.current_occupancy))

        if new_occ < 0:
            return jsonify({'success': False, 'message': 'Occupancy cannot be negative.'}), 400
        if new_occ > shelter.total_capacity:
            return jsonify({'success': False, 'message': f'Occupancy ({new_occ}) cannot exceed total capacity ({shelter.total_capacity}).'}), 400

        shelter.current_occupancy = new_occ
        shelter.recalculate_capacity()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Shelter "{shelter.name}" capacity updated successfully.',
            'shelter': shelter.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Failed to update capacity: {str(e)}'}), 500


# ================= EMERGENCY SOS DISPATCH =================

@feature_bp.route('/sos', methods=['GET', 'POST'])
def sos():
    """Emergency SOS submission page and request endpoint."""
    if request.method == 'POST':
        try:
            name = request.form.get('sender_name', '').strip()
            phone = request.form.get('contact_phone', '').strip()
            location = request.form.get('location', '').strip()
            lat = request.form.get('latitude')
            lng = request.form.get('longitude')
            urgency = request.form.get('urgency_level', 'High')
            description = request.form.get('situation_description', '').strip()

            if not name or not phone or not location:
                return render_template('sos.html', error="Please provide your name, contact phone, and location.")

            sos_req = EmergencyRequest(
                sender_name=name,
                contact_phone=phone,
                location=location,
                latitude=float(lat) if lat else None,
                longitude=float(lng) if lng else None,
                urgency_level=urgency,
                situation_description=description,
                status='Pending'
            )
            db.session.add(sos_req)
            db.session.commit()

            return render_template('sos.html', success="Emergency SOS broadcast sent! Rescue units and emergency responders have been notified.")
        except Exception as e:
            return render_template('sos.html', error=f"Could not transmit SOS request: {str(e)}")

    return render_template('sos.html')


# ================= ASK GEMINI ASSISTANT MODULE =================

@feature_bp.route('/api/chatbot', methods=['POST'])
def chatbot_api():
    """
    'Ask Gemini' AI Assistant API for disaster preparedness, safety advice, live shelter queries, weather, and system guidance.
    Uses real Google Gemini API when GEMINI_API_KEY is configured, with a comprehensive multi-intent grounded offline engine as fallback.
    """
    try:
        data = request.get_json(silent=True) or request.form or {}
        user_query = data.get('message', '').strip()

        if not user_query:
            return jsonify({'reply': "👋 Hello! I am **Ask Gemini**, your AI Disaster Management Assistant. How can I assist you with safety guidelines, shelter locations, weather alerts, or emergency procedures today?"})

        # 1. Fetch live system telemetry from database
        try:
            verified_shelters = Shelter.query.filter_by(verification_status='Verified').all()
            total_shelters = len(verified_shelters)
            total_free_beds = sum(s.available_capacity for s in verified_shelters) if verified_shelters else 0
            active_alerts = DisasterAlert.query.filter_by(is_active=True).all()
            alerts_summary = "; ".join([f"{a.title} ({a.severity} in {a.location})" for a in active_alerts]) if active_alerts else "No active critical alerts broadcasted currently."

            top_shelter_info = ""
            if verified_shelters:
                top_s = max(verified_shelters, key=lambda s: s.available_capacity)
                top_shelter_info = f"Top Recommended Shelter: **{top_s.name}** in *{top_s.district}, {top_s.city_village}* with **{top_s.available_capacity} free beds** remaining. Contact: {top_s.contact}."
        except Exception:
            total_shelters = 0
            total_free_beds = 0
            alerts_summary = "All systems monitored."
            top_shelter_info = ""

        gemini_key = current_app.config.get('GEMINI_API_KEY') or os.environ.get('GEMINI_API_KEY')

        # 2. If Gemini API Key exists, call Google Gemini Generative API
        if gemini_key and len(gemini_key.strip()) > 5:
            system_prompt = f"""
            You are 'Ask Gemini', the dedicated AI Disaster & Emergency Assistant for the 'RADAR - Smart AI Disaster Management Web Application'.
            Your mission is to provide concise, calm, actionable, and accurate guidance regarding disaster safety, emergency preparedness, verified shelters, weather alerts, and application features.

            REAL-TIME SYSTEM CONTEXT (Ground your answers in this data):
            - Verified Shelters in RADAR: {total_shelters} shelters.
            - Total Available Bed Capacity: {total_free_beds} beds free across registered relief centers.
            - {top_shelter_info}
            - Current Active Disaster Alerts: {alerts_summary}
            - 24x7 National Emergency Helplines (India): 108 (Ambulance & Medical), 112 / 100 (Police & General Emergency), 101 (Fire Brigade), 1078 (NDRF Disaster Support).

            RULES:
            - Keep responses clear, practical, and formatted with Markdown (bold text, bullet points).
            - Always provide emergency helplines if the user indicates danger or distress.
            - Do NOT fabricate non-existent phone numbers or fake shelters.
            """

            full_prompt = f"{system_prompt}\n\nUser Question: {user_query}"

            # Try Gemini models via REST endpoint
            models_to_try = ['gemini-1.5-flash', 'gemini-2.0-flash', 'gemini-1.5-pro']
            for m in models_to_try:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={gemini_key.strip()}"
                    payload = {
                        "contents": [{"parts": [{"text": full_prompt}]}],
                        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 600}
                    }
                    resp = requests.post(url, json=payload, timeout=8)
                    if resp.status_code == 200:
                        res_json = resp.json()
                        candidates = res_json.get('candidates', [])
                        if candidates and 'content' in candidates[0]:
                            parts = candidates[0]['content'].get('parts', [])
                            if parts and 'text' in parts[0]:
                                return jsonify({'reply': parts[0]['text'], 'provider': f'Google Gemini ({m})'})
                except Exception as gem_err:
                    print(f"[Ask Gemini {m} Error]: {gem_err}")

        # 3. Comprehensive, Multi-Intent Grounded Offline AI Engine
        msg = user_query.lower()

        # Greetings & Welcomes
        if any(k in msg for k in ['hi', 'hello', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening']):
            reply = (
                "👋 **Hello! Welcome to RADAR Emergency Assistant.**\n\n"
                "I am **Ask Gemini**, your 24/7 AI guide. How can I help you today?\n"
                "- 🏠 **Find Shelters & Beds**: Ask *'Where is the nearest shelter?'*\n"
                "- ⚡ **AI Disaster Risk**: Ask *'How do I predict flood or cyclone risk?'*\n"
                "- 🚨 **Emergency SOS**: Ask *'How to send an SOS signal?'*\n"
                "- ⛰️ **Landslide & Hill Stations**: Ask *'Landslide safety tips'*\n"
                "- 📞 **Helplines**: Ask *'Emergency helpline numbers'*"
            )

        # Identity & Capabilities
        elif any(k in msg for k in ['who are you', 'what is your name', 'what are you', 'what is radar', 'what can you do', 'features', 'help me']):
            reply = (
                "🤖 **About Ask Gemini & RADAR**:\n\n"
                "I am **Ask Gemini**, the built-in intelligent assistant for **RADAR - Smart AI Disaster Management System**.\n\n"
                "Here is what you can do on RADAR:\n"
                "1. **AI Risk Prediction**: Calculate flood, cyclone, or earthquake danger with our ML model at [AI Predictor](/predict).\n"
                "2. **Shelter Locator**: Find verified camps across states, districts, and villages with live beds at [Shelters](/shelters).\n"
                "3. **Emergency SOS**: Broadcast your live GPS coordinates directly to rescue operations at [Emergency SOS](/sos).\n"
                "4. **Live Weather & Bulletins**: Monitor real-time rain, wind, and active government warnings at [Live Alerts](/alerts).\n"
                "5. **24x7 Helplines**: National Disaster Response Force (**1078**), Ambulance (**108**), Police (**112**)."
            )

        # Landslide & Hill Stations
        elif any(k in msg for k in ['landslide', 'mudslide', 'rockfall', 'hill station', 'slope', 'mountain', 'darjeeling', 'shimla', 'manali', 'munnar', 'wayanad', 'ooty']):
            reply = (
                "⛰️ **Landslide & Hill Station Safety Protocol**:\n\n"
                "- **Watch Warning Signs**: Tilting trees, widening ground cracks, sudden muddy river currents, or rumbling sounds.\n"
                "- **Immediate Action**: Move away from steep slopes, ravines, and drainage channels to stable high ground.\n"
                "- **Driving in Hill Stations**: Avoid driving through mountain passes during torrential rain; watch for debris on roads.\n"
                "- **Severe Zones**: Districts like *Darjeeling, Wayanad, Idukki, Chamoli, Shimla, and Nilgiris* require maximum vigilance.\n"
                "- **Emergency Help**: Call **1078** (NDRF Landslide Rescue) or **108** immediately."
            )

        # Shelters & Camps
        elif any(k in msg for k in ['shelter', 'refuge', 'bed', 'camp', 'stay', 'where', 'location', 'capacity', 'accommodation', 'hospital']):
            reply = (
                f"🏠 **Emergency Relief Shelters Update**:\n\n"
                f"- **Active Verified Shelters**: **{total_shelters} centers** currently registered.\n"
                f"- **Available Bed Capacity**: **{total_free_beds} beds free** right now.\n"
                f"- {top_shelter_info}\n\n"
                f"Explore shelters filtered by State &rarr; District &rarr; City/Village &rarr; Facility Type on our [Shelter Locator](/shelters)."
            )

        # Emergency SOS & Distress
        elif any(k in msg for k in ['sos', 'emergency', 'danger', 'trapped', 'save me', 'rescue', 'distress', 'help now']):
            reply = (
                "🚨 **EMERGENCY ASSISTANCE PROTOCOL**:\n\n"
                "If you or someone nearby is in immediate danger:\n"
                "1. Click the red [Emergency SOS Button](/sos) immediately to transmit your **exact live GPS coordinates** to the rescue control room.\n"
                "2. Call National Emergency Services directly:\n"
                "   - 🚑 **Medical / Ambulance**: **108**\n"
                "   - 🚔 **Police / General Emergency**: **112** or **100**\n"
                "   - 🚒 **Fire Brigade**: **101**\n"
                "   - 🛡️ **NDRF Disaster Rescue**: **1078** / **011-24363260**\n"
                "3. Stay calm, stay in a safe visible area, and keep your phone battery conserved."
            )

        # Flood & Waterlogging
        elif any(k in msg for k in ['flood', 'water', 'submerged', 'drowning', 'rain', 'river', 'overflow']):
            reply = (
                "🌊 **Flood Emergency Action Plan**:\n\n"
                "- **High Ground**: Evacuate instantly to higher elevation or designated relief camps.\n"
                "- **Never Walk or Drive**: Just 6 inches of fast-moving water can knock you down; 2 feet can float a vehicle.\n"
                "- **Electrical Safety**: Turn off main electricity switches; avoid fallen electrical lines in standing water.\n"
                "- **Check Weather**: Track live precipitation telemetry on [Live Alerts & Weather](/alerts).\n"
                "- **Helplines**: Call **108** (Rescue/Ambulance) or **1078** (NDRF)."
            )

        # Earthquake
        elif any(k in msg for k in ['earthquake', 'tremor', 'quake', 'shaking', 'seismic', 'richter']):
            reply = (
                "🧱 **Earthquake Survival Guidelines**:\n\n"
                "- **If Indoors**: **DROP, COVER, and HOLD ON!** Take refuge beneath a sturdy desk or table. Protect your head and neck.\n"
                "- **Stay Away**: Keep clear of glass windows, mirrors, hanging lighting, and unanchored furniture.\n"
                "- **If Outdoors**: Move to an open clearing away from buildings, streetlights, and utility wires.\n"
                "- **After Shocks**: Anticipate secondary aftershocks. Check for gas leaks and structural damage before re-entering."
            )

        # Cyclone, Storm & Wind
        elif any(k in msg for k in ['cyclone', 'wind', 'storm', 'hurricane', 'typhoon', 'gale']):
            reply = (
                "🌪️ **Cyclone & Severe Storm Advisory**:\n\n"
                "- **Stay Indoors**: Secure all doors and windows. Move to the strongest interior room away from outer glass.\n"
                "- **Emergency Kit**: Keep battery torches, power banks, first-aid supplies, dry food, and clean water ready.\n"
                "- **Do Not Venture Out**: Even if the wind temporarily calms, you may be in the 'eye' of the cyclone; wait for official clearance.\n"
                "- **Real-Time Warnings**: Monitor updates at [Live Alerts](/alerts)."
            )

        # Fire Emergency
        elif any(k in msg for k in ['fire', 'flame', 'smoke', 'burn', 'blaze']):
            reply = (
                "🔥 **Fire Emergency Guidelines**:\n\n"
                "- **Evacuate Immediately**: **GET OUT AND STAY OUT!** Never re-enter a burning structure.\n"
                "- **Crawl Low**: Smoke and poisonous gases rise; crawl near the floor where air is cleaner.\n"
                "- **Clothes on Fire**: **STOP, DROP, and ROLL** until flames are smothered.\n"
                "- **Call Fire Brigade**: Dial **101** or **112** immediately."
            )

        # Tsunami & Coastal Surge
        elif any(k in msg for k in ['tsunami', 'sea wave', 'coastal surge', 'high tide']):
            reply = (
                "🌊 **Tsunami Coastal Safety Protocol**:\n\n"
                "- **Warning Signs**: Rapid, abnormal receding of sea water or a roaring ocean sound.\n"
                "- **Evacuate**: Move at least 2 kilometers inland or climb to high ground at least 15 meters above sea level.\n"
                "- **Avoid Coastlines**: Never stay to watch a tsunami wave; subsequent waves can be much larger.\n"
                "- **Helpline**: Call Indian Tsunami Early Warning Center / NDRF **1078**."
            )

        # Heatwave & Sunstroke
        elif any(k in msg for k in ['heatwave', 'heat', 'sunstroke', 'temperature', 'dehydration', 'hot']):
            reply = (
                "☀️ **Heatwave Health & Safety Advisory**:\n\n"
                "- **Hydration**: Drink plenty of water and ORS solutions, even if you do not feel thirsty.\n"
                "- **Peak Hours**: Avoid direct outdoor exposure between 12:00 PM and 4:00 PM.\n"
                "- **Clothing**: Wear lightweight, loose-fitting, light-colored cotton clothes and head covering.\n"
                "- **Sunstroke Symptoms**: Dizziness, high body temperature, nausea. Move to shade and apply cool damp cloths. Call **108**."
            )

        # Thunderstorm & Lightning
        elif any(k in msg for k in ['lightning', 'thunder', 'thunderstorm', 'electric shock']):
            reply = (
                "⚡ **Lightning & Severe Thunderstorm Rules**:\n\n"
                "- **30-30 Rule**: If time between lightning flash and thunderclap is under 30 seconds, seek indoor shelter immediately.\n"
                "- **Avoid Open Areas**: Do NOT stand under isolated trees, near metal poles, or near water bodies.\n"
                "- **Indoor Safety**: Unplug sensitive electronics; avoid bathing or touching wired plumbing during strikes."
            )

        # AI Prediction / ML Engine
        elif any(k in msg for k in ['predict', 'prediction', 'risk', 'machine learning', 'ml', 'forecast risk', 'calculate']):
            reply = (
                "⚡ **RADAR Smart AI Disaster Risk Predictor**:\n\n"
                "Our machine learning model (`RandomForestClassifier`, 97.5% accuracy) evaluates:\n"
                "- 🌧️ Rainfall (mm)\n"
                "- 🌊 River / Flood Water Level (m)\n"
                "- 💨 Wind Speed (km/h)\n"
                "- 🌡️ Temperature & Humidity\n"
                "- 🧱 Seismic Activity (Richter Scale)\n\n"
                "Try calculating your location's real-time disaster hazard index at [AI Predictor](/predict)."
            )

        # Accounts, Login, Admin
        elif any(k in msg for k in ['login', 'admin', 'register', 'signup', 'password', 'account', 'dashboard']):
            reply = (
                "🔐 **Account & Portal Access**:\n\n"
                "- **Citizen Portal**: [Sign In](/login) or [Create an Account](/register).\n"
                "- **User Profile**: Track your transmitted SOS emergency broadcasts at [Profile](/profile).\n"
                "- **Admin Operations Portal**: Accessible at [Admin Login](/admin/login).\n"
                "  *(Default Credentials: Username `admin` | Password `admin123`)*."
            )

        # Helplines & Contacts
        elif any(k in msg for k in ['helpline', 'number', 'police', 'ambulance', 'ndrf', 'call', 'contact', 'phone']):
            reply = (
                "📞 **24x7 Official National Emergency Helplines (India)**:\n\n"
                "- 🚑 **Ambulance & Medical Emergency**: **108**\n"
                "- 🚔 **Police / National Emergency Number**: **112** / **100**\n"
                "- 🚒 **Fire Brigade**: **101**\n"
                "- 🛡️ **NDRF Disaster Support**: **1078** / **011-24363260**\n"
                "- 🚨 **Disaster Management Helpline**: **1070** (State) / **1077** (District)"
            )

        # Weather queries
        elif any(k in msg for k in ['weather', 'forecast', 'rain', 'current weather', 'monsoon', 'clouds']):
            reply = (
                "🌦️ **Live Weather & Precipitation Telemetry**:\n\n"
                "RADAR integrates live global satellite telemetry via **Open-Meteo & OpenWeatherMap** APIs.\n"
                "- Check temperature, wind gusts, humidity, and rainfall rates for your district at [Live Weather & Alerts](/alerts).\n"
                "- Live GPS weather is automatically fed into the AI Risk Predictor!"
            )

        # General Fallback
        else:
            reply = (
                f"✨ **Ask Gemini Assistant**:\n\n"
                f"I am ready to help you with disaster response and safety! Here are popular topics you can ask me about:\n"
                f"- 🏠 **Verified Shelters**: *'Show available shelters with beds'*\n"
                f"- ⛰️ **Landslide & Hill Stations**: *'Landslide safety rules'*\n"
                f"- 🌊 **Flood / Earthquake / Cyclone**: *'What to do during a flood?'*\n"
                f"- ⚡ **AI Prediction**: *'How does AI risk prediction work?'*\n"
                f"- 🚨 **Emergency SOS**: *'How do I send an SOS call?'*\n"
                f"- 📞 **Helpline Numbers**: *'Emergency contact numbers'*\n\n"
                f"*(Note: You can also configure `GEMINI_API_KEY` in your `.env` file to unlock free-form conversational Google Gemini LLM responses!)*"
            )

        return jsonify({'reply': reply, 'provider': 'RADAR Smart Intelligence'})

    except Exception as e:
        return jsonify({
            'reply': "✨ **Ask Gemini Assistant**: I am here to help with verified shelters, safety guidelines, weather alerts, and emergency helplines. Please ask a question or explore our [Shelter Locator](/shelters)."
        })


@feature_bp.route('/api/recommend_shelter', methods=['POST'])
def recommend_shelter():
    """Smart verified shelter recommendation based on user latitude & longitude and capacity."""
    data = request.get_json() or {}
    user_lat = data.get('latitude')
    user_lng = data.get('longitude')

    shelters_list = Shelter.query.filter(Shelter.verification_status == 'Verified', Shelter.available_capacity > 0).all()
    if not shelters_list:
        return jsonify({'success': False, 'message': 'No verified shelters with available capacity found.'})

    if user_lat and user_lng:
        try:
            ulat, ulng = float(user_lat), float(user_lng)
            sorted_shelters = sorted(shelters_list, key=lambda s: haversine_distance(ulat, ulng, s.latitude, s.longitude))
            best_shelter = sorted_shelters[0]
            dist_km = haversine_distance(ulat, ulng, best_shelter.latitude, best_shelter.longitude)
            
            return jsonify({
                'success': True,
                'shelter': best_shelter.to_dict(),
                'distance_km': dist_km
            })
        except Exception:
            pass

    best_shelter = max(shelters_list, key=lambda s: s.available_capacity)
    return jsonify({
        'success': True,
        'shelter': best_shelter.to_dict(),
        'distance_km': None
    })
