from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, validators


# Form for creating new account
class signInForm(FlaskForm):
    name = StringField(label='Name:', validators=[validators.required(), validators.length(max=30)])
    surname = StringField(label='Surname:', validators=[validators.required(), validators.length(max=30)])
    email = StringField(label='Email:', validators=[validators.required(), validators.length(max=30), validators.email()])
    username = StringField(label='Username:', validators=[validators.required(), validators.length(max=50)])
    password = PasswordField(label='Password:', validators=[validators.required()])
    password_val = PasswordField(label='Confirm Password:', validators=[validators.required()])
    role = SelectField(label="Role:", default='Tourist', choices=[('Tourist', 'Tourist'),
                                                                 ('Admin', 'Admin'),
                                                                 ('Travel Guide', 'Travel Guide')
                                                                ],
                       validators=[validators.required()]
                       )
    submit = SubmitField(label='Create new account')


# Form for user who already have account
class logInForm(FlaskForm):
    username = StringField(label='Username:', validators=[validators.required(), validators.length(max=50)])
    password = PasswordField(label='Password:', validators=[validators.required()])
    submit = SubmitField(label='Log In with existing account')