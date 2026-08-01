from datetime import datetime
from database import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    """
    User model storing registered users and administrator accounts.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user') # 'admin' or 'user'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        """Hashes and sets user password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifies provided password against stored hash."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Converts model instance to JSON serializable dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
