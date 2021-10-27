from flask import render_template

from Booking import app
from Booking.models import User, Offer, Guide, Arrangement
from Booking.forms import signInForm, logInForm

# http://localhost:5000/
@app.route('/', methods=['GET'])
def index():
    allOffers = Offer.query.all()
    return render_template('index.html', offers=allOffers)


# http://localhost:5000/signIn
# adding new user in base
@app.route('/signIn', methods=['GET'])
def signIn_page():
    form = signInForm()
    return render_template('signIn.html', form=form)


# http://localhost:5000/logIn
# user already have account
@app.route('/logIn', methods=['GET'])
def logIn_page():
    form = logInForm()
    return render_template('logIn.html', form=form)


# http://localhost:5000/allusers
@app.route('/allusers', methods=['GET'])
def allUsers_page():
    users = User.query.all()
    if len(users) > 0:
        return "I have all users here"
    else:
        return "Fail!"