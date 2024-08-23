from flask import Blueprint, flash, redirect, render_template, url_for, jsonify, request, current_app, send_from_directory
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from .form import AddBusForm, AddScheduleForm, PaymentForm
from .models import Customer, Bus, Schedule, Payment, Ticket
from sqlalchemy import desc, asc
from . import db
import os

admin = Blueprint('admin', __name__)

# Define your default image file name
DEFAULT_IMAGE = 'default_bus.png'

@admin.route('/media/<path:filename>')
def get_image(filename):
    return send_from_directory('../media', filename)


@admin.route('/add-buses', methods=['GET', 'POST'])
@login_required
def add_buses():
    if current_user.id == 1:
        form = AddBusForm()
        if form.validate_on_submit():
            bus_type = form.bus_type.data
            side_number = form.side_number.data
            bus_picture = form.bus_picture.data

            if bus_picture:
                file = form.bus_picture.data
                file_name = secure_filename(bus_picture.filename)
                #file_path = os.path.join('static/images/buses', file_name)
                #file_path = os.path.join(current_app.root_path, 'static/images/buses', file_name)
                file_path = f'./media/{file_name}'

                file.save(file_path)


            # Inside your route function
            else:
                # Use default image path if no picture is provided
                file_path = f'./static/images/buses/{DEFAULT_IMAGE}'



            try:
                new_bus = Bus(bus_type=bus_type, side_number=side_number, bus_picture=file_path, customer_id=current_user.id)
                db.session.add(new_bus)
                db.session.commit()
                flash('Bus added successfully', 'success')
            except Exception as e:
                print('Error adding bus:', e)
                flash('An error occurred while adding the bus', 'danger')

            return redirect(url_for('admin.add_buses'))
        return render_template('add-buses.html', form=form)
    else:
        return render_template('404.html')
    
    
@admin.route('/get-bus', methods=['GET', 'POST'])
@login_required
def get_bus():
    # If the request method is POST, handle form submission
    if request.method == 'POST':
        # Process the form data here if needed
        pass

    # Get distinct bus types from the database
    bus_types = Bus.query.with_entities(Bus.bus_type).distinct().all()
    bus_types_list = [bus_type[0] for bus_type in bus_types]

    # Render the template and pass bus types to populate the dropdown menu
    return render_template('get-bus.html', bus_types=bus_types_list)


@admin.route('/get-bus-data', methods=['GET'])
def get_bus_data():
    # Fetch all distinct bus types from the Bus model
    bus_types = Bus.query.with_entities(Bus.bus_type).distinct().all()
    
    # Convert the query results to lists
    bus_types_list = [bus_type[0] for bus_type in bus_types]
    
    # Return the bus types as JSON
    return jsonify({'bus_types': bus_types_list})



@admin.route('/get-side-numbers', methods=['GET'])
def get_side_numbers():
    selected_bus_type = request.args.get('bus_type')
    if selected_bus_type:
        side_numbers = Bus.query.filter_by(bus_type=selected_bus_type).with_entities(Bus.id, Bus.side_number).all()
        side_numbers_list = [{'id': bus.id, 'number': bus.side_number} for bus in side_numbers]
        return jsonify(side_numbers_list)
    else:
        return jsonify([])




from datetime import datetime

@admin.route('/add-schedule', methods=['GET', 'POST'])
@login_required
def add_schedule():
    bus_id = request.form.get('bus_id')  # Changed to request.form to match form submission
    bus = Bus.query.get(bus_id)
    
    if not bus_id or not bus:
        flash('Bus not found', 'danger')
        return redirect(url_for('admin.get_bus'))
    
    form = AddScheduleForm()
    
    if form.validate_on_submit():
        departure = form.departure.data
        destination = form.destination.data
        departure_date = form.departure_date.data  # Retrieve as string from form
        departure_time = form.departure_time.data
        arrival_time = form.arrival_time.data
        price = float(form.price.data)
        travel_packages = form.travel_packages.data
        
        try:
            new_schedule = Schedule(
                departure=departure,
                destination=destination,
                departure_date=departure_date,
                departure_time=departure_time,
                arrival_time=arrival_time,
                price=price,
                travel_packages=travel_packages,
                bus_id=bus.id,
                customer_id=current_user.id
            )
            db.session.add(new_schedule)
            db.session.commit()
            flash('Schedule added successfully', 'success')
            return redirect(url_for('admin.get_bus'))
        except Exception as e:
            db.session.rollback()  # Rollback the transaction on error
            print('Error adding schedule:', e)
            flash('An error occurred while adding the schedule', 'danger')

    return render_template('add-schedule.html', form=form, bus=bus)


