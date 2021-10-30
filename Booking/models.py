from Booking import db, bcrypt, login_manager

from datetime import date
from flask_user import UserMixin, roles_required
import smtplib
from email.message import EmailMessage

'''
Relations:
    One-to-Many:
        One User can create Many Offers
        One User can make Many Arrangements
        
        One Offer can have Many Arrangements
        
        One Guide can work on Many Arrangements
        
    Every Arrangment can have only one User, Offer and Guide
'''

'''
For rebuild the base:
from Booking import db
db.drop_all()
db.create_all()
'''


# Need to inherit UserMixin because of some necessary function implementation( is_authenticated, is_active, is_anonymous, get_id)
class User(db.Model, UserMixin):
    __tablename__ = 'bookingUser'
    username = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    surname = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    # Role that user want when he Sign In
    wanted_role = db.Column(db.String(50), nullable=False)
    # Role that administrator approved for this user after his request( need for Admin and Tourist Guide role)
    real_role = db.Column(db.String(50))

    # Offers that this user created
    createdOffers = db.relationship("Offer", backref="offerCreator", lazy=True)

    # Arrangements that this user made
    madeArrangement = db.relationship("Arrangement", backref="userWhoReserved", lazy=True )

    # Field I will you for connecting with roles that I use for authorization
    # secondary argument indicate association table(User JOIN Role)
    # NOTE: wanted_role and real_role don't have direct link with this field
    roles = db.relationship("Role", secondary='user_roles')

    # All role requests for this user (when user sign In or later if user want to upgrade his role)
    requests = db.relationship("Request", backref="requestMaker", lazy=True)


    def __init__(self, username, name, surname, email, password, wanted_role):
        self.username = username
        self.name = name
        self.surname = surname
        self.email = email
        self.password_hash = self.hashing_password(password)
        self.wanted_role = wanted_role
        # Until wanted_role is not approved by admin
        self.real_role = 'Tourist'
        # By default everyone is Tourist in the beginning
        self.roles = [db.session.query(Role).filter_by(name="Tourist").first()]

    def __repr__(self):
        return f'New User: {self.username}'

    # rounds is the number that dictates the 'slowness' and slow is desirable here
    # Recommendation: The process of hashing should take approximately one second => between 12 and 14 rounds
    def hashing_password(self, password_raw):
        return bcrypt.generate_password_hash(password_raw, rounds=14).decode('utf-8')

    # Need to override this method because in User I don't have id like field
    def get_id(self):
        return self.username

    # Because of authorization, I need to have id property with name 'id'
    # For my User, that is username
    @property
    def id(self):
        # getter
        return self.username

    @id.setter
    def id(self, value):
        # setter
        self.username = value

    # Necessary function for authorization
    def get_user_by_token(token):
        return User.query.get(token)

    # Admin needs insight in role request list
    # TODO check does exist some criteria from approval
    # @role_required('Admin')
    # List of requests => Admin want to approve it => tmpRequest.approveThisRequest(self.username)

    # Approving role request for this user
    def approveRequest(self):
        self.real_role = self.wanted_role
        self.roles = [db.session.query(Role).filter_by(name=self.wanted_role).first()]


# https://flask-login.readthedocs.io/en/latest/#how-it-works
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)



# Tables for authorization: User, Role and association table UserRoles
class Role(db.Model):
    '''
    id | name
    -----------------
    1  | Tourist
    2  | Admin
    3  | Travel Guide
    '''
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __init__(self, name):
        self.name = name


class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('bookingUser.username', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))


