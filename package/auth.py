from flask import Blueprint, render_template, redirect, flash, request, url_for
from flask_login import login_required, logout_user, login_user
from .form import SignupForm, LoginForm
from . import db
from .models import Customer, Bus, Schedule, Ticket, Payment
from .form import PasswordChangeForm, EmailChangeForm
from werkzeug.security import generate_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password1 = form.password1.data
        password2 = form.password2.data
        
        if password1 == password2:
            new_customer = Customer()
            new_customer.username = username
            new_customer.email = email
            new_customer.set_password(password2)  # Ensure password is hashed
            
            try:
                db.session.add(new_customer)
                db.session.commit()
                flash('Account created successfully, You can now login', 'success')
                return redirect('/login')
            except Exception as e:
                db.session.rollback()  # Rollback in case of exception to avoid partial commits
                print(e)  # Log the specific exception for debugging
                flash('Account not created! Username/Email already exists.', 'danger')
    
    return render_template('signup.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username_or_email = form.username_or_email.data
        password = form.password.data 
        
        customer = Customer.query.filter_by(username=username_or_email).first() or Customer.query.filter_by(email=username_or_email).first()
        if customer:
            if not customer.is_active:
                flash('This account does not exist anymore', 'danger')
            elif customer.check_password(password=password):
                login_user(customer)
                return redirect('/')
            else:
                flash('Incorrect email or password', 'danger')
        else:
            flash('This account does not exist', 'danger')
                    
    return render_template('login.html', form=form)

@auth.route('/profile/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def profile(customer_id):
    customer = Customer.query.get(customer_id)
    return render_template('profile.html', customer=customer)


@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect('/home')


@auth.route('/change-password/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def change_password(customer_id):
    customer = Customer.query.get(customer_id)
    form = PasswordChangeForm()

    if form.validate_on_submit():
        current_password = form.current_password.data
        new_password = form.new_password.data
        confirm_new_password = form.confirm_new_password.data

        if customer.check_password(current_password):
            if new_password == confirm_new_password:
                customer.set_password(new_password)
                db.session.commit()
                flash('Password Updated Successfully', 'success')
                return redirect(f'/profile/{customer_id}')
            else:
                flash('Passwords did not match!!')
        else:
            flash('Current password is incorrect!', 'danger')
    
    return render_template('change-password.html', form=form, customer_id=customer_id)


@auth.route('/change-email/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def change_email(customer_id):
    customer = Customer.query.get(customer_id)
    form = EmailChangeForm()

    if form.validate_on_submit():
        new_email = form.new_email.data

        # Update the email address
        customer.email = new_email
        db.session.commit()

        flash('Email Updated Successfully', 'success')
        return redirect(f'/profile/{customer_id}')
    
    return render_template('change-email.html', form=form, customer_id=customer_id)


# A route to delete an account

@auth.route('/delete-account/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def delete_account(customer_id):
    account_to_delete = Customer.query.get(customer_id)
    if not account_to_delete:
        flash('Account not found', 'danger')
        return redirect(url_for('auth.profile'))

    if request.method == 'POST':
        password = request.form.get('password')
        
        if account_to_delete and account_to_delete.check_password(password):
            try:
                # Delete associated records
                Ticket.query.filter_by(customer_id=customer_id).delete()
                Schedule.query.filter_by(customer_id=customer_id).delete()
                Payment.query.filter_by(customer_id=customer_id).delete()
                Bus.query.filter_by(customer_id=customer_id).delete()
                
                # Commit the changes
                db.session.commit()
                
                # Delete the customer account
                db.session.delete(account_to_delete)
                db.session.commit()
                
                flash('Account deleted successfully', 'success')
                return redirect(url_for('auth.signup'))
            except Exception as e:
                db.session.rollback()
                print('Error deleting account:', e)
                flash('An error occurred while deleting the account', 'danger')
        else:
            flash('Incorrect password. Please try again.', 'danger')

    return render_template('delete-account.html', customer_id=customer_id)
