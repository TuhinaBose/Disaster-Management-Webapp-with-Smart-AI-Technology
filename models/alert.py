from datetime import datetime
from database import db

class DisasterAlert(db.Model):
    """
    DisasterAlert model storing warning bulletins, weather warnings, and emergency alerts.
    """
    __tablename__ = 'disaster_alerts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    disaster_type = db.Column(db.String(50), nullable=False) # 'Flood', 'Cyclone', 'Earthquake', 'Heavy Rain', 'Fire'
    severity = db.Column(db.String(20), nullable=False)       # 'Critical', 'Warning', 'Advisory'
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Converts model instance to JSON dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'disaster_type': self.disaster_type,
            'severity': self.severity,
            'location': self.location,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
