from flask import Blueprint, render_template, flash, send_from_directory, redirect, url_for, current_app, request
from flask_login import login_required, current_user
from .forms import AvailableBusesForm, OrderForm, PaymentForm
from werkzeug.utils import secure_filename
from .models import Bus, Seat, Customer, Payment
from datetime import datetime
from . import db

admin = Blueprint('admin', __name__)


@admin.route('/media/<path:filename>')
def get_image(filename):
    return send_from_directory('../media', filename)

@admin.route('/add-routes', methods=['GET', 'POST'])
@login_required
def add_routes():
    if current_user.id == 1:
        form = AvailableBusesForm()

        if form.validate_on_submit():
            departure = form.departure.data
            destination = form.destination.data
            bus_name = form.bus_name.data
            departure_date = form.departure_date.data
            departure_time = form.departure_time.data
            arrival_time = form.arrival_time.data
            price = form.price.data
            
            #in_stock = form.in_stock.data
            flash_sale = form.flash_sale.data

             # Convert departure_date_str to a Python datetime object
            

        # Now you can use departure_date in your database insertion code
        
            file = form.bus_picture.data

            file_name = secure_filename(file.filename)

            file_path = f'./media/{file_name}'

            file.save(file_path)

            new_bus = Bus()
            new_bus.departure = departure
            new_bus.destination = destination
            new_bus.bus_name = bus_name
            new_bus.departure_date = departure_date
            new_bus.departure_time = departure_time
            new_bus.arrival_time = arrival_time
            new_bus.price = price
            new_bus.flash_sale = flash_sale


            new_bus.bus_picture = file_path

            try:
                db.session.add(new_bus)
                db.session.commit()
                flash(f'{bus_name} added Successfully')
                return render_template('add-routes.html', form=form)
            except Exception as e:
                print(e)
                flash('Route Not Added!!')

        return render_template('add-routes.html', form=form)

    return render_template('404.html')


@admin.route('/manage-routes', methods=['GET', 'POST'])
@login_required
def manage_routes():
    if current_user.id == 1:
        fields = Bus.query.order_by(Bus.date_added).all()
        return render_template('manage-routes.html', fields=fields)
    return render_template('404.html')


 # Redirect to the same page to allow user to search again
        #except Exception as e:
        #    current_app.logger.error(f"An error occurred while processing your request: {str(e)}")
        #    flash('An error occurred while processing your request.')
    
    # For GET requests or if form validation fails, render the form
    
@admin.route('/add-payment', methods=['GET', 'POST'])
@login_required
def add_payment():
    if current_user.id == 1:
        form = PaymentForm()

        if form.validate_on_submit():
            
            bank_name = form.bank_name.data

        
            file = form.bank_logo.data

            file_name = secure_filename(file.filename)

            file_path = f'./media/{file_name}'

            file.save(file_path)

            new_payment = Payment()
            new_payment.bank_name = bank_name
            new_payment.bank_logo = file_path

            try:
                db.session.add(new_payment)
                db.session.commit()
                flash(f'{bank_name} added Successfully')
                return render_template('add-payment.html', form=form)
            except Exception as e:
                print(e)
                flash('Payment Method Not Added!!')

        return render_template('add-payment.html', form=form)

    return render_template('404.html')

@admin.route('/manage-banks', methods=['GET', 'POST'])
@login_required
def manage_banks():
    if current_user.id == 1:
        fields = Payment.query.order_by(Payment.date_added).all()
        return render_template('manage-banks.html', fields=fields)
    return render_template('404.html')
"""
@admin.route('/available', methods=['GET'])
def available_buses():
    # Query all available buses from the database (example query)
    available_buses = Bus.query.all()
    
    # Render the available.html template and pass the list of available buses
    return render_template('available.html', buses=available_buses)





@admin.route('/confirm-booking', methods=['POST'])
@login_required
def confirm_booking():
    # Handle the confirmation of booking
    bus_id = request.form.get('bus_id')
    # Fetch selected seats from the request
    selected_seats = request.form.getlist('selected_seats')
    
    # Perform booking confirmation logic here
    
    # Redirect to a confirmation page or any other page as needed
    return redirect(url_for('admin.booking_confirmation'))


@admin.route('/booking-confirmation')
@login_required
def booking_confirmation():
    # Render the booking confirmation page
    return render_template('booking_confirmation.html')
    
"""

    


@admin.route('/update-field/<int:field_id>', methods=['GET', 'POST'])
@login_required
def update_field(field_id):
    if current_user.id == 1:
        form = AvailableBusesForm()

        field_to_update = Bus.query.get(field_id)

        form.departure.render_kw = {'placeholder': field_to_update.departure}
        form.destination.render_kw = {'placeholder': field_to_update.destination}
        form.bus_name.render_kw = {'placeholder': field_to_update.bus_name}
        form.departure_date.render_kw = {'placeholder': field_to_update.departure_date}
        form.departure_time.render_kw = {'placeholder': field_to_update.departure_time}
        form.arrival_time.render_kw = {'placeholder': field_to_update.arrival_time}
        form.price.render_kw = {'placeholder': field_to_update.price}
        form.flash_sale.render_kw = {'placeholder': field_to_update.flash_sale}

        if form.validate_on_submit():
            departure = form.departure.data
            destination = form.destination.data
            bus_name = form.bus_name.data
            departure_date = form.departure_date.data
            departure_time = form.departure_time.data
            arrival_time = form.arrival_time.data
            price = form.price.data
            flash_sale = form.flash_sale.data

            file = form.bus_picture.data

            file_name = secure_filename(file.filename)
            file_path = f'./media/{file_name}'

            file.save(file_path)

            try:
                Bus.query.filter_by(id=field_id).update(dict(departure=departure,
                                                                destination=destination,
                                                                bus_name=bus_name,
                                                                departure_date = departure_date,
                                                                departure_time=departure_time,
                                                                arrival_time=arrival_time,
                                                                price = price,
                                                                flash_sale=flash_sale,
                                                                bus_picture=file_path))

                db.session.commit()
                flash(f'{ bus_name} updated Successfully')
                print('Field Upadted')
                return redirect('/manage-routes')
            except Exception as e:
                print('Field not Upated', e)
                flash('Field Not Updated!!!')

        return render_template('update-field.html', form=form)
    return render_template('404.html')


@admin.route('/delete-field/<int:field_id>', methods=['GET', 'POST'])
@login_required
def delete_field(field_id):
    if current_user.id == 1:
        try:
            field_to_delete = Bus.query.get(field_id)
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

    return redirect(url_for('admin.manage_routes'))