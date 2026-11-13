from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database import db
from models import User, DisasterAlert, Shelter, EmergencyRequest, RiskPrediction

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home Page with hero banner, live awareness ticker, quick tiles, and live stats."""
    active_alerts = DisasterAlert.query.filter_by(is_active=True).order_by(DisasterAlert.created_at.desc()).all()
    recent_alerts = active_alerts[:3]
    
    verified_shelters = Shelter.query.filter_by(verification_status='Verified').all()
    total_shelters = len(verified_shelters)
    available_beds = sum(s.available_capacity for s in verified_shelters) if verified_shelters else 0
    total_capacity = sum(s.total_capacity for s in verified_shelters) if verified_shelters else 0
    
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

# ================= USER AUTHENTICATION & REGISTRATION =================

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User Registration Route."""
    if session.get('user_id'):
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_pass = request.form.get('confirm_password', '').strip()

        if password != confirm_pass:
            flash('Passwords do not match. Please try again.', 'danger')
            return render_template('register.html')

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or Email already registered. Please login.', 'warning')
            return redirect(url_for('main.login'))

        new_user = User(username=username, email=email, role='user')
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        # Log user in
        session['user_id'] = new_user.id
        session['username'] = new_user.username
        session['role'] = new_user.role
        flash(f'Welcome to Smart Disaster Management System, {new_user.username}! Your account has been created.', 'success')
        return redirect(url_for('main.index'))

    return render_template('register.html')

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User & General Account Login Route."""
    if session.get('user_id'):
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        user = User.query.filter((User.username == username) | (User.email == username)).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash(f'Welcome back, {user.username}!', 'success')
            
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('main.profile'))
        else:
            flash('Invalid username or password. Please try again or create a new account.', 'danger')

    return render_template('login.html')

@main_bp.route('/logout')
def logout():
    """User logout route."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@main_bp.route('/profile')
def profile():
    """User Profile & Request Tracker Dashboard."""
    if not session.get('user_id'):
        flash('Please login to access your profile.', 'warning')
        return redirect(url_for('main.login'))

    user = User.query.get(session['user_id'])
    my_requests = EmergencyRequest.query.filter_by(sender_name=user.username).order_by(EmergencyRequest.created_at.desc()).all()
    my_predictions = RiskPrediction.query.order_by(RiskPrediction.created_at.desc()).limit(10).all()

    return render_template('profile.html', user=user, my_requests=my_requests, my_predictions=my_predictions)
