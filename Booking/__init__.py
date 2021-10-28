from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://momcilo:momcilo@localhost/bookinguser'

# Need SECRET_KEY for Flask Forms
# os.urandom(12).hex()
app.config['SECRET_KEY'] = '099659d6f2cce803c9c0ee8c'

db = SQLAlchemy(app)

# For hashing password
bcrypt = Bcrypt(app)

# For authentication
# Name is from documentation
login_manager = LoginManager(app)

from Booking import routes