from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text

# Initialize SQLAlchemy Database Instance
db = SQLAlchemy()

def init_db(app):
    """
    Binds the Flask application instance to SQLAlchemy
    and creates/migrates database tables automatically.
    """
    db.init_app(app)
    with app.app_context():
        inspector = inspect(db.engine)
        if inspector.has_table("shelters"):
            columns = [c['name'] for c in inspector.get_columns("shelters")]
            # If table exists with legacy schema lacking current_occupancy, recreate table cleanly
            if "current_occupancy" not in columns or "verification_status" not in columns:
                print("[Database Migration] Updating legacy shelter table schema...")
                try:
                    db.session.execute(text("DROP TABLE IF EXISTS shelters"))
                    db.session.commit()
                except Exception:
                    pass

        # Create all tables defined in models
        db.create_all()
