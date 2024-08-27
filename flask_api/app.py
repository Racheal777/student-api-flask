from  flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return "<p>Hello, Racheal, This is Flask for you!</p>"


@app.route('/greeting/<name>')
def introduce(name):
    return f"Hi I am {name}. Welcome to Today's class"

@app.route('/square/<int:number>')
def square(number):
    return f" number {number} square is {number** 2}"