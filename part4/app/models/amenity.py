import uuid
from datetime import datetime
from .basemodel import BaseModel
from app.extensions import db
from sqlalchemy.orm import validates


class Amenity(BaseModel):
    __tablename__ = "amenities"

    name = db.Column(db.String(255), nullable=False)

    @validates("name")
    def validate_name(self, key, value):
        if not isinstance(value, str):
            raise TypeError("Name must be a string")
        if value == "":
            raise ValueError("Name is required")
        if len(value) > 50:
            raise ValueError("Name must be less than 50 character")
        return value
