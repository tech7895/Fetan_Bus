from . import db, LoginManager
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
    
    #cart_items = db.relationship('Cart', backref=db.backref('customer', lazy=True))
    #orders = db.relationship('Order', backref=db.backref('customer', lazy=True))
    
    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password=password)
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password=password)
    
    
    def __str__(self):
        return '<Customer %r>' % Customer.id # print(customer1) <Customer 01>

class Bus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    departure = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    bus_name = db.Column(db.String(100), nullable=False)
    bus_picture = db.Column(db.String(1000), nullable=False)
    departure_date = db.Column(db.Date, nullable=False)
    departure_time = db.Column(db.String(20), nullable=False)
    arrival_time = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    flash_sale = db.Column(db.Boolean, default=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __str__(self):
        return '<Bus %r>' % self.bus_name


class Seat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    selected_seats = db.Column(db.String(220), nullable=False)
    
    def __repr__(self):
        return '<Seat %r>' % self.selected_seats
    

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bank_name = db.Column(db.String(100), nullable=False)
    bank_logo = db.Column(db.String(1000), nullable=False)
    # Add other attributes as needed
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign key referencing Bus
    #bus_id = db.Column(db.Integer, db.ForeignKey('bus.id'), nullable=False)
    #bus = db.relationship('Bus', backref=db.backref('payments', lazy=True))

    def __str__(self):
        return '<Payment %r>' % self.bank_name

