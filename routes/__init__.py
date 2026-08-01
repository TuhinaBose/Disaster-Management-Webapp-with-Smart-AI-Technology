from .main_routes import main_bp
from .feature_routes import feature_bp
from .admin_routes import admin_bp

def register_blueprints(app):
    """Registers all application blueprints."""
    app.register_blueprint(main_bp)
    app.register_blueprint(feature_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
