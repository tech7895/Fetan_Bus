from flask import session, Blueprint, render_template, flash, request, redirect, url_for, abort, jsonify, send_from_directory, current_app
from flask_login import login_required, current_user
from .form import AddScheduleForm
from .models import Customer, Bus, Schedule, Ticket, Payment, Price
from . import db
from datetime import datetime
import uuid
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc, asc



views = Blueprint('views', __name__)


@views.route('/')
@views.route('/home')
def index():
    return render_template('index.html')

@views.route('/about')
def about():
    return render_template('about.html')




@views.route('/get-schedule', methods=['GET', 'POST'])
@login_required
def get_bus():
    # If the request method is POST, handle form submission
    if request.method == 'POST':
        # Process the form data here if needed
        pass
 
    
    departures = Schedule.query.with_entities(Schedule.departure)
    departure_list = [departure[0] for departure in departures]
    
    destinations = Schedule.query.with_entities(Schedule.destination)
    destination_list = [destination[0] for destination in destinations]

    # Render the template and pass bus types to populate the dropdown menu
    return render_template('get-schedule.html', departures=departure_list, destinations=destination_list)


@views.route('/get-schedule-data', methods=['GET'])
def get_schedule_data():
    departures = Schedule.query.with_entities(Schedule.departure).distinct().all()
    departure_list = [departure[0] for departure in departures]
    
    destinations = Schedule.query.with_entities(Schedule.destination).distinct().all()
    destination_list = [destination[0] for destination in destinations]
    
    return jsonify({'departures': departure_list, 'destinations': destination_list})




@views.route('/available_schedules', methods=['GET', 'POST'])
@login_required
def available_schedules():
    if request.method == 'POST':
        # Retrieve form data
        departure = request.form.get('departure')
        destination = request.form.get('destination')
        departure_date_str = request.form.get('departure_date')
        
        # Convert the departure_date_str to a datetime object
        departure_date = datetime.strptime(departure_date_str, '%Y-%m-%d').date()
        today = datetime.today().date()
        
        # Check if the departure date is in the past
        if departure_date < today:
            flash('No schedule for past dates.', 'danger')
            return redirect(url_for('views.get_bus'))
        
        # Store data in session for later retrieval in select_seats route
        session['search_data'] = {
            'departure': departure,
            'destination': destination,
            'departure_date': departure_date_str  # Store as string for simplicity
        }
        
        # Fetch the requested schedules from the database
        schedules = Schedule.query.filter_by(departure=departure, destination=destination, departure_date=departure_date).all()
        
        # Render the results in the available-schedules.html template
        return render_template('available-schedules.html', schedules=schedules)
    
    elif request.method == 'GET':
        # Check if search data exists in the session
        search_data = session.get('search_data')
        
        if search_data:
            departure = search_data['departure']
            destination = search_data['destination']
            departure_date_str = search_data['departure_date']
            
            # Convert departure_date_str to datetime object
            departure_date = datetime.strptime(departure_date_str, '%Y-%m-%d').date()
            
            # Fetch the requested schedules from the database
            schedules = Schedule.query.filter_by(departure=departure, destination=destination, departure_date=departure_date).all()
            
            # Render the results in the available-schedules.html template
            return render_template('available-schedules.html', schedules=schedules)
        
        # If no search data, redirect to the get_bus page
        return redirect(url_for('views.get_bus'))
    
    # Default to redirect to the get_bus page if method is not GET or POST
    return redirect(url_for('views.get_bus'))



@views.route('/select-seats/<int:bus_id>', methods=['GET', 'POST'])
@login_required
def select_seats(bus_id):
    # Fetch the selected bus from the database
    selected_bus = Schedule.query.get(bus_id)
    
    if selected_bus:
        # Fetch session data for departure, destination, and departure date
        search_data = session.get('search_data')
        if not search_data:
            flash('Session data expired. Please search again.')
            return redirect(url_for('views.get_bus'))
        
        departure = search_data['departure']
        destination = search_data['destination']
        departure_date_str = search_data['departure_date']
        
        # Convert departure_date_str to datetime object
        departure_date = datetime.strptime(departure_date_str, '%Y-%m-%d').date()
        
        schedules = Schedule.query.filter_by(departure=departure, destination=destination, departure_date=departure_date).all()
        # Fetch reserved seats for the selected bus
        reserved_tickets = Ticket.query.filter_by(schedule_id=selected_bus.id).all()
        
        # Initialize a set to store all reserved seat numbers
        reserved_seat_numbers = set()

        for ticket in reserved_tickets:
            # Split seat numbers by comma and add to the set
            seats = ticket.seat_number.split(', ')
            reserved_seat_numbers.update(seats)
        
        # Count the total number of reserved seats
        reserved_seat_counts = len(reserved_seat_numbers)
        
        if reserved_seat_counts == 60:
            flash('Seats are full, please choose another bus.', 'danger')
            return redirect(url_for('views.available_schedules'))
        
        # Render the seat selection page and pass the selected bus information and reserved seats count
        return render_template('choose-seats.html', bus=selected_bus, reserved_seat_counts=reserved_seat_counts, reserved_seat_numbers=list(reserved_seat_numbers))
    else:
        flash('Selected bus not found.')
        return redirect(url_for('views.find_bus'))

    
    
