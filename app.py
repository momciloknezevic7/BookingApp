from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://momcilo:momcilo@localhost/bookinguser'
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'bookingUser'
    username = db.Column(db.String(50), primary_key = True)
    name = db.Column(db.String(30), nullable = False)
    surname = db.Column(db.String(30), nullable = False)
    email = db.Column(db.String(30), nullable = False)
    password = db.Column(db.String(50), nullable = False)
    role = db.Column(db.String(50), nullable = False)

    def __init__(self, username, name, surname, email, password, role):
        self.username = username
        self.name = name
        self.surname = surname
        self.email = email
        self.password = password
        self.role = role

    def __repr__(self):
        return f'New User: {self.username}'


# function for home page
@app.route('/')
def index():
    return "Home page!"


if __name__ == "__main__":
    app.run(debug=True)