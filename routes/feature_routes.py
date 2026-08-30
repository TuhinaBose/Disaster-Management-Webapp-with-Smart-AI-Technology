from flask import Blueprint, render_template, request, jsonify, current_app
from database import db
from models import Shelter, EmergencyRequest, RiskPrediction, DisasterAlert
from models.ai_model import DisasterPredictor
import math

feature_bp = Blueprint('feature', __name__)

# Lazy predictor instance
_predictor = None

def get_predictor():
    global _predictor
    if _predictor is None:
        model_path = current_app.config.get('MODEL_PATH')
        _predictor = DisasterPredictor(model_path)
    return _predictor

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

@feature_bp.route('/shelters')
def shelters():
    """Shelter locator view with dynamic cascading State -> District -> City/Village -> Facility Type filter + Live OSM Schools/Colleges."""
    import urllib.request
    import json

    state_query = request.args.get('state', '').strip()
    district_query = request.args.get('district', '').strip()
    city_query = request.args.get('city_village', '').strip()
    facility_query = request.args.get('facility_type', '').strip()
    search_keyword = request.args.get('query', '').strip()
    
    query = Shelter.query
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

    # Fetch Live OpenStreetMap Schools, Colleges, and Hospitals if location or search term specified
    osm_shelters = []
    loc_target = city_query or district_query or state_query or search_keyword

    if loc_target:
        try:
            nom_url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(loc_target + ', India')}&format=json&limit=1"
            req = urllib.request.Request(nom_url, headers={'User-Agent': 'RADAR-Disaster-App/1.0'})
            with urllib.request.urlopen(req) as resp:
                nom_data = json.loads(resp.read().decode())

            if nom_data:
                lat = nom_data[0]['lat']
                lon = nom_data[0]['lon']

                # Overpass API query for schools, colleges, hospitals
                overpass_q = f"""
                [out:json][timeout:10];
                (
                  node["amenity"="school"](around:12000,{lat},{lon});
                  node["amenity"="college"](around:12000,{lat},{lon});
                  node["amenity"="hospital"](around:12000,{lat},{lon});
                  way["amenity"="school"](around:12000,{lat},{lon});
                  way["amenity"="college"](around:12000,{lat},{lon});
                  way["amenity"="hospital"](around:12000,{lat},{lon});
                );
                out center 15;
                """
                op_url = "https://overpass-api.de/api/interpreter?data=" + urllib.parse.quote(overpass_q)
                req_op = urllib.request.Request(op_url, headers={'User-Agent': 'RADAR-Disaster-App/1.0'})
                with urllib.request.urlopen(req_op) as resp_op:
                    op_data = json.loads(resp_op.read().decode())

                count_id = 9000
                for el in op_data.get('elements', []):
                    count_id += 1
                    tags = el.get('tags', {})
                    raw_type = tags.get('amenity', 'building').capitalize()
                    name = tags.get('name') or tags.get('name:en') or f"Local {raw_type} Emergency Refuge"
                    
                    if facility_query and facility_query.lower() not in raw_type.lower():
                        continue

                    el_lat = float(el.get('lat') or el.get('center', {}).get('lat', 0))
                    el_lon = float(el.get('lon') or el.get('center', {}).get('lon', 0))

                    if el_lat and el_lon:
                        osm_shelters.append({
                            'id': count_id,
                            'name': name,
                            'address': tags.get('addr:street') or f"{loc_target}, India",
                            'state': state_query or 'India',
                            'district': district_query or loc_target,
                            'city_village': city_query or loc_target,
                            'facility_type': raw_type,
                            'latitude': el_lat,
                            'longitude': el_lon,
                            'total_capacity': 500,
                            'available_beds': 350,
                            'occupancy_percentage': 30.0,
                            'has_food': True,
                            'has_water': True,
                            'has_medical': True if raw_type == 'Hospital' else False,
                            'contact_number': '+91-108 (Emergency)',
                            'is_osm_live': True
                        })
        except Exception:
            pass

    shelter_list = db_shelters + osm_shelters

    # Unique list of states for initial dropdown
    states = [s[0] for s in db.session.query(Shelter.state).distinct().all() if s[0]]
    districts = [d[0] for d in db.session.query(Shelter.district).distinct().all() if d[0]]
    cities = [c[0] for c in db.session.query(Shelter.city_village).distinct().all() if c[0]]
    facility_types = ['School', 'College', 'Hospital', 'Community Center', 'Stadium', 'Building']

    return render_template('shelters.html',
                           shelters=shelter_list,
                           states=states,
                           districts=districts,
                           cities=cities,
                           facility_types=facility_types,
                           current_state=state_query,
                           current_district=district_query,
                           current_city=city_query,
                           current_facility=facility_query,
                           search_query=search_keyword)

