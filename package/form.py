from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, DateField, SubmitField, FileField
from wtforms.validators import DataRequired, Length, Email, length



class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), length(min=3)])
    email = EmailField('Email', validators=[DataRequired()])
    password1 = PasswordField('Enter your password', validators=[DataRequired(), length(min=5)])
    password2 = PasswordField('Confirm your password', validators=[DataRequired(), length(min=5)])
    submit = SubmitField('Sign up')
    
class LoginForm(FlaskForm):
    username_or_email = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Enter your password', validators=[DataRequired(), length(min=6)])
    submit = SubmitField('Log in')
    
class PasswordChangeForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired(), length(min=6)])
    new_password = PasswordField('New Password', validators=[DataRequired(), length(min=6)])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), length(min=6)])
    change_password = SubmitField('Change Password')
    
class EmailChangeForm(FlaskForm):
    new_email = StringField('New Email', validators=[DataRequired(), Email(), Length(min=6)])
    change_email = SubmitField('Change Email')
    
    
class AddBusForm(FlaskForm):
    bus_type = StringField('Bus Type', validators=[DataRequired()])
    side_number = StringField('Side number', validators=[DataRequired()])
    bus_picture = FileField('Bus Photo')#, validators=[DataRequired()])
    submit = SubmitField('Add Bus')
    
    
class AddScheduleForm(FlaskForm):
    departure = StringField('Departure', validators=[DataRequired()])
    destination = StringField('Destination', validators=[DataRequired()])
    departure_date = DateField('Departure Date', format='%Y-%m-%d', validators=[DataRequired()])
    departure_time = StringField('Departure Time', validators=[DataRequired()])
    arrival_time = StringField('Arrival Time', validators=[DataRequired()])
    price = StringField('Price', validators=[DataRequired()])
    travel_packages = StringField('Travel packages')
    submit = SubmitField('Search Bus')
    add_schedule = SubmitField('Add Schedule')
    update_schedule = SubmitField('Update')
    
    
class PaymentForm(FlaskForm):
    bank_name = StringField('Bank Name', validators=[DataRequired()])
    bank_logo = FileField('Bank Logo', validators=[DataRequired()])

    submit = SubmitField('Submit')
    add_payment = SubmitField('Add')
