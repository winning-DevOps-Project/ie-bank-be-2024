from datetime import datetime
import string, random
from iebank_api import db
from werkzeug.security import generate_password_hash, check_password_hash

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

    def __repr__(self):
        return f'<Account {self.account_number}>'

    def __init__(self, name, currency, country):
        self.name = name
        self.account_number = ''.join(random.choices(string.digits, k=20))
        self.currency = currency
        self.balance = 0.0
        self.status = "Active"
        self.country = country

# User Model for Authentication
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

# Initialize the SQLAlchemy object
db = SQLAlchemy()

def init_db(app):
    """Initialize the database with the app context."""
    db.init_app(app)
    with app.app_context():
        db.create_all()  # Creates tables for all defined models