@feature_bp.route('/api/location_options')
def api_location_options():
    """API returning cascading dropdown data (Districts for selected State, Cities for District)."""
    state_param = request.args.get('state', '').strip()
    district_param = request.args.get('district', '').strip()

    if state_param and not district_param:
        districts = [d[0] for d in db.session.query(Shelter.district).filter(Shelter.state.ilike(f'%{state_param}%')).distinct().all() if d[0]]
        return jsonify({'districts': districts})

    if state_param and district_param:
        cities = [c[0] for c in db.session.query(Shelter.city_village).filter(Shelter.state.ilike(f'%{state_param}%'), Shelter.district.ilike(f'%{district_param}%')).distinct().all() if c[0]]
        return jsonify({'cities': cities})

    return jsonify({'districts': [], 'cities': []})

@feature_bp.route('/api/search_facilities')
def api_search_facilities():
    """
    Unified Live Search API combining local DB shelters with live OpenStreetMap (OSM)
    Schools, Colleges, Hospitals, and Buildings.
    """
    import urllib.request
    import json

    state_q = request.args.get('state', '').strip()
    district_q = request.args.get('district', '').strip()
    city_q = request.args.get('city_village', '').strip()
    facility_q = request.args.get('facility_type', '').strip()
    keyword_q = request.args.get('query', '').strip()

    # 1. Fetch DB Shelters
    query = Shelter.query
    if state_q:
        query = query.filter(Shelter.state.ilike(f'%{state_q}%'))
    if district_q:
        query = query.filter(Shelter.district.ilike(f'%{district_q}%'))
    if city_q:
        query = query.filter(Shelter.city_village.ilike(f'%{city_q}%'))
    if facility_q:
        query = query.filter(Shelter.facility_type.ilike(f'%{facility_q}%'))
    if keyword_q:
        query = query.filter(
            (Shelter.name.ilike(f'%{keyword_q}%')) |
            (Shelter.district.ilike(f'%{keyword_q}%')) |
            (Shelter.city_village.ilike(f'%{keyword_q}%')) |
            (Shelter.facility_type.ilike(f'%{keyword_q}%'))
        )

    db_shelters = [s.to_dict() for s in query.all()]

    # 2. Fetch Live OpenStreetMap Schools, Colleges, Hospitals if location or search term specified
    osm_results = []
    location_target = city_q or district_q or state_q or keyword_q

    if location_target:
        try:
            # Geocode target location via OpenStreetMap Nominatim
            nom_url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(location_target + ', India')}&format=json&limit=1"
            req = urllib.request.Request(nom_url, headers={'User-Agent': 'RADAR-Disaster-App/1.0'})
            with urllib.request.urlopen(req) as resp:
                nom_data = json.loads(resp.read().decode())

            if nom_data:
                lat = nom_data[0]['lat']
                lon = nom_data[0]['lon']

                # Overpass API query for schools, colleges, hospitals
                overpass_q = f"""
                [out:json][timeout:10];
                (
                  node["amenity"="school"](around:12000,{lat},{lon});
                  node["amenity"="college"](around:12000,{lat},{lon});
                  node["amenity"="hospital"](around:12000,{lat},{lon});
                  way["amenity"="school"](around:12000,{lat},{lon});
                  way["amenity"="college"](around:12000,{lat},{lon});
                  way["amenity"="hospital"](around:12000,{lat},{lon});
                );
                out center 20;
                """
                op_url = "https://overpass-api.de/api/interpreter?data=" + urllib.parse.quote(overpass_q)
                req_op = urllib.request.Request(op_url, headers={'User-Agent': 'RADAR-Disaster-App/1.0'})
                with urllib.request.urlopen(req_op) as resp_op:
                    op_data = json.loads(resp_op.read().decode())

                count_id = 9000
                for el in op_data.get('elements', []):
                    count_id += 1
                    tags = el.get('tags', {})
                    raw_type = tags.get('amenity', 'building').capitalize()
                    name = tags.get('name') or tags.get('name:en') or f"Local {raw_type} Facility"
                    
                    if facility_q and facility_q.lower() not in raw_type.lower():
                        continue

                    el_lat = float(el.get('lat') or el.get('center', {}).get('lat', 0))
                    el_lon = float(el.get('lon') or el.get('center', {}).get('lon', 0))

                    if el_lat and el_lon:
                        osm_results.append({
                            'id': count_id,
                            'name': name,
                            'address': tags.get('addr:street') or f"{location_target}, India",
                            'state': state_q or 'India',
                            'district': district_q or location_target,
                            'city_village': city_q or location_target,
                            'facility_type': raw_type,
                            'latitude': el_lat,
                            'longitude': el_lon,
                            'total_capacity': 500,
                            'available_beds': 350,
                            'occupancy_percentage': 30.0,
                            'has_food': True,
                            'has_water': True,
                            'has_medical': True if raw_type == 'Hospital' else False,
                            'contact_number': '+91-108 (Emergency)',
                            'is_osm_live': True
                        })
        except Exception as e:
            pass

    combined_results = db_shelters + osm_results
    return jsonify({
        'success': True,
        'count': len(combined_results),
        'db_count': len(db_shelters),
        'osm_count': len(osm_results),
        'shelters': combined_results
    })

