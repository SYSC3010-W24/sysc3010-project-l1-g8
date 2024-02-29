from flask import Flask
from flask import request
from markupsafe import escape
from flask import render_template


app = Flask(__name__)

@app.route('/')
def index(name=None):
    return render_template('index.html', name=name)



@app.route('/<name>')
def settings(name='settings'):
    return render_template('settings.html', name=name)