@views.route('/confirm-booking/<int:bus_id>', methods=['POST', 'GET'])
@login_required
def confirm_booking(bus_id):
    if request.method == 'POST':
        # Fetch the selected seats from the form data
        selected_seats = request.form.getlist('selected_seats[]')

        if not selected_seats:
            flash('No seats selected.', 'danger')
            return redirect(url_for('views.select_seats', bus_id=bus_id))

        # Ensure that bus_id is valid and fetch the associated schedule
        bus_schedule = Schedule.query.get_or_404(bus_id)
       
        # Store the selected seats in the session
        session['selected_seats'] = selected_seats
        
        return redirect(url_for('views.payment_options', bus_id=bus_id))

    # Handle GET request method (optional)
    # You can decide if you want to handle GET requests differently or redirect to another page
    return redirect(url_for('views.find_bus'))
    
    
@views.route('/payment-options/<int:bus_id>', methods=['GET', 'POST'])
@login_required
def payment_options(bus_id):
        bus = Schedule.query.get_or_404(bus_id)
        fields = Payment.query.order_by(Payment.date_added).all()
        return render_template('payment-options.html', fields=fields, bus=bus)
    
    
@views.route('/check-seats/<int:bus_id>', methods=['POST'])
@login_required
def check_seats(bus_id):
    data = request.get_json()
    selected_seats = data.get('selected_seats', [])

    reserved_seats = Ticket.query.filter(Ticket.schedule_id == bus_id, Ticket.seat_number.in_(selected_seats)).all()
    if reserved_seats:
        return jsonify({'success': False, 'message': 'One or more selected seats are already reserved.'})

    return jsonify({'success': True})

 
   
