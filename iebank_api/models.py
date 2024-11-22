from datetime import datetime
import string, random
from iebank_api import db
from datetime import datetime
import string, random
from iebank_api import db
from werkzeug.security import generate_password_hash, check_password_hash
import logging

# Initialize logger for this module
#logger = logging.getLogger(name)

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

    def repr(self):
        return f'<Account {self.account_number}>'

    def init(self, name, currency, country):
        self.name = name
        self.account_number = ''.join(random.choices(string.digits, k=20))
        self.currency = currency
        self.balance = 0.0
        self.status = "Active"
        self.country = country
        logger.info(f"Account initialized for user: {self.name} with account number {self.account_number}")

    def deposit(self, amount):
        try:
            if amount <= 0:
                raise ValueError("Deposit amount must be positive.")
            self.balance += amount
            db.session.commit()
            logger.info(f"Deposited {amount} {self.currency} to account {self.account_number}. New balance: {self.balance}.")
        except Exception as e:
            logger.error(f"Error during deposit to account {self.account_number}: {str(e)}")
            db.session.rollback()
            raise

    def withdraw(self, amount):
        try:
            if amount > self.balance:
                raise ValueError("Insufficient balance.")
            self.balance -= amount
            db.session.commit()
            logger.info(f"Withdrew {amount} {self.currency} from account {self.account_number}. New balance: {self.balance}.")
        except Exception as e:
            logger.error(f"Error during withdrawal from account {self.account_number}: {str(e)}")
            db.session.rollback()
            raise

# User Model for Authentication
class User(db.Model):
    tablename = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def init(self, username, password):
        self.username = username
        self.password_hash = generate_password_hash(password)
        logger.info(f"User created with username: {self.username}")

    def verify_password(self, password):
        try:
            is_valid = check_password_hash(self.password_hash, password)
            logger.info(f"Password verification for user {self.username}: {'Success' if is_valid else 'Failure'}")
            return is_valid
        except Exception as e:
            logger.error(f"Error verifying password for user {self.username}: {str(e)}")
            raise

    def repr(self):
        return f'<User {self.username}>'

# Initialize the SQLAlchemy object
def init_db(app):
    """Initialize the database with the app context."""
    db.init_app(app)
    with app.app_context():
        db.create_all()  # Creates tables for all defined models
        logger.info("Database initialized and all tables created.")