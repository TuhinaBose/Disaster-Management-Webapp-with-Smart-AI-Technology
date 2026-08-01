from flask import Blueprint, render_template
from models import DisasterAlert, Shelter, EmergencyRequest

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home Page with hero banner, live awareness ticker, quick tiles, and live stats."""
    active_alerts = DisasterAlert.query.filter_by(is_active=True).order_by(DisasterAlert.created_at.desc()).all()
    recent_alerts = active_alerts[:3]
    total_shelters = Shelter.query.count()
    
    shelters = Shelter.query.all()
    available_beds = sum(s.available_beds for s in shelters) if shelters else 0
    total_capacity = sum(s.total_capacity for s in shelters) if shelters else 0
    
    pending_sos = EmergencyRequest.query.filter_by(status='Pending').count()

    return render_template('index.html',
                           active_alerts=active_alerts,
                           recent_alerts=recent_alerts,
                           total_shelters=total_shelters,
                           available_beds=available_beds,
                           total_capacity=total_capacity,
                           pending_sos=pending_sos)

@main_bp.route('/safety')
def safety():
    """Safety guidelines page for Flood, Earthquake, Cyclone, Fire, and Heatwave."""
    return render_template('safety.html')

@main_bp.route('/alerts')
def alerts():
    """Live weather and disaster alerts portal."""
    all_alerts = DisasterAlert.query.order_by(DisasterAlert.created_at.desc()).all()
    return render_template('alerts.html', alerts=all_alerts)
