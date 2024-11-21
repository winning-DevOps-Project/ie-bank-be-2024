from flask import Blueprint, jsonify, request
from iebank_api import db
from iebank_api.models import User, Account

api = Blueprint('api', __name__)

# User Registration Route
@api.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    # Validate the input
    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    # Check if username already exists
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already taken"}), 400

    # Create a new user with hashed password
    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

# User Login Route
@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    # Fetch the user by username
    user = User.query.filter_by(username=username).first()
    
    # Verify the password
    if user and user.verify_password(password):
        return jsonify({"message": "Login successful"}), 200

    return jsonify({"error": "Invalid username or password"}), 401

# Create Account Route
@api.route('/accounts', methods=['POST'])
def create_account():
    data = request.get_json()
    name = data.get("name")
    currency = data.get("currency")
    country = data.get("country")

    # Validate the input
    if not name or not currency or not country:
        return jsonify({"error": "Missing account details"}), 400

    # Create a new account
    account = Account(name=name, currency=currency, country=country)
    db.session.add(account)
    db.session.commit()

    return jsonify({
        "message": "Account created successfully",
        "account_number": account.account_number
    }), 201

# Get All Accounts Route
@api.route('/accounts', methods=['GET'])
def get_accounts():
    accounts = Account.query.all()
    return jsonify({
        "accounts": [
            {
                "id": account.id,
                "name": account.name,
                "account_number": account.account_number,
                "balance": account.balance,
                "currency": account.currency,
                "status": account.status,
                "created_at": account.created_at,
                "country": account.country
            }
            for account in accounts
        ]
    })

# Get Single Account Route
@api.route('/accounts/<int:id>', methods=['GET'])
def get_account(id):
    account = Account.query.get(id)
    if not account:
        return jsonify({"error": "Account not found"}), 404

    return jsonify({
        "id": account.id,
        "name": account.name,
        "account_number": account.account_number,
        "balance": account.balance,
        "currency": account.currency,
        "status": account.status,
        "created_at": account.created_at,
        "country": account.country
    })

# Update Account Route
@api.route('/accounts/<int:id>', methods=['PUT'])
def update_account(id):
    account = Account.query.get(id)
    if not account:
        return jsonify({"error": "Account not found"}), 404

    data = request.get_json()
    account.name = data.get("name", account.name)
    account.country = data.get("country", account.country)
    db.session.commit()

    return jsonify({
        "message": "Account updated successfully",
        "id": account.id,
        "name": account.name,
        "country": account.country
    })

# Delete Account Route
@api.route('/accounts/<int:id>', methods=['DELETE'])
def delete_account(id):
    account = Account.query.get(id)
    if not account:
        return jsonify({"error": "Account not found"}), 404

    db.session.delete(account)
    db.session.commit()

    return jsonify({"message": "Account deleted successfully"})

# List Account Route
@api.route('/accounts/<int:id>', methods=['LIST'])
def list_account(id):
    account = Account.query.get(id)
    if not account:
        return jsonify({"error": "Account not found"}), 404
    
    db.session.list(account)
    db.session.commit()

    return jsonify({"message": "Here is a list of accounts: "})

# New Account Route with unique account number
@api.route('/accounts/new', methods=['POST'])
def new_account():
    data = request.get_json()
    name = data.get("name")
    currency = data.get("currency")
    country = data.get("country")

    # Validate the input
    if not name or not currency or not country:
        return jsonify({"error": "Missing account details"}), 400

    # Create a new account with unique account number
    account = Account(name=name, currency=currency, country=country)
    db.session.add(account)
    db.session.commit()

    return jsonify({
        "message": "Account created successfully",
        "account_number": account.account_number
    })