@admin.route('/manage-buses', methods=['GET', 'POST'])
@login_required
def manage_buses():
    if current_user.id == 1:
        fields = Bus.query.order_by(desc(Bus.date_added)).all()
        return render_template('manage-buses.html', fields=fields)
    return render_template('404.html')

@admin.route('/manage-schedule', methods=['GET', 'POST'])
@login_required
def manage_schedule():
    if current_user.id == 1:
        # Join Schedule and Bus tables
        schedules = db.session.query(Schedule, Bus).join(Bus, Schedule.bus_id == Bus.id).order_by(desc(Schedule.date_added)).all()
        
        # Dictionary to hold reserved seat counts for each schedule
        reserved_seat_counts = {}

        for schedule, bus in schedules:
            # Fetch reserved tickets for the current schedule
            reserved_tickets = Ticket.query.filter_by(schedule_id=schedule.id).all()
            
            # Initialize a set to store all reserved seat numbers
            reserved_seat_numbers = set()

            for ticket in reserved_tickets:
                # Split seat numbers by comma and add to the set
                seats = ticket.seat_number.split(', ')
                reserved_seat_numbers.update(seats)
            
            # Count the total number of reserved seats
            reserved_seat_counts[schedule.id] = len(reserved_seat_numbers)
            

        # Render the manage schedule page and pass the schedules and reserved seat counts
        return render_template('manage-schedule.html', schedules=schedules, reserved_seat_counts=reserved_seat_counts)
    else:
        flash('You do not have permission to view this page.', 'danger')
        return redirect(url_for('views.get_schedule'))




@admin.route('/add-payment', methods=['GET', 'POST'])
@login_required
def add_payment():
    # Only allow access to this route for users with specific roles (e.g., admin)
    if current_user.id == 1:  # Adjust this condition based on your role or permission logic
        form = PaymentForm()

        if form.validate_on_submit():
            bank_name = form.bank_name.data
            bank_logo = form.bank_logo.data
            
            # Save bank logo to a designated directory
            if bank_logo:
                file = form.bank_logo.data
                filename = secure_filename(bank_logo.filename)
                file_path = f'./media/{filename}'
                file.save(file_path)

                # Create a new Payment instance and add to the database
                new_payment = Payment(
                    bank_name=bank_name,
                    bank_logo=file_path,
                    customer_id=current_user.id,  # Assuming you have a 'customer_id' field
                    bus_id=current_user.id  # Assuming you have a 'bus_id' field
                )

                try:
                    db.session.add(new_payment)
                    db.session.commit()
                    flash(f'{bank_name} added successfully!', 'success')
                    return redirect(url_for('admin.add_payment'))  # Redirect to clear the form
                except Exception as e:
                    db.session.rollback()
                    flash('Failed to add payment method.', 'error')
                    print(e)  # Print the exception for debugging

        # Render the add-payment.html template with the form
        return render_template('add-payment.html', form=form)

    # If user does not have the required role or permission, show 404 page
    return render_template('404.html')


####################################################################################################
@admin.route('/admin-page')
@login_required
def admin_page():
    if current_user.id == 1:
        
        #fields = Bus.query.order_by(Bus.date_added).all()
        return render_template('admin-page.html')#, fields=fields)
    return render_template('404.html')


@admin.route('/manage-banks', methods=['GET', 'POST'])
@login_required
def manage_banks():
    if current_user.id == 1:
        fields = Payment.query.order_by(Payment.date_added).all()
        return render_template('manage-banks.html', fields=fields)
    return render_template('404.html')    


