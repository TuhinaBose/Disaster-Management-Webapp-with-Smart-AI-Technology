from datetime import datetime
from database import db

class Shelter(db.Model):
    """
    Shelter model storing details about emergency relief camps and centers.
    """
    __tablename__ = 'shelters'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.Text, nullable=False)
    state = db.Column(db.String(100), nullable=False, default='Delhi NCR')
    district = db.Column(db.String(100), nullable=False)
    city_village = db.Column(db.String(100), nullable=False, default='Central City')
    facility_type = db.Column(db.String(50), nullable=False, default='Building') # 'School', 'College', 'Hospital', 'Community Center', 'Stadium', 'Building'
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    total_capacity = db.Column(db.Integer, nullable=False)
    available_beds = db.Column(db.Integer, nullable=False)
    has_food = db.Column(db.Boolean, default=True)
    has_water = db.Column(db.Boolean, default=True)
    has_medical = db.Column(db.Boolean, default=True)
    contact_number = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Converts model instance to JSON dictionary for API endpoints and maps."""
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'state': self.state,
            'district': self.district,
            'city_village': self.city_village,
            'facility_type': self.facility_type,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'total_capacity': self.total_capacity,
            'available_beds': self.available_beds,
            'occupancy_percentage': round(((self.total_capacity - self.available_beds) / self.total_capacity) * 100, 1) if self.total_capacity > 0 else 0,
            'has_food': self.has_food,
            'has_water': self.has_water,
            'has_medical': self.has_medical,
            'contact_number': self.contact_number,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
