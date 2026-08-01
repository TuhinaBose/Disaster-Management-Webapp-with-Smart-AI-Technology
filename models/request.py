from datetime import datetime
from database import db

class EmergencyRequest(db.Model):
    """
    EmergencyRequest model storing citizen SOS distress calls and rescue requests.
    """
    __tablename__ = 'emergency_requests'

    id = db.Column(db.Integer, primary_key=True)
    sender_name = db.Column(db.String(100), nullable=False)
    contact_phone = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    urgency_level = db.Column(db.String(20), nullable=False) # 'Critical', 'High', 'Medium'
    situation_description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Pending') # 'Pending', 'In Progress', 'Resolved'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Converts model instance to JSON dictionary."""
        return {
            'id': self.id,
            'sender_name': self.sender_name,
            'contact_phone': self.contact_phone,
            'location': self.location,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'urgency_level': self.urgency_level,
            'situation_description': self.situation_description,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
