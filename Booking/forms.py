from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, validators, DateField, IntegerField, FloatField

from Booking.models import User

# Form for creating new account
class signInForm(FlaskForm):
    name = StringField(label='Name:', validators=[validators.InputRequired() , validators.length(max=30)])
    surname = StringField(label='Surname:', validators=[validators.InputRequired(), validators.length(max=30)])
    email = StringField(label='Email:', validators=[validators.InputRequired(), validators.length(max=30), validators.email()])
    username = StringField(label='Username:', validators=[validators.InputRequired(), validators.length(max=50)])
    password = PasswordField(label='Password:', validators=[validators.InputRequired()])
    password_val = PasswordField(label='Confirm Password:', validators=[validators.InputRequired(), validators.EqualTo('password')])
    wanted_role = SelectField(label="Role:", default='Tourist', choices=[('Tourist', 'Tourist'),
                                                                 ('Admin', 'Admin'),
                                                                 ('Travel Guide', 'Travel Guide')
                                                                ],
                       validators=[validators.InputRequired()]
                       )
    submit = SubmitField(label='Create new account')

    def uniqueUsernameCheck(self, inputUsername):
        if User.query.filter_by(username=inputUsername).first():
            return False
        else:
            return True


# Form for user who already have account
class logInForm(FlaskForm):
    username = StringField(label='Username:', validators=[validators.InputRequired(), validators.length(max=50)])
    password = PasswordField(label='Password:', validators=[validators.InputRequired()])
    submit = SubmitField(label='Log In with existing account')


# Form for admin who can create new arrangement
class newOfferForm(FlaskForm):
    start = DateField(label='StartDate:', validators=[validators.InputRequired()])
    end = DateField(label='EndDate:', validators=[validators.InputRequired()])
    description = StringField(label='Description:', validators=[validators.InputRequired(), validators.length(max=200)])
    destination = StringField(label='Destination:', validators=[validators.InputRequired(), validators.length(max=100)])
    numOfPlaces = IntegerField(label='Number of Places:', validators=[validators.InputRequired(), validators.NumberRange(min=1, max=1000)])
    price = FloatField(label='Price:', validators=[validators.InputRequired()])
    guideId = IntegerField(label='Guide ID:')

    submit = SubmitField(label='Create Offer')
