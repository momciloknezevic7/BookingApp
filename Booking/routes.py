from Booking import app
from Booking.models import User

# http://localhost:5000/
@app.route('/')
def index():
    return "Home page!"

# http://localhost:5000/allusers
@app.route('/allusers', methods = ['GET'])
def allUsers_page():
    users = User.query.all()
    if len(users) > 0:
        return "I have all users here"
    else:
        return "Fail!"