from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(50), nullable=True)  # Corrected: db.String, not db.string
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    # Relationships
    bookings = db.relationship('Booking', backref='user', lazy=True)


class Flight(db.Model):
    __tablename__ = 'flight'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    flight_number = db.Column(db.String(10), unique=True, nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False)
    origin = db.Column(db.String(50), nullable=False)
    destination = db.Column(db.String(50), nullable=False)
    airline = db.Column(db.String(50), nullable=False)
    total_seats = db.Column(db.Integer, nullable=False)

    # Relationships
    bookings = db.relationship('Booking', backref='flight', lazy=True)
    seats = db.relationship('Seat', backref='flight', lazy=True)

class Booking(db.Model):
    __tablename__ = 'booking'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    flight_id = db.Column(db.Integer, db.ForeignKey('flight.id'), nullable=False)
    booking_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(
        db.Enum('CONFIRMED', 'CANCELLED', name='booking_status'),
        nullable=False,
        default='CONFIRMED'
    )

class Seat(db.Model):
    __tablename__ = 'seat'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    flight_id = db.Column(db.Integer, db.ForeignKey('flight.id'), nullable=False)
    seat_number = db.Column(db.String(10), nullable=False)
    is_available = db.Column(db.Boolean, nullable=False, default=True)