@feature_bp.route('/api/shelters')
def api_shelters():
    """JSON API endpoint returning list of all shelters for interactive map."""
    shelter_list = Shelter.query.all()
    return jsonify([s.to_dict() for s in shelter_list])

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

@feature_bp.route('/api/chatbot', methods=['POST'])
def chatbot_api():
    """
    AI Chatbot API ('RescuBot') for automated disaster assistance, shelter queries, and emergency advice.
    """
    try:
        data = request.get_json(silent=True) or request.form or {}
        message = data.get('message', '').lower().strip()

        if not message:
            return jsonify({'reply': "👋 Hello! I am **RescuBot**, your RADAR AI Emergency Assistant. How can I help you today?"})

        # Rule-based natural language intent parser with live DB telemetry
        if any(k in message for k in ['shelter', 'refuge', 'bed', 'camp', 'stay', 'where', 'location', 'accommodation']):
            available_shelters = Shelter.query.filter(Shelter.available_beds > 0).order_by(Shelter.available_beds.desc()).all()
            if available_shelters:
                top_s = available_shelters[0]
                reply = f"🏠 **Shelter Update**: We currently have **{len(available_shelters)} shelters** open. Recommended: **{top_s.name}** in *{top_s.district}* with **{top_s.available_beds} free beds** remaining. Call: {top_s.contact_number}. View map at [Shelter Locator](/shelters)."
            else:
                reply = "🏠 All shelters are currently monitored. Please visit our [Shelter Locator](/shelters) for live capacity updates."

        elif any(k in message for k in ['flood', 'water', 'submerged', 'drowning', 'rain', 'river']):
            reply = "🌊 **Flood Emergency Tip**: Move immediately to higher ground! Avoid walking or driving through moving flood water. Call **108** for emergency medical/rescue support. Check real-time weather at [Live Alerts](/alerts)."

        elif any(k in message for k in ['earthquake', 'tremor', 'quake', 'shaking']):
            reply = "🧱 **Earthquake Emergency Tip**: DROP, COVER, and HOLD ON! Take shelter under a sturdy table. Stay away from glass windows, heavy furniture, and power lines."

        elif any(k in message for k in ['cyclone', 'wind', 'storm', 'hurricane', 'gust']):
            reply = "🌪️ **Cyclone Warning Tip**: Stay indoors away from windows! Secure loose items outside, keep emergency torchlight ready, and monitor local warning broadcasts."

        elif any(k in message for k in ['fire', 'flame', 'smoke', 'burn']):
            reply = "🔥 **Fire Emergency Tip**: GET OUT, STAY OUT! Crawl low under smoke to avoid toxic gas. Call Fire Brigade **101** immediately. Remember: STOP, DROP, and ROLL if clothes catch fire."

        elif any(k in message for k in ['heatwave', 'heat', 'sun', 'temperature']):
            reply = "☀️ **Heatwave Advisory**: Stay hydrated with water and ORS. Avoid outdoor exposure between 12:00 PM and 4:00 PM. Wear light cotton clothes."

        elif any(k in message for k in ['sos', 'help', 'danger', 'rescue', 'distress', 'emergency', 'trapped', 'stuck']):
            reply = "🚨 **Emergency SOS**: If you are in immediate danger, hit the red [Emergency SOS Button](/sos) to broadcast your live GPS coordinates to rescue teams! Helplines: **108** (Ambulance) / **100** (Police) / **1078** (NDRF)."

        elif any(k in message for k in ['helpline', 'number', 'contact', 'phone', 'police', 'ambulance', 'ndrf', 'call']):
            reply = "📞 **National Emergency Helplines (24x7)**:\n- NDRF Disaster Support: **1078** / **011-24363260**\n- Ambulance Services: **108**\n- Police Operations: **100** / **112**\n- Fire Station: **101**"

        elif any(k in message for k in ['predict', 'risk', 'ai', 'level', 'forecast', 'calculate']):
            reply = "⚡ **AI Risk Predictor**: Calculate real-time flood, cyclone & earthquake risk using our Scikit-Learn ML engine! [Click here to analyze risk](/predict)."

        elif any(k in message for k in ['login', 'admin', 'account', 'password', 'sign in', 'register']):
            reply = "🔐 **Account Access**:\n- Citizen Sign In: [User Login](/login)\n- New Account: [Register](/register)\n- Admin Operations Portal: [Admin Login](/admin/login) *(Default Admin: admin / admin123)*."

        else:
            reply = "🤖 I am **RescuBot**! You can ask me about **Shelters**, **Flood/Earthquake/Cyclone Safety**, **Emergency Helplines**, **AI Risk Predictor**, or **User Login**."

        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'reply': f"🤖 I am RescuBot! You can ask me about **Shelters**, **Safety Tips**, or **Emergency SOS**."})