class Offer(db.Model):
    __tablename__ = 'bookingOffer'
    id = db.Column(db.Integer(), primary_key=True)
    startDate = db.Column(db.Date, nullable=False)
    endDate = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    numOfPlaces = db.Column(db.Integer(), nullable=False)
    numOfAvailablePlaces = db.Column(db.Integer())
    price = db.Column(db.Float(), nullable=False)
    creationDate = db.Column(db.Date, default=date.today())

    userWhoCreated = db.Column(db.String(), db.ForeignKey('bookingUser.username'))

    # Guide who will work on arrangement
    guideId = db.Column(db.Integer(), db.ForeignKey('travelGuide.id'), nullable=True)

    # Arrangements that made for this offer
    madeArrangements = db.relationship("Arrangement", backref="offerForThisArrangement", lazy=True )

    def __init__(self, startDate, endDate, description, destination, numOfPlaces, price, userWhoCreated):
        self.startDate = startDate
        self.endDate = endDate
        self.description = description
        self.destination = destination
        self.numOfPlaces = numOfPlaces
        # numOfAvailablePlaces will reduce after making arrangements for this offer
        self.numOfAvailablePlaces = numOfPlaces
        self.price = price
        self.creationDate = date.today()
        self.userWhoCreated = userWhoCreated

    def setGuideForThisOffer(self, guideId):
        self.guideId = guideId

    def __repr__(self):
        return f'New Offer: {self.id}'


class Guide(db.Model):
    __tablename__ = 'travelGuide'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    surname = db.Column(db.String(30), nullable=False)

    # Offers where this guide will work
    madeOffers = db.relationship("Offer", backref="guideForThisOffer", lazy=True)

    def __init__(self, name, surname):
        self.name = name
        self.surname = surname
        # List of offer's id
        self.madeArrangements = []

    def __repr__(self):
        return f'New Guide: {self.id}'


class Arrangement(db.Model):
    __tablename__ = 'bookingArrangement'
    id = db.Column(db.Integer(), primary_key=True)
    numOfReservedPlaces = db.Column(db.Integer(), nullable=False)

    usernameForReservation = db.Column(db.String(), db.ForeignKey('bookingUser.username'))
    offerId = db.Column(db.Integer(), db.ForeignKey('bookingOffer.id'))

    def __init__(self, numOfReservedPlaces):
        self.numOfReservedPlaces = numOfReservedPlaces

    def __repr__(self):
        return f'New Arrangement: {self.id}'


# Requests submitted by new users for higher role(Admin, Travel Guide)
class Request(db.Model):
    __tablename__ = 'request'
    id = db.Column(db.Integer(), primary_key=True)
    newUserUsername = db.Column(db.String(50), db.ForeignKey('bookingUser.username'))
    status = db.Column(db.String(20), nullable=False)
    comment = db.Column(db.String(500), nullable=True)
    adminUsername = db.Column(db.String(50), nullable=True)

    def __init__(self, newUserUsername):
        self.newUserUsername = newUserUsername
        self.status = 'Pending'

    #@roles_required('Admin') # TODO Check is this line necessary here or only in routes before url where I will call this method
    def solveThisRequest(self, result, adminUsername, *comment):
        '''
        result:
            True  => Approved
            False => Rejected
        '''
        try:
            newUser = User.query.filter_by(username=self.newUserUsername).first()

            if result:
                newUser.approveRequest()
                self.status = 'Approved'
            else:
                # Nothing changes in newUser, real_role and roles are already set on 'Tourist' (by default)
                self.status = 'Rejected'
                if len(comment) == 0:
                    raise "You need to give explanation for rejecting!"
                else:
                    self.comment = comment[0]

            self.sendEmailToUser(newUser, result)
            self.adminUsername = adminUsername
        except:
            return "Error with solving request!"


    def sendEmailToUser(self, newUser, result):
        # Preparations from sending email
        emailText = "Dear " + newUser.name + ", your request for role " \
                    + newUser.wanted_role + " is " + self.status.lower() + "!"
        if not result:
            emailText += "\nExplanation: " + self.comment

        emailMessage = EmailMessage()
        emailMessage.set_content(emailText)
        emailMessage['Subject'] = "Role Request on BookingApp"
        emailMessage['From'] = "bookingAppAdmins@gmail.com"
        emailMessage['To'] = newUser.email

        # Sending email
        # Gmail SMTP port (SSL): 465
        # Gmail SMTP server address: smtp.gmail.com
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            '''
            This isn't real gmail, but this code is successfully tested with real one.
            First argument is GmailID(part before @ in gmail address)
            Second argument is password for that gmail
            '''
            smtp.login('bookingAppAdmins', 'password')
            smtp.send_message(emailMessage)