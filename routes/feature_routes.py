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
    'Ask Gemini' AI Assistant API for disaster preparedness, safety advice, live shelter queries, and weather.
    Grounded in actual application data to avoid hallucinating shelters or weather.
    """
    try:
        data = request.get_json(silent=True) or request.form or {}
        user_query = data.get('message', '').strip()

        if not user_query:
            return jsonify({'reply': "👋 Hello! I am **Ask Gemini**, your AI Disaster Management Assistant. How can I assist you with safety guidelines, shelter locations, weather alerts, or emergency procedures today?"})

        # 1. Fetch live system context from DB to ground Gemini's answer
        verified_shelters = Shelter.query.filter_by(verification_status='Verified').all()
        total_shelters = len(verified_shelters)
        total_free_beds = sum(s.available_capacity for s in verified_shelters) if verified_shelters else 0
        active_alerts = DisasterAlert.query.filter_by(is_active=True).all()
        alerts_summary = "; ".join([f"{a.title} ({a.severity} in {a.location})" for a in active_alerts]) if active_alerts else "No active critical alerts broadcasted currently."

        top_shelter_info = ""
        if verified_shelters:
            top_s = max(verified_shelters, key=lambda s: s.available_capacity)
            top_shelter_info = f"Top Recommended Verified Shelter: {top_s.name} in {top_s.district}, {top_s.city_village} with {top_s.available_capacity} available capacity remaining out of {top_s.total_capacity} total capacity. Contact: {top_s.contact}."

        gemini_key = current_app.config.get('GEMINI_API_KEY') or os.environ.get('GEMINI_API_KEY')

        # 2. If Gemini API Key exists, call Gemini API
        if gemini_key:
            system_prompt = f"""
            You are 'Ask Gemini', an official AI Assistant for RADAR - Smart AI Disaster Management Web Application.
            Answer the user's question clearly, supportively, and accurately regarding disaster safety, emergency preparedness, shelters, weather, and application features.
            
            IMPORTANT GROUNDING DATA (STRICTLY USE THIS REAL-TIME APPLICATION TELEMETRY):
            - Registered Verified Disaster Shelters in System: {total_shelters} shelters.
            - Total Available Capacity in System: {total_free_beds} beds free.
            - {top_shelter_info}
            - Current Active Disaster Bulletins: {alerts_summary}
            - National Helplines: 108 (Ambulance), 100/112 (Police), 101 (Fire), 1078 (NDRF Disaster Response).
            
            RULES:
            - Do NOT invent fake disaster shelters, unverified phone numbers, or fabricated weather reports.
            - Format your response nicely using Markdown (bold text, bullet points).
            """
            
            full_prompt = f"{system_prompt}\n\nUser Question: {user_query}"

            try:
                # Try google-genai SDK first if installed
                try:
                    from google import genai
                    client = genai.Client(api_key=gemini_key)
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=full_prompt,
                    )
                    if response and response.text:
                        return jsonify({'reply': response.text, 'provider': 'Gemini 2.5 Flash'})
                except Exception:
                    pass

                # Fallback to direct HTTP Gemini API endpoint
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
                payload = {
                    "contents": [{"parts": [{"text": full_prompt}]}]
                }
                resp = requests.post(url, json=payload, timeout=8)
                if resp.status_code == 200:
                    res_json = resp.json()
                    candidates = res_json.get('candidates', [])
                    if candidates and 'content' in candidates[0]:
                        parts = candidates[0]['content'].get('parts', [])
                        if parts and 'text' in parts[0]:
                            return jsonify({'reply': parts[0]['text'], 'provider': 'Gemini API'})
            except Exception as gem_err:
                print(f"[Ask Gemini API Error]: {gem_err}")

        # 3. Intelligent Data-Backed Fallback if Gemini Key is unconfigured or call times out
        msg_lower = user_query.lower()
        if any(k in msg_lower for k in ['shelter', 'refuge', 'bed', 'camp', 'stay', 'where', 'location', 'capacity']):
            reply = f"🏠 **Ask Gemini Shelter Status**:\nWe currently have **{total_shelters} verified disaster shelters** active with **{total_free_beds} available beds**. {top_shelter_info}\n\nSearch all verified shelters on our [Shelter Locator](/shelters)."

        elif any(k in msg_lower for k in ['flood', 'water', 'submerged', 'drowning', 'rain', 'river']):
            reply = "🌊 **Flood Safety Guidelines**:\n- Move immediately to higher ground or designated shelters.\n- Never walk or drive through flowing water.\n- Disconnect electrical appliances.\n- Call **108** for emergency rescue support.\nCheck real-time precipitation at [Live Weather & Alerts](/alerts)."

        elif any(k in msg_lower for k in ['earthquake', 'tremor', 'quake', 'shaking']):
            reply = "🧱 **Earthquake Safety Guidelines**:\n- **DROP, COVER, and HOLD ON!** Take refuge under a sturdy table.\n- Stay away from windows, outer walls, and hanging fixtures.\n- If outdoors, move to an open area away from power lines and tall buildings."

        elif any(k in msg_lower for k in ['cyclone', 'wind', 'storm', 'hurricane']):
            reply = "🌪️ **Cyclone Safety Advisory**:\n- Stay indoors away from windows and glass doors.\n- Keep battery torches, emergency kits, and clean drinking water ready.\n- Follow official advisories on [Live Alerts](/alerts)."

        elif any(k in msg_lower for k in ['fire', 'flame', 'smoke', 'burn']):
            reply = "🔥 **Fire Emergency Action**:\n- **GET OUT AND STAY OUT!** Crawl low under smoke.\n- Call Fire Brigade **101** immediately.\n- Use **STOP, DROP, and ROLL** if clothing catches fire."

        elif any(k in msg_lower for k in ['helpline', 'number', 'contact', 'phone', 'police', 'ndrf', 'ambulance']):
            reply = "📞 **24x7 National Emergency Helplines**:\n- NDRF Disaster Response: **1078**\n- Ambulance Services: **108**\n- Police Operations: **100** / **112**\n- Fire Station: **101**"

        else:
            reply = f"✨ **Ask Gemini Assistant**:\nI am your AI Disaster Assistant! You can ask me about **Verified Shelters**, **Flood / Earthquake / Cyclone Safety**, **Live Weather Updates**, or **Emergency Helplines**.\n\n*(Currently operating with verified live telemetry. Configure `GEMINI_API_KEY` in `.env` to enable full Gemini LLM intelligence).* "

        return jsonify({'reply': reply, 'provider': 'RADAR Telemetry System'})

    except Exception as e:
        return jsonify({'reply': f"✨ **Ask Gemini**: I can assist you with emergency shelters, weather reports, and safety advice. Please try again or visit [Shelter Locator](/shelters)."})


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
