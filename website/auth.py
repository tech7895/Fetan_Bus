from flask import Blueprint, render_template, flash, redirect, url_for, request
from .forms import LoginForm, SignUpForm, UpdateForm, PasswordChangeForm, EmailChangeForm
from .models import Bus, Customer
from . import db
from flask_login import login_user, login_required, logout_user



auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        password1 = form.password1.data
        password2 = form.password2.data
        
        if password1 == password2:
           new_customer = Customer()
           new_customer.email = email
           new_customer.username = username
           new_customer.password = password2
           
           try:
               db.session.add(new_customer)
               db.session.commit()
               flash('Account has been created successfully, You can now login')
               return redirect('/login')
           except Exception as e:
               print(e)
               flash('Account not created!, Email already existes')
               
        form.email.data = ''
        form.username.data = ''
        form.password1.data = ''
        form.password2.data = ''
               
                
    return render_template('signup.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        
        customer = Customer.query.filter_by(email=email).first()
        
        if customer:
            if customer.verify_password(password=password):
                login_user(customer)
                return redirect('/')
            else:
                flash('Incorrect email or password')
                
        else:
            flash('This account does not exist')
    return render_template('login.html', form=form)

@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def log_out():
    logout_user()
    return redirect('/')


@auth.route('/profile/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def profile(customer_id):
    customer = Customer.query.get(customer_id)
    form = UpdateForm()

    if form.validate_on_submit():
        # Process the uploaded image
        image_file = request.files['profile-image']
        # Save the image to the server and update the database record
        # Remember to handle image file names, paths, etc.

    image_file = url_for('static', filename='images/'+ customer.image_file)
    return render_template('profile.html', customer=customer, image_file=image_file, form=form)

@auth.route('/change-password/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def change_password(customer_id):
    customer = Customer.query.get(customer_id)
    form = PasswordChangeForm()

    if form.validate_on_submit():
        current_password = form.current_password.data
        new_password = form.new_password.data
        confirm_new_password = form.confirm_new_password.data

        if customer.verify_password(current_password):
            if new_password == confirm_new_password:
                customer.set_password(new_password)
                db.session.commit()
                flash('Password Updated Successfully')
                return redirect(f'/profile/{customer_id}')
            else:
                flash('Passwords did not match!!')
        else:
            flash('Current password is incorrect!')
    
    return render_template('change-password.html', form=form)


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

        flash('Email Updated Successfully')
        return redirect(f'/profile/{customer_id}')
    
    return render_template('change-email.html', form=form)
