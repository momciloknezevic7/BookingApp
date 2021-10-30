from flask import render_template, url_for, redirect
from flask_login import login_user, logout_user, current_user
from flask_user import roles_required, UserManager

from Booking import app, db, bcrypt
from Booking.models import User, Offer, Guide, Arrangement, Request
from Booking.forms import signInForm, logInForm, newOfferForm

user_manager = UserManager(app, db, User)

# http://localhost:5000/
@app.route('/', methods=['GET'])
def index():
    allOffers = Offer.query.all()
    return render_template('index.html', offers=allOffers)


# http://localhost:5000/signIn
# Adding new user in base
# Need POST method because of SignIn process
@app.route('/signIn', methods=['GET', 'POST'])
def signIn_page():
    form = signInForm()

    # Input validation
    usernameCheck = form.uniqueUsernameCheck(form.username.data)
    if form.validate_on_submit() and usernameCheck:
        newUser = User(
            username=form.username.data,
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            password=form.password.data,
            wanted_role=form.wanted_role.data
        )

        db.session.add(newUser)
        db.session.commit()

        # Role Admin and Travel Guide need to be approved by other admin user
        if form.wanted_role.data != 'Tourist':
            newRequest = Request(form.username.data)
            db.session.add(newRequest)
            db.session.commit()

        return redirect(url_for('fullOfferInfo_page'))
    else:
        for error_value in form.errors.values():
            print(f'SignIn problem: {error_value}')

        if not usernameCheck:
            print("UNIQUE CHECK: This username already exists!")
            form.username.data = ""

        return render_template('signIn.html', form=form)


# http://localhost:5000/logIn
# User already have account
@app.route('/logIn', methods=['GET', 'POST'])
def logIn_page():
    form = logInForm()

    # Input validation
    if form.validate_on_submit():
        # if user exist
        tmpUser = User.query.filter_by(username=form.username.data).first()

        # is password correct for that username
        real_password = tmpUser.password_hash
        input_password = form.password.data
        check_password = bcrypt.check_password_hash(real_password, input_password)

        if tmpUser and check_password:
            login_user(tmpUser)
            print("Welcome back " + tmpUser.username)
            return redirect(url_for('fullOfferInfo_page'))
        else:
            print("CHECK: Wrong password or username")
            return render_template('logIn.html', form=form)
    else:
        print("LogIn: Validation failed!")
        return render_template('logIn.html', form=form)


# 'Page' for logging out
@app.route('/logout')
def logOut_function():
    print(f"INFO: Current user {current_user.username} is logged out!")
    logout_user()
    return redirect(url_for('index'))

@app.route('/fullOfferInfo', methods=['GET'])
def fullOfferInfo_page():
    # TODO create new html page with all infos
    return redirect(url_for('index'))

@app.route('/allTouristPossibilities')
@roles_required('Tourist')
def touristPossibilities_page():
    return render_template('tourist.html')

@app.route('/allAdminPossibilities')
@roles_required('Admin')
def adminPossibilities_page():
    return render_template('admin.html')

@app.route('/allGuidePossibilities')
@roles_required('Travel Guide')
def guidePossibilities_page():
    return render_template('guide.html')


# http://localhost:5000/allusers
@app.route('/allusers', methods=['GET'])
def allUsers_page():
    users = User.query.all()
    if len(users) > 0:
        return "I have all users here"
    else:
        return "Fail!"

#----------------------------------------
def checkWhoIsAvailable(allTravelGuids, startDate, endDate):
    return allTravelGuids

@app.route('/createNewOffer', methods=['GET', 'POST'])
@roles_required('Admin')
def createNewOffer_page():
    form = newOfferForm()

    # Input validation
    if form.validate_on_submit():

        newOffer = Offer(
            startDate=form.start.data,
            endDate=form.end.data,
            description=form.description.data,
            destination=form.destination.data,
            numOfPlaces=form.numOfPlaces.data,
            price=form.price.data,
            userWhoCreated=current_user.username,
        )

        db.session.add(newOffer)
        db.session.commit()

        return redirect(url_for('adminPossibilities_page'))
    else:
        for error_value in form.errors.values():
            print(f'NewOffer problem: {error_value}')

        return render_template('createNewOffer.html', form=form)

