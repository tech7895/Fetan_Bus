from flask import Blueprint, render_template, flash, redirect, request, jsonify, url_for, abort
from .models import Customer, Bus, Seat, Payment
from .forms import AvailableBusesForm, PaymentForm
from flask_login import login_required, current_user
from . import db

views = Blueprint('views', __name__)


@views.route('/')
def home():

    items = Bus.query.filter_by(flash_sale=True)
    
    return render_template('home.html')# items=items, cart = Cart.query.filter_by(customer_link=current_user.id).all()
                            #if current_user.is_authenticated else [] )
                            
@views.route('/about')
def about():

    items = Bus.query.filter_by(flash_sale=True)
    
    return render_template('about.html')

@views.route('/profile/<customer_username>')
def profile(customer_username):
    customer = Customer.query.all()
    
    return render_template('profile.html', customer=customer)

@views.route('/find-bus', methods=['GET', 'POST'])
@login_required
def find_bus():
    form = AvailableBusesForm()
    return render_template('find-bus.html', form=form)

@views.route('/available', methods=['GET', 'POST'])
@login_required
def available():
    
    form = AvailableBusesForm()
    if form.validate_on_submit:
        departure = form.departure.data
        destination = form.destination.data
        departure_date = form.departure_date.data
        
        filtered_buses = Bus.query.filter_by(departure=departure, destination=destination, departure_date=departure_date).all()        
            
        if filtered_buses:
            # Pass filtered bus data to the available.html template
            #flash('Buses found for the selected route')
            return render_template('available.html', items=filtered_buses)
            #return redirect(url_for('admin.available', filtered_buses=filtered_buses))
        else:
            flash('No buses found for the selected route and dates.')
            return render_template('find-bus.html', form=form)
    
@views.route('/select-seats/<int:bus_id>', methods=['GET', 'POST'])
@login_required
def select_seats(bus_id):
    # Fetch the selected bus from the database
    selected_bus = Bus.query.get(bus_id)
    if selected_bus:
        # Render the seat selection page and pass the selected bus information
        return render_template('seat.html', bus=selected_bus)
    else:
        flash('Selected bus not found.')
        return redirect(url_for('views.find_bus'))
    
@views.route('/confirm-booking/<int:bus_id>', methods=['POST', 'GET'])
@login_required
def confirm_booking(bus_id):
    if request.method == 'POST':
        # Fetch the selected bus ID from the form data
        #bus_id = request.form.get('bus_id')
        # Fetch the selected seats from the form data
        selected_seats = request.form.getlist('selected_seats[]')
        
        # Create a new Seat object and store the selected seats in the database
        seat = Seat(selected_seats=",".join(selected_seats))  # Assuming selected seats are stored as comma-separated values
        db.session.add(seat)
        db.session.commit()
        
        flash('Booking confirmed successfully!')
        return redirect(url_for('views.payment_options', bus_id=bus_id))  # Redirect to the payment page after confirming booking
    else:
        return redirect(url_for('views.find_bus'))

"""
@views.route('/payment-options/<int:bus_id>', methods=['POST', 'GET'])
@login_required
def payment_options(bus_id):
    # Fetch the bus object using the bus_id
    bus = Bus.query.get(bus_id)
    if not bus:
        abort(404)  # Return a 404 error if bus is not found
    
    fields = Payment.query.order_by(Payment.date_added).all()
    if not fields:
        return render_template('no-payments.html')

    return render_template('payment-options.html', bus=bus, fields=fields)
    """
################################################################################
"""
@views.route('/payment-options/<int:bus_id>', methods=['GET', 'POST'])
@login_required
def payment_options(bus_id):
    if current_user.id == 1:
        bus = Bus.query.get(bus_id)
        fields = Payment.query.order_by(Payment.date_added).all()
        return render_template('payment-options.html', bus=bus, fields=fields)
    return render_template('404.html')
"""
###################################################################################

@views.route('/payment-options/<int:bus_id>', methods=['GET', 'POST'])
@login_required
def payment_options(bus_id):
    if current_user.id == 1:
        bus = Bus.query.get(bus_id)
        fields = Payment.query.order_by(Payment.date_added).all()
        return render_template('payment-options.html', fields=fields, bus=bus)
    return render_template('404.html')

#####################################################################################
"""
@views.route('/payment-options')
@login_required
def payment_options():
    if current_user.id == 1:
        fields = Payment.query.order_by(Payment.date_added).all()
        return render_template('payment-options.html', fields=fields)
    return render_template('404.html')

"""
@views.route('/make-payment/<int:bus_id>', methods=['GET', 'POST'])
@login_required
def make_payment(bus_id):
    # Fetch the selected seats from the database
    selected_seats_entry = Seat.query.first()  # Assuming you only have one entry in the Seat table for simplicity
    # Split the selected seats string into a list
    selected_seats = selected_seats_entry.selected_seats.split(",") if selected_seats_entry else []
    selected_bus = Bus.query.get(bus_id)
    # Calculate the total price based on the number of selected seats
    total_price = len(selected_seats) * selected_bus.price  # Assuming selected_bus is defined somewhere
    #images = Payment.query.all()
    # Calculate the charge (5% of total amount)
    charge = total_price * 0.05

    return render_template('make-payment.html', num_seats=len(selected_seats), total_amount=total_price, charge=charge)#, images=images)
