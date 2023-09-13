from flask import Flask, render_template

app = Flask(__name__)

#default route and route function returning the main screen (index)

@app.route('/home')
@app.route('/')
def index():
    return render_template('index.html')

#interpreter automatically gives main as the name. If another module is used, this may not run
if __name__ == '__main__':
    app.run(debug=True)
    