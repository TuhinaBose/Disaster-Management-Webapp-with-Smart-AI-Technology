from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from database import db
from models import User, Shelter, DisasterAlert, EmergencyRequest, RiskPrediction

admin_bp = Blueprint('admin', __name__)

def is_admin_logged_in():
    """Helper to check if active session belongs to an admin."""
    return session.get('user_id') and session.get('role') == 'admin'

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin Login Page."""
    if is_admin_logged_in():
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        user = User.query.filter((User.username == username) | (User.email == username)).first()
        if user and user.check_password(password) and user.role == 'admin':
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash('Successfully logged in as Admin.', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid admin credentials. Default credentials: admin / admin123', 'danger')

    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    """Logs out admin user."""
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('admin.login'))

@admin_bp.route('/dashboard')
def dashboard():
    """Central Admin Control Dashboard."""
    if not is_admin_logged_in():
        return redirect(url_for('admin.login'))

    total_shelters = Shelter.query.count()
    active_alerts = DisasterAlert.query.filter_by(is_active=True).count()
    pending_sos = EmergencyRequest.query.filter_by(status='Pending').count()
    total_users = User.query.count()

    recent_requests = EmergencyRequest.query.order_by(EmergencyRequest.created_at.desc()).limit(5).all()
    recent_predictions = RiskPrediction.query.order_by(RiskPrediction.created_at.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
                           total_shelters=total_shelters,
                           active_alerts=active_alerts,
                           pending_sos=pending_sos,
                           total_users=total_users,
                           recent_requests=recent_requests,
                           recent_predictions=recent_predictions)

# ================= SHELTER MANAGEMENT =================

@admin_bp.route('/shelters', methods=['GET', 'POST'])
def manage_shelters():
    """Manage Emergency Shelters (View & Add)."""
    if not is_admin_logged_in():
        return redirect(url_for('admin.login'))

    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            address = request.form.get('address', '').strip()
            state = request.form.get('state', 'Delhi NCR').strip()
            district = request.form.get('district', '').strip()
            city_village = request.form.get('city_village', 'Central City').strip()
            facility_type = request.form.get('facility_type', 'Shelter').strip()
            lat = float(request.form.get('latitude', 0))
            lng = float(request.form.get('longitude', 0))
            capacity = int(request.form.get('total_capacity', 0))
            
            # Form may provide either current_occupancy directly or available_beds
            if 'current_occupancy' in request.form:
                occupancy = int(request.form.get('current_occupancy', 0))
            elif 'available_beds' in request.form:
                beds = int(request.form.get('available_beds', capacity))
                occupancy = capacity - beds
            else:
                occupancy = 0

            if occupancy < 0 or occupancy > capacity:
                flash(f'Occupancy ({occupancy}) cannot be negative or exceed total capacity ({capacity}).', 'danger')
                return redirect(url_for('admin.manage_shelters'))

            contact = request.form.get('contact_number') or request.form.get('contact') or '+91-108'
            verification_status = request.form.get('verification_status', 'Verified')
            food = 'has_food' in request.form
            water = 'has_water' in request.form
            medical = 'has_medical' in request.form

            new_shelter = Shelter(
                name=name, address=address, state=state, district=district,
                city_village=city_village, facility_type=facility_type,
                latitude=lat, longitude=lng, total_capacity=capacity,
                current_occupancy=occupancy, available_capacity=capacity - occupancy,
                contact=contact, verification_status=verification_status,
                has_food=food, has_water=water, has_medical=medical
            )
            new_shelter.recalculate_capacity()

            db.session.add(new_shelter)
            db.session.commit()
            flash('New verified shelter added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding shelter: {str(e)}', 'danger')
        return redirect(url_for('admin.manage_shelters'))

    all_shelters = Shelter.query.order_by(Shelter.created_at.desc()).all()
    return render_template('admin/shelters_mgmt.html', shelters=all_shelters)

@admin_bp.route('/shelter/edit/<int:shelter_id>', methods=['POST'])
def edit_shelter(shelter_id):
    """Update shelter details, state, city/village, facility type & capacity/occupancy."""
    if not is_admin_logged_in():
        return redirect(url_for('admin.login'))

    shelter = Shelter.query.get_or_404(shelter_id)
    try:
        shelter.name = request.form.get('name', shelter.name).strip()
        shelter.state = request.form.get('state', shelter.state).strip()
        shelter.district = request.form.get('district', shelter.district).strip()
        shelter.city_village = request.form.get('city_village', shelter.city_village).strip()
        shelter.facility_type = request.form.get('facility_type', shelter.facility_type).strip()
        shelter.total_capacity = int(request.form.get('total_capacity', shelter.total_capacity))
        
        if 'current_occupancy' in request.form:
            shelter.current_occupancy = int(request.form.get('current_occupancy', shelter.current_occupancy))
        elif 'available_beds' in request.form:
            beds = int(request.form.get('available_beds', shelter.available_capacity))
            shelter.current_occupancy = shelter.total_capacity - beds

        if shelter.current_occupancy < 0 or shelter.current_occupancy > shelter.total_capacity:
            flash(f'Occupancy ({shelter.current_occupancy}) cannot be negative or exceed total capacity ({shelter.total_capacity}).', 'danger')
            return redirect(url_for('admin.manage_shelters'))

        shelter.recalculate_capacity()
        shelter.contact = request.form.get('contact_number', shelter.contact).strip()
        shelter.verification_status = request.form.get('verification_status', shelter.verification_status).strip()
        shelter.has_food = 'has_food' in request.form
        shelter.has_water = 'has_water' in request.form
        shelter.has_medical = 'has_medical' in request.form

        db.session.commit()
        flash(f'Shelter "{shelter.name}" updated successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Update failed: {str(e)}', 'danger')

    return redirect(url_for('admin.manage_shelters'))

@admin_bp.route('/shelter/delete/<int:shelter_id>', methods=['POST'])
def delete_shelter(shelter_id):
    """Delete a shelter record."""
    if not is_admin_logged_in():
        return redirect(url_for('admin.login'))

    shelter = Shelter.query.get_or_404(shelter_id)
    db.session.delete(shelter)
    db.session.commit()
    flash('Shelter removed successfully.', 'info')
    return redirect(url_for('admin.manage_shelters'))

# ================= ALERT MANAGEMENT =================

@admin_bp.route('/alerts', methods=['GET', 'POST'])
def manage_alerts():
    """Manage Disaster Alerts & Warnings."""
    if not is_admin_logged_in():
        return redirect(url_for('admin.login'))

    if request.method == 'POST':
        try:
            title = request.form.get('title')
            disaster_type = request.form.get('disaster_type')
            severity = request.form.get('severity')
            location = request.form.get('location')
            description = request.form.get('description')

            new_alert = DisasterAlert(
                title=title, disaster_type=disaster_type,
                severity=severity, location=location,
                description=description, is_active=True
            )
            db.session.add(new_alert)
            db.session.commit()
            flash('Disaster alert published & broadcasted successfully!', 'success')
        except Exception as e:
            flash(f'Error creating alert: {str(e)}', 'danger')
        return redirect(url_for('admin.manage_alerts'))

    all_alerts = DisasterAlert.query.order_by(DisasterAlert.created_at.desc()).all()
    return render_template('admin/alerts_mgmt.html', alerts=all_alerts)

@admin_bp.route('/alert/toggle/<int:alert_id>', methods=['POST'])
def toggle_alert(alert_id):
    """Toggle active/inactive status of a disaster alert."""
    if not is_admin_logged_in():
        return redirect(url_for('admin.login'))

    alert = DisasterAlert.query.get_or_404(alert_id)
    alert.is_active = not alert.is_active
    db.session.commit()
    flash(f'Alert status updated to {"Active" if alert.is_active else "Inactive"}.', 'info')
    return redirect(url_for('admin.manage_alerts'))

@admin_bp.route('/alert/delete/<int:alert_id>', methods=['POST'])
def delete_alert(alert_id):
    """Delete a disaster alert."""
    if not is_admin_logged_in():
        return redirect(url_for('admin.login'))

    alert = DisasterAlert.query.get_or_404(alert_id)
    db.session.delete(alert)
    db.session.commit()
    flash('Alert deleted.', 'info')
    return redirect(url_for('admin.manage_alerts'))

# ================= EMERGENCY SOS MANAGEMENT =================

@admin_bp.route('/sos', methods=['GET', 'POST'])
def manage_sos():
    """View and update status of emergency SOS requests."""
    if not is_admin_logged_in():
        return redirect(url_for('admin.login'))

    all_requests = EmergencyRequest.query.order_by(EmergencyRequest.created_at.desc()).all()
    return render_template('admin/sos_mgmt.html', requests=all_requests)

@admin_bp.route('/sos/status/<int:req_id>', methods=['POST'])
def update_sos_status(req_id):
    """Update SOS request status (Pending -> In Progress -> Resolved)."""
    if not is_admin_logged_in():
        return redirect(url_for('admin.login'))

    req_item = EmergencyRequest.query.get_or_404(req_id)
    new_status = request.form.get('status')
    if new_status in ['Pending', 'In Progress', 'Resolved']:
        req_item.status = new_status
        db.session.commit()
        flash(f'Emergency Request #{req_id} status changed to "{new_status}".', 'success')

    return redirect(url_for('admin.manage_sos'))