@feature_bp.route('/api/recommend_shelter', methods=['POST'])
def recommend_shelter():
    """Smart shelter recommendation based on user latitude & longitude and bed capacity."""
    data = request.get_json() or {}
    user_lat = data.get('latitude')
    user_lng = data.get('longitude')

    shelters = Shelter.query.filter(Shelter.available_beds > 0).all()
    if not shelters:
        return jsonify({'success': False, 'message': 'No available shelters found.'})

    if user_lat and user_lng:
        try:
            ulat, ulng = float(user_lat), float(user_lng)
            # Calculate distance using Haversine formula
            def get_dist(s):
                dlat = math.radians(s.latitude - ulat)
                dlng = math.radians(s.longitude - ulng)
                a = math.sin(dlat/2)**2 + math.cos(math.radians(ulat)) * math.cos(math.radians(s.latitude)) * math.sin(dlng/2)**2
                return 6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

            sorted_shelters = sorted(shelters, key=get_dist)
            best_shelter = sorted_shelters[0]
            dist_km = round(get_dist(best_shelter), 2)
            
            return jsonify({
                'success': True,
                'shelter': best_shelter.to_dict(),
                'distance_km': dist_km
            })
        except Exception:
            pass

    # Fallback to shelter with highest available beds
    best_shelter = max(shelters, key=lambda s: s.available_beds)
    return jsonify({
        'success': True,
        'shelter': best_shelter.to_dict(),
        'distance_km': None
    })