@views.route('/make-payment/<int:bus_id>', methods=['GET', 'POST'])
@login_required
def make_payment(bus_id):
    if request.method == 'GET':
        try:
            selected_seats = session.get('selected_seats', [])
            seat_number = ', '.join(selected_seats) if selected_seats else ''

            # Query for selected bus
            selected_bus = Schedule.query.join(Bus).filter(Schedule.id == bus_id).first()
            if not selected_bus:
                abort(404)

            total_price = len(selected_seats) * selected_bus.price
            charge = round(total_price * 0.05, 2)

            payment_id = request.args.get('payment_id')
            selected_payment = Payment.query.get(payment_id)
            if not selected_payment:
                abort(404)

            bank_name = selected_payment.bank_name
            bank_logo = selected_payment.bank_logo

            return render_template('make-payment.html', 
                                   bus_id=bus_id, 
                                   num_seats=len(selected_seats), 
                                   total_amount=total_price, 
                                   charge=charge,
                                   bank_name=bank_name,
                                   bank_logo=bank_logo,
                                   payment_id=payment_id)

        except Exception as e:
            flash('An unexpected error occurred while processing your request. Please try again later.', 'error')
            current_app.logger.error(f'Error in make_payment GET: {str(e)}')
            return redirect(url_for('views.select_seats', bus_id=bus_id))

    elif request.method == 'POST':
        try:
            selected_bus = Schedule.query.join(Bus).filter(Schedule.id == bus_id).first()
            if not selected_bus:
                abort(404)

            selected_seats = session.get('selected_seats', [])
            seat_number = ', '.join(selected_seats) if selected_seats else ''
            total_price = len(selected_seats) * selected_bus.price
            charge = round(total_price * 0.05, 2)

            payment_id = request.form.get('payment_id')
            selected_payment = Payment.query.get(payment_id)
            if not selected_payment:
                abort(404)

            bank_name = selected_payment.bank_name
            bank_logo = selected_payment.bank_logo

            # Check if any of the selected seats are already reserved
            reserved_seats = Ticket.query.filter(Ticket.schedule_id == selected_bus.id, Ticket.seat_number.in_(selected_seats)).all()
            if reserved_seats:
                flash('Seats are already reserved.', 'danger')
                return redirect(url_for('views.select_seats', bus_id=bus_id))

            # Process each seat and create a ticket
            ticket_info = []
            for seat in selected_seats:
                ticket_number = str(uuid.uuid4().hex.upper()[:10])  # Generate a new ticket number for each seat

                ticket = Ticket(
                    customer_id=current_user.id,
                    bus_id=selected_bus.bus.id,
                    seat_number=seat,
                    schedule_id=selected_bus.id,
                    ticket_number=ticket_number,
                    departure=selected_bus.departure,
                    destination=selected_bus.destination,
                    departure_date=selected_bus.departure_date.strftime('%a, %d %b %Y'),
                    departure_time=selected_bus.departure_time,
                    arrival_time=selected_bus.arrival_time,
                    bus_type=selected_bus.bus.bus_type,
                    bus_side_number=selected_bus.bus.side_number
                )
                db.session.add(ticket)
                db.session.commit()  # Commit the ticket to get the id assigned

                price = Price(
                    ticket_id=ticket.id,  # Use ticket.id here
                    amount=selected_bus.price,
                    payment_method=selected_payment.bank_name,
                )
                db.session.add(price)

                # Append ticket info to list
                ticket_info.append({
                    'bus_id': str(bus_id),
                    'user_name': current_user.username,
                    'seat_numbers': [seat],
                    'ticket_number': ticket_number,  # Each ticket has its own unique ticket number
                    'bus_side_number': str(selected_bus.bus.side_number),
                    'bus_type': selected_bus.bus.bus_type,
                    'departure': selected_bus.departure,
                    'destination': selected_bus.destination,
                    'departure_date': selected_bus.departure_date.strftime('%a, %d %b %Y'),
                    'departure_time': selected_bus.departure_time,
                    'arrival_time': selected_bus.arrival_time
                })

            db.session.commit()

            # Store ticket_info in session
            session['ticket_info'] = ticket_info
            return redirect(url_for('views.show_ticket', bus_id=bus_id))

        except IntegrityError as e:
            db.session.rollback()
            flash('An error occurred while processing your request. Please try again.', 'error')
            current_app.logger.error(f'IntegrityError in make_payment POST: {str(e)}')
            return redirect(url_for('views.select_seats', bus_id=bus_id))

        except Exception as e:
            db.session.rollback()
            flash('An unexpected error occurred while processing your request. Please try again later.', 'danger')
            current_app.logger.error(f'Error in make_payment POST: {str(e)}')
            return redirect(url_for('views.select_seats', bus_id=bus_id))




@views.route('/ticket/<int:bus_id>', methods=['GET'])
@login_required
def show_ticket(bus_id):
    ticket_info_list = session.get('ticket_info')

    # Check if ticket information is available and filter
    # tickets for the given bus_id
    if not ticket_info_list or not any(ticket.get('bus_id') == str(bus_id) for ticket in ticket_info_list):
        flash('Ticket information not found or expired.')
        abort(404)

    # Filter tickets for the given bus_id
    tickets = [ticket for ticket in ticket_info_list if ticket.get('bus_id') == str(bus_id)]

    # Prepare formatted departure_date
    for ticket in tickets:
        departure_date_parts = ticket['departure_date'].split(',')[1].split(' ')[1:4]
        departure_date = ' '.join(departure_date_parts)
        date_obj = datetime.strptime(departure_date, '%d %b %Y')
        ticket['formatted_departure_date'] = date_obj.strftime('%a, %d %b %Y')
        
    return render_template('ticket.html', tickets=tickets)

# Custom error handler for 404 errors
@views.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404




@views.route('/your-bookings', methods=['GET'])
@login_required
def your_bookings():
    customer_id = current_user.id
    tickets = Ticket.query.filter_by(customer_id=customer_id).order_by((desc(Ticket.id))).all()

    bookings = {}

    for ticket in tickets:
        if ticket.ticket_number not in bookings:
            bookings[ticket.ticket_number] = {
                'bus_type': ticket.bus_type,
                'side_number': ticket.bus_side_number,
                'departure': ticket.departure,
                'destination': ticket.destination,
                'departure_date': ticket.departure_date,
                'departure_time': ticket.departure_time,
                'arrival_time': ticket.arrival_time,
                'ticket_number': ticket.ticket_number,
                'seat_numbers': [],
                'booking_date': ticket.date_added.strftime('%a, %d %b %Y %H:%M:%S') if isinstance(ticket.date_added, datetime) else ticket.date_added
            }
        bookings[ticket.ticket_number]['seat_numbers'].append(ticket.seat_number)

    booking_list = list(bookings.values())

    return render_template('your-bookings.html', bookings=booking_list)
