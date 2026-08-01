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

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password) and user.role == 'admin':
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash('Successfully logged in as Admin.', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid admin credentials. Please try again.', 'danger')

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
            name = request.form.get('name')
            address = request.form.get('address')
            district = request.form.get('district')
            lat = float(request.form.get('latitude', 0))
            lng = float(request.form.get('longitude', 0))
            capacity = int(request.form.get('total_capacity', 0))
            beds = int(request.form.get('available_beds', 0))
            food = 'has_food' in request.form
            water = 'has_water' in request.form
            medical = 'has_medical' in request.form
            contact = request.form.get('contact_number')

            new_shelter = Shelter(
                name=name, address=address, district=district,
                latitude=lat, longitude=lng, total_capacity=capacity,
                available_beds=beds, has_food=food, has_water=water,
                has_medical=medical, contact_number=contact
            )
            db.session.add(new_shelter)
            db.session.commit()
            flash('New shelter added successfully!', 'success')
        except Exception as e:
            flash(f'Error adding shelter: {str(e)}', 'danger')
        return redirect(url_for('admin.manage_shelters'))

    all_shelters = Shelter.query.order_by(Shelter.created_at.desc()).all()
    return render_template('admin/shelters_mgmt.html', shelters=all_shelters)

@admin_bp.route('/shelter/edit/<int:shelter_id>', methods=['POST'])
def edit_shelter(shelter_id):
    """Update shelter available beds & total capacity."""
    if not is_admin_logged_in():
        return redirect(url_for('admin.login'))

    shelter = Shelter.query.get_or_404(shelter_id)
    try:
        shelter.name = request.form.get('name', shelter.name)
        shelter.total_capacity = int(request.form.get('total_capacity', shelter.total_capacity))
        shelter.available_beds = int(request.form.get('available_beds', shelter.available_beds))
        shelter.contact_number = request.form.get('contact_number', shelter.contact_number)
        shelter.has_food = 'has_food' in request.form
        shelter.has_water = 'has_water' in request.form
        shelter.has_medical = 'has_medical' in request.form

        db.session.commit()
        flash(f'Shelter "{shelter.name}" updated successfully.', 'success')
    except Exception as e:
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
