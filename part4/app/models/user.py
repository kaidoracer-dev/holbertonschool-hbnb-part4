import uuid
from .basemodel import BaseModel
from app.extensions import db, bcrypt
from sqlalchemy.orm import validates
import re

class User(BaseModel):
    __tablename__ = 'users'

    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    places = db.relationship('Place', backref='user', lazy=True, cascade='all, delete')
    reviews = db.relationship('Review', backref='user', lazy=True, cascade='all, delete')

    @validates("first_name")
    def validate_first_name(self, key, value):
        if not isinstance(value, str):
            raise TypeError("First Name must be a string")
        if value == "":
            raise ValueError("First Name is required")
        if len(value) > 50:
            raise ValueError("First Name must be less than 50 characters")
        return value

    @validates("last_name")
    def validate_last_name(self, key, value):
        if not isinstance(value, str):
            raise TypeError("Last Name must be a string")
        if value == "":
            raise ValueError("Last Name is required")
        if len(value) > 50:
            raise ValueError("Last Name must be less than 50 characters")
        return value

    @validates("email")
    def validate_email(self, key, value):
        regex = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}"
        if not isinstance(value, str):
            raise TypeError("Email must be a string")
        if value == "":
            raise ValueError("Email is required")
        if not re.fullmatch(regex, value):
            raise ValueError("Email must be in format: myemail@address.com")
        return value

    def hash_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        return bcrypt.check_password_hash(self.password, password)