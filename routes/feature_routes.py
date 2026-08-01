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
    """Shelter locator view with district search and filter support."""
    district_query = request.args.get('district', '').strip()
    
    if district_query:
        shelter_list = Shelter.query.filter(Shelter.district.ilike(f'%{district_query}%')).all()
    else:
        shelter_list = Shelter.query.all()

    # Unique list of districts for filter dropdown
    districts = db.session.query(Shelter.district).distinct().all()
    districts = [d[0] for d in districts]

    return render_template('shelters.html', shelters=shelter_list, districts=districts, current_district=district_query)

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
    data = request.get_json() or {}
    message = data.get('message', '').lower().strip()

    if not message:
        return jsonify({'reply': "Hello! I am **RescuBot**, your AI Emergency Assistant. How can I help you today?"})

    # Rule-based natural language intent parser for quick, helpful emergency response
    if any(k in message for k in ['shelter', 'refuge', 'bed', 'camp', 'stay']):
        available_shelters = Shelter.query.filter(Shelter.available_beds > 0).all()
        if available_shelters:
            top_s = available_shelters[0]
            reply = f"🏠 **Shelter Update**: We currently have **{len(available_shelters)} shelters** open. Recommended: **{top_s.name}** in *{top_s.district}* with **{top_s.available_beds} beds** remaining. Call: {top_s.contact_number}."
        else:
            reply = "🏠 All shelters are currently monitored. Please visit our [Shelter Locator](/shelters) for live capacity updates."

    elif any(k in message for k in ['flood', 'water', 'submerged', 'drowning']):
        reply = "🌊 **Flood Emergency Tip**: Move immediately to higher ground! Avoid walking or driving through moving water. Call **108** for emergency medical/rescue support."

    elif any(k in message for k in ['earthquake', 'tremor', 'quake', 'shaking']):
        reply = "🧱 **Earthquake Emergency Tip**: DROP, COVER, and HOLD ON! Take shelter under a sturdy table. Stay away from glass windows and power lines."

    elif any(k in message for k in ['sos', 'help', 'danger', 'rescue', 'distress', 'emergency']):
        reply = "🚨 **Emergency SOS**: If you are in immediate danger, please hit the red [Emergency SOS Button](/sos) to send your GPS coordinates to our rescue operations room! Helpline: **108** (Ambulance) / **100** (Police) / **1078** (NDRF)."

    elif any(k in message for k in ['helpline', 'number', 'contact', 'phone', 'police']):
        reply = "📞 **Emergency Numbers**:\n- NDRF Disaster Support: **1078** / **011-24363260**\n- Ambulance Services: **108**\n- Police Operations: **100**\n- Fire Station: **101**\n- National Emergency Number: **112**"

    elif any(k in message for k in ['predict', 'risk', 'ai', 'level', 'forecast']):
        reply = "⚡ **AI Risk Predictor**: You can calculate real-time flood & cyclone risk using our AI ML tool! [Click here to analyze risk](/predict)."

    else:
        reply = "🤖 I am here to assist with disaster response! You can ask me about **Shelters**, **Flood/Earthquake Safety**, **Helpline Numbers**, or **Emergency SOS**."

    return jsonify({'reply': reply})

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
