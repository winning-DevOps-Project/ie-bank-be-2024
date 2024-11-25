from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
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

    db.init_app(app)
    jwt.init_app(app)
    CORS(app)

    # Register blueprints
    from iebank_api.routes import api
    app.register_blueprint(api, url_prefix='/api')

    # Return the app instance
    return app
