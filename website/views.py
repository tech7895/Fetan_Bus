from flask import Blueprint, render_template, flash, redirect, request, url_for, abort, send_file, session, render_template_string, make_response, jsonify
from .models import Customer, Bus, Payment, Ticket
from .forms import AvailableBusesForm, PaymentForm
from flask_login import login_required, current_user
from . import db
#from flask_weasyprint import HTML, render_pdf
import pdfkit
import imgkit
import io
from datetime import datetime, time



views = Blueprint('views', __name__)


@views.route('/')
def index():
    
    return render_template('index.html')# items=items, cart = Cart.query.filter_by(customer_link=current_user.id).all()
                            #if current_user.is_authenticated else [] )
                            
@views.route('/about')
def about():
    
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
        departure = capitalize_first_letter(form.departure.data)
        destination = capitalize_first_letter(form.destination.data)
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
    return render_template('404.html')

def capitalize_first_letter(s):
    return s.capitalize() if s else s


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
        
        # Store the selected seats for the specific bus
        bus = Bus.query.get_or_404(bus_id)
        bus.seats = ', '.join(selected_seats)
        #bus.seats = '|'.join(selected_seats)
        db.session.commit()
        
        return redirect(url_for('views.payment_options', bus_id=bus_id))  # Redirect to the payment page after confirming booking
    else:
        return redirect(url_for('views.find_bus'))


@views.route('/payment-options/<int:bus_id>', methods=['GET', 'POST'])
@login_required
def payment_options(bus_id):
        bus = Bus.query.get_or_404(bus_id)
        fields = Payment.query.order_by(Payment.date_added).all()
        
        return render_template('payment-options.html', fields=fields, bus=bus)



@views.route('/make-payment/<int:bus_id>', methods=['GET', 'POST'])
@login_required
def make_payment(bus_id):
    # Fetch the selected bus and its corresponding selected seats
    selected_bus = Bus.query.get_or_404(bus_id)
    selected_seats = selected_bus.seats.split(",") if selected_bus.seats else []

    # Calculate the total price based on the number of selected seats
    total_price = len(selected_seats) * selected_bus.price

    # Calculate the charge (5% of total amount)
    charge = round(total_price * 0.05, 2)

    # Assuming 'payment_id' and 'bank_name' are passed from the payment options page
    payment_id = request.args.get('payment_id')
    selected_payment = Payment.query.get(payment_id)

    if not selected_payment:
        abort(404)  # Handle invalid payment method

    bank_name = selected_payment.bank_name
    bank_logo = selected_payment.bank_logo  # Assuming you have a 'bank_logo' field in your Payment model

    return render_template('make-payment.html', 
                           bus_id=bus_id, 
                           num_seats=len(selected_seats), 
                           total_amount=total_price, 
                           charge=charge,
                           bank_name=bank_name,
                           bank_logo=bank_logo)


@views.route('/ticket/<int:bus_id>', methods=['GET', 'POST'])
@login_required
def show_ticket(bus_id):
    selected_bus = Bus.query.get_or_404(bus_id)

    # Retrieve bus information
    bus_name = selected_bus.bus_name
    side_number = selected_bus.side_number
    departure = selected_bus.departure
    destination = selected_bus.destination
    departure_date = selected_bus.departure_date
    departure_time = selected_bus.departure_time
    arrival_time = selected_bus.arrival_time
    user_name = current_user.username

    selected_seats = selected_bus.seats
    seat_number = ''.join(selected_seats) if selected_seats else ''

    # Convert departure_time and arrival_time to time objects
    departure_time_obj = datetime.strptime(departure_time, '%I:%M %p').time()  # Parse departure time
    arrival_time_obj = datetime.strptime(arrival_time, '%I:%M %p').time()      # Parse arrival time

    # Create a new ticket record in the database
    ticket = Ticket(
        user_id=current_user.id,
        bus_id=bus_id,
        seat_number=seat_number,
        bus_name=bus_name,
        side_number=side_number,
        departure=departure,
        destination=destination,
        departure_date=departure_date,
        departure_time=departure_time_obj,  # Use parsed time object
        arrival_time=arrival_time_obj       # Use parsed time object
    )
    db.session.add(ticket)
    db.session.commit()

    # Render the ticket.html template with the bus information and seat details
    return render_template('ticket.html', bus=selected_bus, seat_number=seat_number, user_name=user_name)


"""
# Define route to download the ticket as PDF or JPG
@views.route('/generatepdf', methods=['POST'])
def generatepdf():
    # Retrieve necessary data to generate the ticket (e.g., seat numbers, bus details)
    seat_numbers = request.form.getlist('selected_seats[]')
    bus_name = request.form.get('bus_name')
    departure = request.form.get('departure')
    destination = request.form.get('destination')
    departure_date = request.form.get('departure_date')
    departure_time = request.form.get('departure_time')
    arrival_time = request.form.get('arrival_time')
    customer_name = request.form.get('customer_name')

    # Render HTML template for the ticket
    html_content = render_template('ticket.html', seat_numbers=seat_numbers,
                                   bus_name=bus_name, departure=departure,
                                   destination=destination, departure_date=departure_date,
                                   departure_time=departure_time, arrival_time=arrival_time,
                                   customer_name=customer_name)

    # Generate PDF from HTML content using WeasyPrint
    pdf = HTML(string=html_content).write_pdf()

    # Save the PDF file to a temporary location or serve it directly
    pdf_filename = 'ticket.pdf'
    with open(pdf_filename, 'wb') as f:
        f.write(pdf)

    # Return the PDF file as a downloadable attachment
    return send_file(pdf_filename, as_attachment=True)
    
"""

@views.route('/your-bookings', methods=['GET'])
@login_required
def your_bookings():
    user_id = current_user.id
    # Query tickets for the current user
    tickets = Ticket.query.filter_by(user_id=user_id).all()

    bookings = []
    for ticket in tickets:
        # Fetch the associated bus details
        bus = Bus.query.get(ticket.bus_id)
        
        bus_info = {
            'bus_name': ticket.bus_name,
            'side_number': ticket.side_number,
            'departure': ticket.departure,
            'destination': ticket.destination,
            'departure_date': ticket.departure_date,
            'departure_time': ticket.departure_time,
            'arrival_time': ticket.arrival_time,
            'seat_number': ticket.seat_number,
            #'booking_date': ticket.booking_date.strftime('%Y-%m-%d %H:%M:%S') # Uncomment if you have a booking_date field
        }
        bookings.append(bus_info)

    return render_template('your-bookings.html', bookings=bookings)


