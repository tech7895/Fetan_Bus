from flask import Blueprint, render_template, flash, send_from_directory, redirect, url_for, current_app, request
from flask_login import login_required, current_user
from .forms import AvailableBusesForm, OrderForm, PaymentForm
from werkzeug.utils import secure_filename
from .models import Bus, Customer, Payment
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
            side_number = form.side_number.data
            departure_date = form.departure_date.data
            departure_time = form.departure_time.data
            arrival_time = form.arrival_time.data
            price = form.price.data
            
             # Set customer_id to the ID of the current user
            customer_id = current_user.id
            #payments = current_user.id

        
            file = form.bus_picture.data

            file_name = secure_filename(file.filename)

            file_path = f'./media/{file_name}'

            file.save(file_path)

            new_bus = Bus()
            new_bus.departure = departure
            new_bus.destination = destination
            new_bus.bus_name = bus_name
            new_bus.side_number = side_number
            new_bus.departure_date = departure_date
            new_bus.departure_time = departure_time
            new_bus.arrival_time = arrival_time
            new_bus.price = price


            new_bus.bus_picture = file_path
            new_bus.customer_id = customer_id  # Set customer_id
            #new_bus.payments = payments  # Assign payments

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


@admin.route('/admin-page')
@login_required
def admin_page():
    if current_user.id == 1:
        
        #fields = Bus.query.order_by(Bus.date_added).all()
        return render_template('admin-page.html')#, fields=fields)
    return render_template('404.html')


@admin.route('/manage-routes', methods=['GET', 'POST'])
@login_required
def manage_routes():
    if current_user.id == 1:
        fields = Bus.query.order_by(Bus.date_added).all()
        return render_template('manage-routes.html', fields=fields)
    return render_template('404.html')


 
@admin.route('/add-payment', methods=['GET', 'POST'])
@login_required
def add_payment():
    # Only allow access to this route for users with specific roles (e.g., admin)
    if current_user.id == 1:  # Adjust this condition based on your role or permission logic
        form = PaymentForm()

        if form.validate_on_submit():
            bank_name = form.bank_name.data
            bank_logo_file = form.bank_logo.data
            
            # Save bank logo to a designated directory
            if bank_logo_file:
                filename = secure_filename(bank_logo_file.filename)
                file_path = f'./media/{filename}'
                bank_logo_file.save(file_path)

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

@admin.route('/manage-banks', methods=['GET', 'POST'])
@login_required
def manage_banks():
    if current_user.id == 1:
        fields = Payment.query.order_by(Payment.date_added).all()
        return render_template('manage-banks.html', fields=fields)
    return render_template('404.html')    


@admin.route('/update-field/<int:field_id>', methods=['GET', 'POST'])
@login_required
def update_field(field_id):
    if current_user.id == 1:
        form = AvailableBusesForm()

        field_to_update = Bus.query.get(field_id)

        form.departure.render_kw = {'placeholder': field_to_update.departure}
        form.destination.render_kw = {'placeholder': field_to_update.destination}
        form.bus_name.render_kw = {'placeholder': field_to_update.bus_name}
        form.side_number_kw = {'placeholder': field_to_update.side_number}
        form.departure_date.render_kw = {'placeholder': field_to_update.departure_date}
        form.departure_time.render_kw = {'placeholder': field_to_update.departure_time}
        form.arrival_time.render_kw = {'placeholder': field_to_update.arrival_time}
        form.price.render_kw = {'placeholder': field_to_update.price}

        if form.validate_on_submit():
            departure = form.departure.data
            destination = form.destination.data
            bus_name = form.bus_name.data
            side_number = form.side_number.data
            departure_date = form.departure_date.data
            departure_time = form.departure_time.data
            arrival_time = form.arrival_time.data
            price = form.price.data

            file = form.bus_picture.data

            file_name = secure_filename(file.filename)
            file_path = f'./media/{file_name}'

            file.save(file_path)

            try:
                Bus.query.filter_by(id=field_id).update(dict(departure=departure,
                                                                destination=destination,
                                                                bus_name=bus_name,
                                                                side_number = side_number,
                                                                departure_date = departure_date,
                                                                departure_time=departure_time,
                                                                arrival_time=arrival_time,
                                                                price = price,
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
