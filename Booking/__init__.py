from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://momcilo:momcilo@localhost/bookinguser'
db = SQLAlchemy(app)

from Booking import routes