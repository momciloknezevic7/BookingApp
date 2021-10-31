from flask import render_template, url_for, redirect, request
from flask_login import login_user, logout_user, current_user
from flask_user import roles_required, UserManager
from datetime import date, datetime
import smtplib
from email.message import EmailMessage

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

        return redirect(url_for('index'))
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
            return redirect(url_for('index'))
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
# TODO
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

@app.route('/modifyOffer', methods=['GET', 'POST'])
@roles_required('Admin')
def modifyOffer_page():
    allOffers = Offer.query.all()

    return render_template('modifyOffer.html', offers=allOffers)

@app.route('/updateOffer/<int:id>', methods=['GET', 'POST'])
def updateOffer_page(id):
    offerToUpdate = Offer.query.get(id)

    if request.method == 'POST':
        offerToUpdate.startDate = datetime.strptime(request.form['startDate'], '%Y-%m-%d').date()
        offerToUpdate.endDate = datetime.strptime(request.form['endDate'], '%Y-%m-%d').date()
        offerToUpdate.description = request.form['description']
        offerToUpdate.destination = request.form['destination']
        offerToUpdate.numOfPlaces = request.form['numOfPlaces']
        offerToUpdate.price = request.form['price']

        try:
            if (offerToUpdate.getStartDate()-date.today()).days > 5:
                db.session.commit()
                return redirect(url_for('adminPossibilities_page'))
            else:
                print("You are late! Can't update this offer anymore!")
        except Exception as ex:
            print(ex)
            print("Error: Problem with update option!")
            return render_template('updateOffer.html', offerToUpdate=offerToUpdate)
    else:
        # GET method
        return render_template('updateOffer.html', offerToUpdate=offerToUpdate)


def sendMail(username):
    user = User.query.filter_by(username=username).first()

    # Preparations from sending email
    emailText = "Dear " + user.name + ", offer where you have arrangement is canceled!"

    emailMessage = EmailMessage()
    emailMessage.set_content(emailText)
    emailMessage['Subject'] = "Your arrangement failed on BookingApp"
    emailMessage['From'] = "bookingAppAdmins@gmail.com"
    emailMessage['To'] = user.email

    # Sending email
    # Gmail SMTP port (SSL): 465
    # Gmail SMTP server address: smtp.gmail.com
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        '''
        This isn't real gmail address, but this code is successfully tested with real one.
        First argument is GmailID(part before @ in gmail address)
        Second argument is password for that gmail
        '''
        #smtp.login('bookingAppAdmins', 'password')
        smtp.send_message(emailMessage)


def sendMailToAllTourist(allTouristsForThisOffer):
    for touristUsername in allTouristsForThisOffer:
        sendMail(touristUsername)


@app.route('/deleteOffer/<int:id>')
def deleteOffer_page(id):
    offerToDelete = Offer.query.get(id)

    allTouristsForThisOffer = []
    allArrangementForThisOffer = offerToDelete.getMadeArrangements()
    for arr in allArrangementForThisOffer:
        allTouristsForThisOffer.append(arr.getUsernameForReservation())

    try:
        if (offerToDelete.getStartDate()-date.today()).days > 5:
            # Sending mail to every tourist who have arrangement for this offer
            sendMailToAllTourist(allTouristsForThisOffer)
            db.session.delete(offerToDelete)
            db.session.commit()
            return redirect(url_for('adminPossibilities_page'))
        else:
            print("You are late! Can't delete this offer anymore!")
            return redirect(url_for('modifyOffer_page'))
    except Exception as ex:
        print(ex)
        print("Error: Problem with delete option!")
        return redirect(url_for('modifyOffer_page'))


@app.route('/fullOffersInfo/<string:filter>', methods=['GET'])
def fullOffersInfo_page(filter):

    if filter == "all":
        allOffers = Offer.query.all()
        return render_template('fullOffersInfo.html', offers=allOffers)
    elif filter == "my":
        myOffers = Offer.query.filter_by(userWhoCreated=current_user.username)
        return render_template('fullOffersInfo.html', offers=myOffers)

