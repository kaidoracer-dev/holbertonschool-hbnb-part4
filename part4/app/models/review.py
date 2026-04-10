import uuid
from datetime import datetime
from .basemodel import BaseModel
from app.extensions import db
from sqlalchemy.orm import validates


class Review(BaseModel):
    __tablename__ = 'reviews'

    text = db.Column(db.String, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    place_id = db.Column(db.Integer, db.ForeignKey('places.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    @validates("text")
    def validate_text(self, key, value):
        """
        Check if the text is a string and non empty
        """
        if not isinstance(value, str):
            raise TypeError("Text must be a string")
        if value == "":
            raise ValueError("Text is required")
        return value

    @validates("rating")
    def validate_rating(self, key, value):
        """
        Check if the rating is an int between 1 or 5
        """
        if not isinstance(value, int):
            raise TypeError("Rating must an integer")
        if not 1 <= value <= 5:
            raise ValueError("Rating must be an integer bewteen 1 and 5")
        return value

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "text": self.text,
            "rating": self.rating,
            "place_id": self.place_id,
            "user_id": self.user_id
        })
        return data
