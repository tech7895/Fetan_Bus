from flask_login import UserMixin
from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import CheckConstraint
import uuid

class Customer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(100))
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    date_joined = db.Column(db.DateTime(), default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    buses = db.relationship('Bus', backref='customer', cascade="all, delete-orphan")
    schedules = db.relationship('Schedule', backref='customer', lazy=True)
    payments = db.relationship('Payment', backref='customer', lazy=True)
    tickets = db.relationship('Ticket', backref='customer', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def hide_account(self):
        self.is_active = False
    
    def __repr__(self):
        return f'<Customer {self.id}>'

class Bus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bus_type = db.Column(db.String(50), nullable=False)
    side_number = db.Column(db.Integer, nullable=False)
    seats = db.Column(db.String(220), nullable=False, default='')
    bus_picture = db.Column(db.String(150), nullable=False, default='default_bus.png')
    date_added = db.Column(db.DateTime(), default=datetime.utcnow)
    
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id', ondelete='SET NULL'), nullable=True)
    
    tickets = db.relationship('Ticket', backref='bus', lazy=True)
    schedules = db.relationship('Schedule', backref='bus', lazy=True)
    
    def __repr__(self):
        return f'<Bus {self.id}, Type: {self.bus_type}>'

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    departure = db.Column(db.String(50), nullable=False)
    destination = db.Column(db.String(50), nullable=False)
    departure_date = db.Column(db.Date, nullable=False)
    departure_time = db.Column(db.String(50), nullable=False)
    arrival_time = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    date_added = db.Column(db.DateTime(), default=datetime.utcnow)
    travel_packages = db.Column(db.String(200), nullable=True)
    
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id', ondelete='SET NULL'), nullable=True)
    tickets = db.relationship('Ticket', backref='schedule', lazy=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('bus.id'), nullable=False)
    
    def __repr__(self):
        return f'<Schedule {self.id}, From: {self.departure} To: {self.destination}>'

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bank_name = db.Column(db.String(150), nullable=False)
    bank_logo = db.Column(db.String(150), nullable=False)
    date_added = db.Column(db.DateTime(), default=datetime.utcnow)
    
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id', ondelete='SET NULL'), nullable=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('bus.id'), nullable=False)
    
    def __repr__(self):
        return f'<Payment {self.bank_name}>'
    

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    bus_id = db.Column(db.Integer, db.ForeignKey('bus.id'), nullable=False)
    seat_number = db.Column(db.String(50), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'), nullable=False)
    ticket_number = db.Column(db.String(50), unique=True, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    # Static fields to store schedule details
    departure = db.Column(db.String(120), nullable=False)
    destination = db.Column(db.String(120), nullable=False)
    departure_date = db.Column(db.String(50), nullable=False)
    departure_time = db.Column(db.String(50), nullable=False)
    arrival_time = db.Column(db.String(50), nullable=False)
    bus_type = db.Column(db.String(50), nullable=False)
    bus_side_number = db.Column(db.String(50), nullable=False)

    # Define relationship to Price model
    prices = db.relationship('Price', backref='ticket', lazy=True)

    def __init__(self, customer_id, bus_id, seat_number, schedule_id, ticket_number, departure, destination, departure_date, departure_time, arrival_time, bus_type, bus_side_number):
        self.customer_id = customer_id
        self.bus_id = bus_id
        self.seat_number = seat_number
        self.schedule_id = schedule_id
        self.ticket_number = ticket_number
        self.departure = departure
        self.destination = destination
        self.departure_date = departure_date
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.bus_type = bus_type
        self.bus_side_number = bus_side_number

    def __repr__(self):
        return (f"Ticket(customer_id={self.customer_id}, bus_id={self.bus_id}, seat_number='{self.seat_number}', "
                f"schedule_id={self.schedule_id})")


        
class Price(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(100), nullable=False)
    date_added = db.Column(db.DateTime(), default=datetime.utcnow)

    def __init__(self, ticket_id, amount, payment_method):
        self.ticket_id = ticket_id
        self.amount = amount
        self.payment_method = payment_method

    def __repr__(self):
        return f"Price(ticket_id={self.ticket_id}, amount={self.amount}, payment_method='{self.payment_method}')"
