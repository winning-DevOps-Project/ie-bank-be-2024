from datetime import datetime
import string, random
from iebank_api import db
from datetime import datetime
import string, random
from iebank_api import db
from werkzeug.security import generate_password_hash, check_password_hash
import logging

# Initialize logger for this module
logger = logging.getLogger("hello")

# Account Model
class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    account_number = db.Column(db.String(20), nullable=False, unique=True)
    balance = db.Column(db.Float, nullable=False, default=0.0)
    currency = db.Column(db.String(1), nullable=False, default="€")
    status = db.Column(db.String(10), nullable=False, default="Active")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    country = db.Column(db.String(15), nullable=False, default="No Country Selected")

    # Add the foreign key to link the account to a user
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Foreign key

    def __repr__(self):
        return f'<Account {self.account_number}>'

    def __init__(self, name, currency, country):
        self.name = name
        self.account_number = ''.join(random.choices(string.digits, k=20))
        self.currency = currency
        self.balance = 0.0
        self.status = "Active"
        self.country = country
        logger.info(f"Account initialized for user: {self.name} with account number {self.account_number}")


# User Model for Authentication
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    
    # Updated relationship to match the foreign key
    account = db.relationship('Account', backref='user', uselist=True)

    def set_password(self, password):
        """
        Hash and set the password for the user.
        """
        try:
            self.password_hash = generate_password_hash(password)
            logger.info(f"Password set for user: {self.username}")
        except Exception as e:
            logger.error(f"Error setting password for user {self.username}: {str(e)}")
            raise

    def verify_password(self, password):
        """
        Check if the provided password matches the stored hash.
        """
        try:
            is_valid = check_password_hash(self.password_hash, password)
            logger.info(f"Password verification for user {self.username}: {'Success' if is_valid else 'Failure'}")
            return is_valid
        except Exception as e:
            logger.error(f"Error verifying password for user {self.username}: {str(e)}")
            raise

    def __repr__(self):
        """
        Return a string representation of the user.
        """
        return f'<User {self.username}>'
    


# Initialize the SQLAlchemy object
def init_db(app):
    """Initialize the database with the app context."""
    db.init_app(app)
    with app.app_context():
        db.create_all()  # Creates tables for all defined models
        logger.info("Database initialized and all tables created.")