from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)

# Select environment based on the ENV environment variable
if os.getenv('ENV') == 'local':
    print("Running in local mode")
    app.config.from_object('config.LocalConfig')
elif os.getenv('ENV') == 'dev':
    print("Running in development mode")
    app.config.from_object('config.DevelopmentConfig')
elif os.getenv('ENV') == 'ghci':
    print("Running in GitHub CI mode")
    app.config.from_object('config.GithubCIConfig')
elif os.getenv('ENV') == 'uat':
    print("Running in UAT mode")
    app.config.from_object('config.UATConfig')

# Initialize database
db = SQLAlchemy(app)

# Import models to ensure tables are created
from iebank_api.models import Account, User  # Importing both Account and User models

# Enable CORS
CORS(app)

# Import routes to register endpoints
from iebank_api import routes

