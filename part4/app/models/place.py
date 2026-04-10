import uuid
from datetime import datetime
from app.extensions import db
from sqlalchemy.orm import validates
from .basemodel import BaseModel

#Adding a table for the many-to-many relationship between places and amenities
place_amenities = db.Table('place_amenities',
    db.Column('place_id', db.Integer, db.ForeignKey('places.id'), primary_key=True),
    db.Column('amenity_id', db.Integer, db.ForeignKey('amenities.id'), primary_key=True)
)

class Place(BaseModel):
    __tablename__ = 'places'

    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reviews = db.relationship('Review', backref='place', lazy=True, cascade='all, delete')
    amenities = db.relationship('Amenity', secondary=place_amenities, lazy='subquery', backref=db.backref('places', lazy=True))

    @validates("title")
    def validate_title(self, key, value):
        if not isinstance(value, str):
            raise TypeError("Title must be a string")
        self._title = value
        if value == "":
            raise ValueError("Title is required")
        if len(value) > 100:
            raise ValueError("Title must be under 100 Characters")
        return value

    @validates("description")
    def validate_description(self, key, value):
        if value is not None and not isinstance(value, str):
            raise TypeError("Description must be a string or None")
        return value

    @validates("price")
    def validate_price(self, key, value):
        if not isinstance(value, (float, int)):
            raise TypeError("Price must be a number")
        value = float(value)
        if value < 0:
            raise ValueError("Price must be positive")
        return value

    @validates("latitude")
    def validate_latitude(self, key, value):
        if not isinstance(value, float):
            raise TypeError("Latitude must be a Float")
        if not (-90.0 <= value <= 90.0):
            raise ValueError("Latitude must be between -90.0 and 90.0")
        return value

    @validates("longitude")
    def validate_longitude(self, key, value):
        if not isinstance(value, float):
            raise TypeError("Longitude must be a Float")
        if not (-180.0 <= value <= 180.0):
            raise ValueError("longitude must be between -180.0 and 180.0")
        return value

    def add_review(self, review):
        """Add a review to the place."""
        self.reviews.append(review)

    def add_amenity(self, amenity):
        """Add an amenity to the place."""
        self.amenities.append(amenity)
