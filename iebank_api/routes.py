from flask import Flask, request, jsonify
from iebank_api import db, app
from iebank_api.models import Account
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

auth = HTTPBasicAuth()

# Define the User model
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

# Update the verify_password function
@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.verify_password(password):
        return user
    return None

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/skull', methods=['GET'])
@auth.login_required
def skull():
    text = 'Hi! This is the BACKEND SKULL! 💀 '
    text += '<br/>Database URL:' + db.engine.url.database
    if db.engine.url.host:
        text += '<br/>Database host:' + db.engine.url.host
    if db.engine.url.port:
        text += '<br/>Database port:' + db.engine.url.port
    if db.engine.url.username:
        text += '<br/>Database user:' + db.engine.url.username
    if db.engine.url.password:
        text += '<br/>Database password:' + db.engine.url.password
    return text

@app.route('/accounts', methods=['POST'])
@auth.login_required
def create_account():
    name = request.json['name']
    currency = request.json['currency']
    country = request.json['country']
    account = Account(name, currency, country)
    db.session.add(account)
    db.session.commit()
    return format_account(account)

@app.route('/accounts', methods=['GET'])
@auth.login_required
def get_accounts():
    accounts = Account.query.all()
    return {'accounts': [format_account(account) for account in accounts]}

@app.route('/accounts/<int:id>', methods=['GET'])
@auth.login_required
def get_account(id):
    account = Account.query.get(id)
    return format_account(account)

@app.route('/accounts/<int:id>', methods=['PUT'])
@auth.login_required
def update_account(id):
    account = Account.query.get(id)
    account.name = request.json['name']
    account.country = request.json['country']
    db.session.commit()
    return format_account(account)

@app.route('/accounts/<int:id>', methods=['DELETE'])
@auth.login_required
def delete_account(id):
    account = Account.query.get(id)
    db.session.delete(account)
    db.session.commit()
    return format_account(account)

def format_account(account):
    return {
        'id': account.id,
        'name': account.name,
        'country': account.country,
        'account_number': account.account_number,
        'balance': account.balance,
        'currency': account.currency,
        'status': account.status,
        'created_at': account.created_at
    }

# Route to add a new user (for testing or admin use only)
@app.route('/register', methods=['POST'])
def register():
    username = request.json['username']
    password = request.json['password']
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "User already exists"}), 400
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201
