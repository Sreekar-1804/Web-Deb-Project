from applications.database import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=True, default='default.jpg')
    password = db.Column(db.String(128), nullable=False)  # Store hashed passwords
    approved = db.Column(db.Boolean(), default=False)
    
    # Relationships
    roles = db.relationship('Role', secondary='user_role', backref=db.backref('users', lazy=True))
    customer_dets = db.relationship('Customer', backref='user', lazy=True, uselist=False)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mobile_no = db.Column(db.String(10), unique=True, nullable=False)
    address = db.Column(db.String(255), nullable=False)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)

class UserRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)

class Services(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    service_name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer, nullable=False)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)  # Allow NULL
    professional_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    remarks = db.Column(db.String(500), nullable=True)
    date_requested = db.Column(db.DateTime, nullable=False)
    date_completed = db.Column(db.DateTime, nullable=True)
    cost = db.Column(db.Float, nullable=True)

    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='bookings_as_customer', lazy=True)
    professional = db.relationship('User', foreign_keys=[professional_id], backref='bookings_as_professional', lazy=True)
    service = db.relationship('Services', backref='bookings', lazy=True)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    professional_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # Rating from 1-5
    feedback = db.Column(db.String(500), nullable=True)  # Optional text feedback
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    booking = db.relationship('Booking', backref='review', lazy=True)
    customer = db.relationship('User', foreign_keys=[customer_id], backref='reviews_given', lazy=True)
    professional = db.relationship('User', foreign_keys=[professional_id], backref='reviews_received', lazy=True)
    service = db.relationship('Services', backref='reviews', lazy=True)
