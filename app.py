from flask import Flask
from iebank_api import db
from iebank_api.routes import api  # Import the blueprint
from iebank_api.models import User, Account  # Ensure User and Account models are loaded
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'  # Update as needed
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Register the blueprint
app.register_blueprint(api)

with app.app_context():
    db.create_all()  # Creates tables for the User and Account models if not existing

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']
    app.run(debug=debug_mode)
