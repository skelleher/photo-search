from flask import Flask, render_template, jsonify
from flask_cors import CORS
from random import *

app = Flask(__name__,
            static_folder = "./dist/static",
            template_folder = "./dist")

CORS(app)

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/api/random')
def random_number():
    response = {
        'randomNumber': randint(1, 100)
    }
    return jsonify(response)

@app.route('/api/query')
def query():
    response = {
        'query_result': randint(1, 100)
    }
    return jsonify(response)

