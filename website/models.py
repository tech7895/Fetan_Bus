from . import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class Customer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(100), unique=True)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password_hash = db.Column(db.String(150))
    date_joined = db.Column(db.DateTime(), default=datetime.utcnow)
    
    # Define a relationship with Bus
    buses = db.relationship('Bus', backref='customer', lazy=True)
    
    # Define a relationship with Payment
    payments = db.relationship('Payment', backref='customer', lazy=True)
    
    tickets = db.relationship('Ticket', backref='customer', lazy=True)
    
    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password=password)
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password=password)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def __str__(self):
        return '<Customer %r>' % self.id


class Bus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    departure = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    bus_name = db.Column(db.String(100), nullable=False)
    side_number = db.Column(db.Integer, nullable=False)
    bus_picture = db.Column(db.String(1000), nullable=False)
    departure_date = db.Column(db.Date, nullable=False)
    departure_time = db.Column(db.String(20), nullable=False)
    arrival_time = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    
    seats = db.Column(db.String(220), nullable=False, default='')  # Assuming seats are stored as comma-separated values
    # Define a relationship with Customer
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    
    # Define a relationship with Payment
    payments = db.relationship('Payment', backref='bus', lazy=True)
    
    tickets = db.relationship('Ticket', backref='bus', lazy=True)
    
    def __str__(self):
        return '<Bus %r>' % self.bus_name




class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bank_name = db.Column(db.String(100), nullable=False)
    bank_logo = db.Column(db.String(1000), nullable=False)
    # Add other attributes as needed
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Define a relationship with Customer
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    
    # Define a relationship with Bus
    bus_id = db.Column(db.Integer, db.ForeignKey('bus.id'), nullable=False)
    
    def __str__(self):
        return '<Payment %r>' % self.bank_name
    
    
class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)  # Corrected foreign key reference
    bus_id = db.Column(db.Integer, db.ForeignKey('bus.id'), nullable=False)
    seat_number = db.Column(db.String(50), nullable=False)
    bus_name = db.Column(db.String(100), nullable=False)
    side_number = db.Column(db.String(50), nullable=False)
    departure = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    departure_date = db.Column(db.Date, nullable=False)
    departure_time = db.Column(db.Time, nullable=False)
    arrival_time = db.Column(db.Time, nullable=False)
    # Add any additional fields as necessary

    def __repr__(self):
        return (f"Ticket(user_id={self.user_id}, bus_id={self.bus_id}, seat_number='{self.seat_number}', "
                f"bus_name='{self.bus_name}', side_number='{self.side_number}', departure='{self.departure}', "
                f"destination='{self.destination}', departure_date={self.departure_date}, "
                f"departure_time={self.departure_time}, arrival_time={self.arrival_time})")
