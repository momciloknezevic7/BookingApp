from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://momcilo:momcilo@localhost/bookinguser'

# Need SECRET_KEY for Flask Forms
# os.urandom(24).hex()
app.config['SECRET_KEY'] = '027571c11e7cbd3a680b0820e3cef67067a672503e577ed4'

app.config['USER_ENABLE_EMAIL'] = False
app.config['USER_EMAIL_SENDER_EMAIL'] = 'moma.knezevic7@gmail.com'

db = SQLAlchemy(app)

# For hashing password
bcrypt = Bcrypt(app)

# For authentication
# Name is from documentation
login_manager = LoginManager(app)

from Booking import routes