from datetime import datetime
from database import db

class RiskPrediction(db.Model):
    """
    RiskPrediction model storing history of AI disaster predictions and inputs.
    """
    __tablename__ = 'predictions'

    id = db.Column(db.Integer, primary_key=True)
    rainfall = db.Column(db.Float, nullable=False)
    river_level = db.Column(db.Float, nullable=False)
    wind_speed = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    earthquake_mag = db.Column(db.Float, nullable=False)
    predicted_risk = db.Column(db.String(20), nullable=False) # 'Low', 'Medium', 'High'
    risk_score = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Converts model instance to JSON dictionary."""
        return {
            'id': self.id,
            'rainfall': self.rainfall,
            'river_level': self.river_level,
            'wind_speed': self.wind_speed,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'earthquake_mag': self.earthquake_mag,
            'predicted_risk': self.predicted_risk,
            'risk_score': self.risk_score,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
