import os

from flask import Flask

app = Flask(__name__)

# Use environment variable for DB URL
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False