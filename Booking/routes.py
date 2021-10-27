from flask import render_template, url_for, redirect

from Booking import app
from Booking.models import User, Offer, Guide, Arrangement
from Booking.forms import signInForm, logInForm
from Booking import db

# http://localhost:5000/
@app.route('/', methods=['GET'])
def index():
    allOffers = Offer.query.all()
    return render_template('index.html', offers=allOffers)


# http://localhost:5000/signIn
# adding new user in base
# Need POST method because of SignIn process
@app.route('/signIn', methods=['GET', 'POST'])
def signIn_page():
    form = signInForm()

    # Input validation
    usernameCheck = uniqueUsernameCheck(form.username.data)
    if form.validate_on_submit() and usernameCheck:
        newUser = User(
            username=form.username.data,
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            password=form.password.data,
            wanted_role=form.wanted_role.data
        )

        # TODO if wanted_role != 'Tourist' => need to send request to admin(new column in table Requests)

        db.session.add(newUser)
        db.session.commit()
        return redirect(url_for('fullOfferInfo_page'))
    else:
        for error_value in form.errors.values():
            print(f'SignIn problem: {error_value}')

        if not usernameCheck:
            print("UNIQUE CHECK: This username already exists!")
            form.username.data = ""

        return render_template('signIn.html', form=form)


def uniqueUsernameCheck(inputUsername):
    if User.query.filter_by(username = inputUsername).first():
        return False
    else:
        return True


# http://localhost:5000/logIn
# user already have account
@app.route('/logIn', methods=['GET'])
def logIn_page():
    form = logInForm()
    return render_template('logIn.html', form=form)


@app.route('/fullOfferInfo', methods=['GET'])
def fullOfferInfo_page():
    # TODO create new html page with all infos
    return redirect(url_for('index'))


# http://localhost:5000/allusers
@app.route('/allusers', methods=['GET'])
def allUsers_page():
    users = User.query.all()
    if len(users) > 0:
        return "I have all users here"
    else:
        return "Fail!"