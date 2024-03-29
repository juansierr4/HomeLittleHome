from flask import Flask, render_template, url_for, redirect, request, session
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from passlib.hash import pbkdf2_sha256
from flask_migrate import Migrate
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from flask_mail import Mail, Message
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key= 'Hiq1qOTgPpYDdQv4fScNcA'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:45#Kangaroo@35.203.175.67/hlhdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure Flask-Mail to use Gmail's SMTP server
app.config['MAIL_SERVER'] = 'smtp.office365.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'jwall156@hotmail.com'
app.config['MAIL_PASSWORD'] = '3#Arrancapedos'
app.config['MAIL_DEFAULT_SENDER'] = 'jwall156@hotmail.com'


db = SQLAlchemy(app)
migrate = Migrate(app,db)
mail = Mail(app)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(100), unique = True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    date_joined = db.Column(db.DateTime, default=func.current_date())

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    home_booked = db.Column(db.String(10), nullable=False)
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    guests = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    home_id = db.Column(db.Integer, db.ForeignKey('home.id'), nullable=False)
    home = db.relationship('Home', back_populates='bookings')

    def __repr__(self):
        return f'<Booking {self.id}>'
    
class Home(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), unique=True, nullable=False)
    bookings = db.relationship('Booking', back_populates='home')

available_homes = [
    {'id':1, 'name':'Home 1'},
    {'id':2, 'name':'Home 2'},
    {'id':3, 'name':'Home 3'},
]

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/home1')
def home1():
    return render_template('home1.html', available_homes=available_homes)
@app.route('/home2')
def home2():
    return render_template('home2.html', available_homes=available_homes)
@app.route('/home3')
def home3():
    return render_template('home3.html', available_homes=available_homes)
@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        hashed_password = pbkdf2_sha256.hash(password)

        new_user = User(username = username, email = email, password = hashed_password)

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('signup.html')
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_field = request.form['login']  # 'login' can be either username or email
        password = request.form['password']

        # Attempt to find the user by username or email
        user = User.query.filter((User.username == login_field) | (User.email == login_field)).first()

        if user and pbkdf2_sha256.verify(password, user.password):
            session['username'] = user.username
            return redirect(url_for('index'))
        else:
            # Handle login failure
            return "Invalid username/email or password", 401

    return render_template('login.html')

@app.route('/profile', methods = ['GET', 'POST'])
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    user = User.query.filter_by(username = session['username']).first()

    if user:
        #fetch the user's bookings
        bookings = db.session.query(Booking, Home).join(Home).filter(Booking.user_id == user.id).all()
        return render_template('profile.html', user=user, bookings=bookings)
    else:
        return 'You must be loggeed in to view your profile'
    
@app.route('/booking_appointment', methods=['POST'])
def book_appointment():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    user = User.query.filter_by(username=session['username']).first()

    if user:
        check_in = request.form['checkin']
        check_out = request.form['checkout']
        guests = int(request.form['guests'])
        home_booked = request.form['home_booked']
        check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
        check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()

        home = Home.query.filter_by(name=home_booked).first()

        if home is not None:
            new_booking = Booking(
                user_id=user.id,
                check_in=check_in_date,
                check_out=check_out_date,
                guests=guests,
                home_booked=home_booked,
                home_id=home.id
            )

            db.session.add(new_booking)
            db.session.commit()

            # Send email to the user
            send_mail("Booking Confirmation", user.email, f"Your booking for {home_booked} from {check_in} to {check_out} is confirmed.")

            # Send email to the owner
            send_mail("New Booking Notification", "jwall156@hotmail.com", f"A new booking for {home_booked} from {check_in} to {check_out} has been made.")

            return redirect(url_for('confirmation', booking_id=new_booking.id))
        else:
            return 'Invalid home selected'
    else:
        return 'You must be logged in to book an appointment'

@app.route('/confirmation/<int:booking_id>')
def confirmation(booking_id):
    # Ensure the user is logged in and has access to this booking
    if 'username' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session['username']).first()

    if not user:
        return redirect(url_for('login'))

    # Get the booking and the corresponding home details
    booking = Booking.query.get(booking_id)
    home = Home.query.get(booking.home_id) if booking else None

    # Check if the booking exists and belongs to the logged-in user
    if booking and booking.user_id == user.id:
        # Render the booking confirmation page with booking and home details
        return render_template('confirmation.html', booking=booking, home=home)
    else:
        # If booking does not exist or does not belong to user, redirect to index
        return redirect(url_for('index'))

@app.route('/delete_booking/<int:booking_id>', methods=['POST'])
def delete_booking(booking_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(username=session['username']).first()
    if user:
        booking = Booking.query.filter_by(id=booking_id, user_id=user.id).first()
        if booking:
            #deletes
            db.session.delete(booking)
            db.session.commit()
            return redirect(url_for('profile'))
        else:
            return 'Booking not found or you do not have permission to delete it'
    else:
        return 'You must be logged in to delete a booking'

@app.route('/logout')
def logout():
    session.pop('username',None)
    return redirect(url_for('login'))


@app.route('/send_mail')
def send_mail(subject, recipient, body):
    msg = Message(subject, recipients=[recipient])
    msg.body = body
    mail.send(msg)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
