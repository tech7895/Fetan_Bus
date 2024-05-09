from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, PasswordField, EmailField, BooleanField, DateField, SubmitField, SelectField
from wtforms.validators import DataRequired, length, NumberRange
from flask_wtf.file import FileField, FileRequired
from flask_login import current_user


class SignUpForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired(), length(min=2)])
    password1 = PasswordField('Enter Your Password', validators=[DataRequired(), length(min=6)])
    password2 = PasswordField('Confirm Your Password', validators=[DataRequired(), length(min=6)])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Enter Your Password', validators=[DataRequired()])
    submit = SubmitField('Log in')


class PasswordChangeForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired(), length(min=6)])
    new_password = PasswordField('New Password', validators=[DataRequired(), length(min=6)])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), length(min=6)])
    change_password = SubmitField('Change Password')


class AvailableBusesForm(FlaskForm):
    departure = StringField('Departure', validators=[DataRequired()])
    destination = StringField('Destination', validators=[DataRequired()])
    bus_name = StringField('Bus Name', validators=[DataRequired()])
    bus_picture = FileField('Bus Photo', validators=[DataRequired()])
    departure_date = DateField('Departure Date', format='%Y-%m-%d', validators=[DataRequired()])
    departure_time = StringField('Departure Time', validators=[DataRequired()])
    arrival_time = StringField('Arrival Time', validators=[DataRequired()])
    price = StringField('Price', validators=[DataRequired()])
    flash_sale = BooleanField('Flash Sale')

    submit = SubmitField('Search Bus')
    add_bus = SubmitField('Add Bus')
    update_bus = SubmitField('Update')


class OrderForm(FlaskForm):
    order_status = SelectField('Order Status', choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'),
                                                        ('Out for delivery', 'Out for delivery'),
                                                        ('Delivered', 'Delivered'), ('Canceled', 'Canceled')])

    update = SubmitField('Update Status')
    

class UpdateForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired(), length(min=2)])
    password1 = PasswordField('Enter Your Password', validators=[DataRequired(), length(min=6)])
    password2 = PasswordField('Confirm Your Password', validators=[DataRequired(), length(min=6)])
    picture = FileField('Change Profile picture')
    submit = SubmitField('Update')
    
class PaymentForm(FlaskForm):
    bank_name = StringField('Bank Name', validators=[DataRequired()])
    bank_logo = FileField('Bank Logo', validators=[DataRequired()])
    # Add other fields as needed
    submit = SubmitField('Submit')
    add_payment = SubmitField('Add')