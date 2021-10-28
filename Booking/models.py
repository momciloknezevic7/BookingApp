from Booking import db, bcrypt, login_manager
from datetime import datetime
from flask_login import UserMixin

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

# https://flask-login.readthedocs.io/en/latest/#how-it-works
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# Need to inherit UserMixin because of some necessary function implementation( is_authenticated, is_active, is_anonymous, get_id)
class User(db.Model, UserMixin):
    __tablename__ = 'bookingUser'
    username = db.Column(db.String(50), primary_key = True)
    name = db.Column(db.String(30), nullable = False)
    surname = db.Column(db.String(30), nullable = False)
    email = db.Column(db.String(30), nullable = False)
    password_hash = db.Column(db.String(60), nullable = False)
    # Role that user want when he Sign In
    wanted_role = db.Column(db.String(50), nullable = False)
    # Role that administrator approved for this user after his request( need for Admin and Tourist Guide role)
    real_role = db.Column(db.String(50))


    createdOffers = db.relationship("Offer", backref = "offerCreator", lazy = True)

    # Arrangements that this user made
    madeArrangement = db.relationship("Arrangement", backref = "userWhoReserved", lazy = True )

    def __init__(self, username, name, surname, email, password, wanted_role):
        self.username = username
        self.name = name
        self.surname = surname
        self.email = email
        self.password_hash = self.hashing_password(password)
        self.wanted_role = wanted_role
        # Until approved by the administrator
        self.real_role = 'Tourist'

    def __repr__(self):
        return f'New User: {self.username}'

    # rounds is the number that dictates the 'slowness' and slow is desirable here
    # Recommendation: The process of hashing should take approximately one second => between 12 and 14 rounds
    def hashing_password(self, password_raw):
        return bcrypt.generate_password_hash(password_raw, rounds=14).decode('utf-8')

    # Need to override this method because in User I don't have id like field
    def get_id(self):
        return self.username


class Offer(db.Model):
    __tablename__ = 'bookingOffer'
    id = db.Column(db.Integer(), primary_key = True)
    startDate = db.Column(db.DateTime, nullable = False)
    endDate = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    destination = db.Column(db.String(100), nullable = False)
    numOfPlaces = db.Column(db.Integer(), nullable=False)
    numOfAvailablePlaces = db.Column(db.Integer())
    price = db.Column(db.Float(), nullable = False)
    creationDate = db.Column(db.DateTime, default = datetime.utcnow())

    userWhoCreated = db.Column(db.String(), db.ForeignKey('bookingUser.username'))

    # Arrangements that made for this offer
    madeArrangements = db.relationship("Arrangement", backref = "offerForThisArrangement", lazy = True )

    def __init__(self, startDate, endDate, description, destination, numOfPlaces, price, userWhoCreated):
        self.startDate = startDate
        self.endDate = endDate
        self.description = description
        self.destination = destination
        self.numOfPlaces = numOfPlaces
        # numOfAvailablePlaces will reduce after making arrangements for this offer
        self.numOfAvailablePlaces = numOfPlaces
        self.price = price
        self.creationDate = datetime.utcnow()
        self.userWhoCreated = userWhoCreated

    def __repr__(self):
        return f'New Offer: {self.id}'


class Guide(db.Model):
    __tablename__ = 'touristGuide'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    surname = db.Column(db.String(30), nullable=False)

    # Arrangements where this guide will work
    madeArrangements = db.relationship("Arrangement", backref = "guideForThisArrangement", lazy = True )

    def __init__(self, name, surname):
        self.name = name
        self.surname = surname

    def __repr__(self):
        return f'New Guide: {self.id}'


class Arrangement(db.Model):
    __tablename__ = 'bookingArrangement'
    id = db.Column(db.Integer(), primary_key = True)
    numOfReservedPlaces = db.Column(db.Integer(), nullable=False)

    usernameForReservation = db.Column(db.String(), db.ForeignKey('bookingUser.username'))
    offerId = db.Column(db.Integer(), db.ForeignKey('bookingOffer.id'))
    guideId = db.Column(db.Integer(), db.ForeignKey('touristGuide.id'))

    def __init__(self, numOfReservedPlaces):
        self.numOfReservedPlaces = numOfReservedPlaces

    def __repr__(self):
        return f'New Arrangement: {self.id}'