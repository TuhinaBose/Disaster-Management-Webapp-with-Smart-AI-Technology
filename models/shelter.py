from datetime import datetime
from database import db

class Shelter(db.Model):
    """
    Shelter model storing verified emergency relief camps, shelters, and centers.
    
    Required Fields:
    name, address, state, district, city_village, latitude, longitude,
    total_capacity, current_occupancy, available_capacity, contact, verification_status
    """
    __tablename__ = 'shelters'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.Text, nullable=False)
    state = db.Column(db.String(100), nullable=False, default='Delhi NCR')
    district = db.Column(db.String(100), nullable=False)
    city_village = db.Column(db.String(100), nullable=False, default='Central City')
    facility_type = db.Column(db.String(50), nullable=False, default='Shelter') # 'Shelter', 'School', 'College', 'Hospital', 'Community Center', 'Stadium', 'Building'
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    total_capacity = db.Column(db.Integer, nullable=False)
    current_occupancy = db.Column(db.Integer, nullable=False, default=0)
    available_capacity = db.Column(db.Integer, nullable=False, default=0)
    contact = db.Column(db.String(50), nullable=False, default='+91-108')
    verification_status = db.Column(db.String(20), nullable=False, default='Verified') # 'Verified' or 'Unverified'
    
    has_food = db.Column(db.Boolean, default=True)
    has_water = db.Column(db.Boolean, default=True)
    has_medical = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def recalculate_capacity(self):
        """Ensures available capacity is automatically total_capacity - current_occupancy."""
        if self.current_occupancy < 0:
            self.current_occupancy = 0
        if self.current_occupancy > self.total_capacity:
            self.current_occupancy = self.total_capacity
        self.available_capacity = self.total_capacity - self.current_occupancy

    @property
    def contact_number(self):
        """Backwards compatibility alias for contact."""
        return self.contact

    @contact_number.setter
    def contact_number(self, value):
        self.contact = value

    @property
    def available_beds(self):
        """Backwards compatibility alias for available_capacity."""
        return self.available_capacity

    @available_beds.setter
    def available_beds(self, value):
        self.available_capacity = value

    def to_dict(self):
        """Converts model instance to JSON dictionary for API endpoints and maps."""
        self.recalculate_capacity()
        occ_pct = round((self.current_occupancy / self.total_capacity) * 100, 1) if self.total_capacity > 0 else 0
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
            'current_occupancy': self.current_occupancy,
            'available_capacity': self.available_capacity,
            'available_beds': self.available_capacity,
            'occupancy_percentage': occ_pct,
            'has_food': self.has_food,
            'has_water': self.has_water,
            'has_medical': self.has_medical,
            'contact': self.contact,
            'contact_number': self.contact,
            'verification_status': self.verification_status,
            'is_verified': self.verification_status == 'Verified',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
