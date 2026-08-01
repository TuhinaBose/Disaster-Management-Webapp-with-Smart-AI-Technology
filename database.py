from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy Database Instance
db = SQLAlchemy()

def init_db(app):
    """
    Binds the Flask application instance to SQLAlchemy
    and creates missing database tables automatically.
    """
    db.init_app(app)
    with app.app_context():
        # Create all tables defined in models if they don't exist yet
        db.create_all()
