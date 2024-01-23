
from flask import Flask, render_template, url_for, redirect, request, session
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from passlib.hash import pbkdf2_sha256
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://jsier:password@localhost:3306/hlhdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app,db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(100), unique = True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    date_joined = db.Column(db.Date, default=datetime.utcnow)

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/home1')
def home1():
    return render_template('home1.html')
@app.route('/home2')
def home2():
    return render_template('home2.html')
@app.route('/home3')
def home3():
    return render_template('home3.html')
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
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username = username).first()

        if user and check_password_hash(user.password, password):
            session['username'] = user.username
            return redirect(url_for('index'))
        else:
            pass #handle login failure

    return render_template('login.html')

@app.route('/profile', methods = ['GET', 'POST'])
def profile():
    return render_template('profile.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
