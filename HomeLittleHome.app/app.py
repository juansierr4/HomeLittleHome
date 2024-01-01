
from flask import Flask, render_template, url_for
from datetime import timedelta
#from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://Users/jsier/Desktop/homelittlehome/og_database.db'


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
#if __name__ == '__main__':
    #with app.app_context():
       #db.create_all()
#app.run(debug=True) #automatically detects changes
    