@admin.route('/update-schedule/<int:field_id>', methods=['GET', 'POST'])
@login_required
def update_schedule(field_id):
    if current_user.id == 1:
        form = AddScheduleForm()

        # Fetch the schedule and associated bus to update
        field_to_update = Schedule.query.get_or_404(field_id)
        bus_to_update = field_to_update.bus  # Assuming 'bus' is a relationship on 'Schedule'

        if form.validate_on_submit():
            try:
                departure = form.departure.data
                destination = form.destination.data
                departure_date = form.departure_date.data  # Retrieve as string from form
                departure_time = form.departure_time.data
                arrival_time = form.arrival_time.data
                price = float(form.price.data)
                travel_packages = form.travel_packages.data

                # Update bus and schedule details
                field_to_update.departure = departure
                field_to_update.destination = destination
                field_to_update.departure_date = departure_date
                field_to_update.departure_time = departure_time
                field_to_update.arrival_time = arrival_time
                field_to_update.price = price
                field_to_update.travel_packages = travel_packages

                db.session.commit()
                flash(f'Field updated successfully', 'success')
                return redirect('/manage-schedule')
            except Exception as e:
                print('Error updating bus:', e)
                flash('Failed to update bus!', 'danger')

        # Populate form fields with current values
        form.departure.data = field_to_update.departure if hasattr(field_to_update, 'departure') else ''
        form.destination.data = field_to_update.destination if hasattr(field_to_update, 'destination') else ''
        form.departure_date.data = field_to_update.departure_date
        form.departure_time.data = field_to_update.departure_time
        form.arrival_time.data = field_to_update.arrival_time
        form.price.data = field_to_update.price
        form.travel_packages.data = field_to_update.travel_packages

        return render_template('update-schedule.html', form=form, bus=bus_to_update, field_to_update=field_to_update)
    return render_template('404.html')




        # Populate form fields with current values
        #form.departure.data = bus_to_update.departure
        #form.destination.data = bus_to_update.destination
        #form.bus_name.data = bus_to_update.bus_name
        #form.departure_date.data = field_to_update.departure_date
        #form.departure_time.data = field_to_update.departure_time
        #form.arrival_time.data = field_to_update.arrival_time
        #form.price.data = field_to_update.price





@admin.route('/delete-bus/<int:bus_id>', methods=['GET', 'POST'])
@login_required
def delete_bus(bus_id):
    if current_user.id == 1:
        try:
            bus_to_delete = Bus.query.get(bus_id)
            if bus_to_delete:               
                # First, delete all related schedules
                Schedule.query.filter_by(bus_id=bus_id).delete()
                
                # Now delete the bus
                db.session.delete(bus_to_delete)
                db.session.commit()
                flash('Bus and its related schedules deleted successfully', 'success')
            else:
                flash('Bus not found', 'danger')
        except Exception as e:
            print('Error deleting bus:', e)
            flash('An error occurred while deleting the bus', 'danger')
    else:
        flash('Unauthorized to delete buses.', 'danger')

    return redirect(url_for('admin.manage_buses'))



@admin.route('/delete-schedule/<int:schedule_id>', methods=['GET', 'POST'])
@login_required
def delete_schedule(schedule_id):
    if current_user.id == 1:
        try:
            schedule_to_delete = Schedule.query.get(schedule_id)
            if schedule_to_delete:
                # Update related tickets to set schedule_id to None
                #Ticket.query.filter_by(schedule_id=schedule_id).update({"schedule_id": None})
                Ticket.query.filter_by(schedule_id=schedule_id).delete()
                
                db.session.commit()  # Commit the update before deleting the schedule
                
                db.session.delete(schedule_to_delete)
                db.session.commit()
                flash('Bus schedule deleted successfully', 'success')
            else:
                flash('Bus schedule not found', 'danger')
        except Exception as e:
            print('Error deleting bus:', e)
            flash('An error occurred while deleting the bus schedule', 'danger')
    else:
        flash('Unauthorized to delete bus schedules.', 'danger')

    return redirect(url_for('admin.manage_schedule'))




@admin.route('/delete-bank/<int:bank_id>', methods=['GET', 'POST'])
@login_required
def delete_bank(bank_id):
    if current_user.id == 1:
        try:
            field_to_delete = Payment.query.get(bank_id)
            if field_to_delete:
                db.session.delete(field_to_delete)
                db.session.commit()
                flash('Field deleted successfully')
            else:
                flash('Field not found')
        except Exception as e:
            print('Field not deleted', e)
            flash('Field not deleted!')
    else:
        flash('Unauthorized to delete fields.')

    return redirect(url_for('admin.manage_banks'))

