from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin


app = Flask(__name__)
db = SQLAlchemy(app) #creates the database instance
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db' #connects app file to db file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisisasecretkey'



#table for the database with id column, username column, and password column
class User(db.model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False) #max of 20 characters
    password = db.Column(db.String(80), nullable=False) #max of 80 characters after hash



#default route and route function returning the main screen (index)
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

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/login')
def login():
    return render_template('login.html')

#interpreter automatically gives main as the name. If another module is used, this may not run
if __name__ == '__main__':
    app.run(debug=True) #automatically detects changes
    
