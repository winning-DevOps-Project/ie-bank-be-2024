import logging
from flask import Blueprint, request, jsonify
from iebank_api.models import Account, User
from iebank_api import db  # Import db here
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

# Initialize logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Define the blueprint
api = Blueprint('api', __name__)

@api.route('/register', methods=['POST'])
def register():
    logger.info("Register endpoint accessed")
    try:
        username = request.json.get("username")
        password = request.json.get("password")
        is_admin = request.json.get("is_admin", False)

        # Validate inputs
        if not username or not password:
            logger.warning("Username or password missing")
            return jsonify({"msg": "Username or password missing"}), 400

        # Check if user already exists
        if User.query.filter_by(username=username).first():
            logger.warning(f"User {username} already exists")
            return jsonify({"msg": "User already exists"}), 400

        # Create and save the user
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        logger.info(f"User {username} registered successfully")
        
        # Generate tokens
        access_token = create_access_token(identity={"username": user.username, "is_admin": user.is_admin})
        refresh_token = create_refresh_token(identity={"username": user.username, "is_admin": user.is_admin})

        return jsonify({
            "msg": "User registered successfully",
            "access_token": access_token,
            "refresh_token": refresh_token
        }), 201

    except Exception as e:
        logger.error(f"Error in register endpoint: {str(e)}")
        return jsonify({"error": "An error occurred"}), 500

# User Login Route
@api.route('/login', methods=['POST'])
def login():
    logger.info("Login endpoint accessed")
    try:
        # Extract username and password from the request
        username = request.json.get("username")
        password = request.json.get("password")

        # Fetch user from the database
        user = User.query.filter_by(username=username).first()

        # Verify password using the User model's method
        if user and user.verify_password(password):
            logger.info(f"User {username} logged in successfully")
            # Generate JWT token
            access_token = create_access_token(identity={"username": user.username, "is_admin": user.is_admin})
            refresh_token = create_refresh_token(identity={"username": user.username, "is_admin": user.is_admin})
            return jsonify({
            "msg": "User logged in successfully",
            "access_token": access_token,
            "refresh_token": refresh_token
        }), 201

        logger.warning(f"Login failed for user {username}")
        return jsonify({"msg": "Invalid username and/or password"}), 401
    except Exception as e:
        logger.error(f"Error in login endpoint: {str(e)}")
        return jsonify({"error": "An error occurred"}), 500

@api.route('/accounts', methods=['POST'])
@jwt_required()
def create_account():
    logger.info("Create account endpoint accessed")
    current_user = get_jwt_identity()
    if not current_user.get("is_admin"):
        logger.warning("Non-admin user attempted to create an account")
        return jsonify({"msg": "Admin access required"}), 403

    try:
        name = request.json['name']
        currency = request.json['currency']
        country = request.json['country']
        account = Account(name=name, currency=currency, country=country)
        db.session.add(account)
        db.session.commit()
        logger.info(f"Account created successfully for {name}")
        return jsonify({"msg": "Account created successfully"}), 201
    except Exception as e:
        logger.error(f"Error creating account: {str(e)}")
        return jsonify({"error": "An error occurred"}), 500


@api.route('/transfer', methods=['POST'])
@jwt_required()
def transfer_money():
    logger.info("Transfer endpoint accessed")
    current_user = get_jwt_identity()

    try:
        sender_account_number = request.json.get('sender_account_number')
        recipient_account_number = request.json.get('recipient_account_number')
        transfer_amount = request.json.get('amount')

        if not transfer_amount or transfer_amount <= 0:
            logger.warning(f"Invalid transfer amount: {transfer_amount}")
            return jsonify({"msg": "Invalid transfer amount"}), 400

        sender_account = Account.query.filter_by(account_number=sender_account_number).first()
        recipient_account = Account.query.filter_by(account_number=recipient_account_number).first()

        if not sender_account:
            logger.warning(f"Sender account {sender_account_number} not found")
            return jsonify({"msg": "Sender account not found"}), 404
        if not recipient_account:
            logger.warning(f"Recipient account {recipient_account_number} not found")
            return jsonify({"msg": "Recipient account not found"}), 404

        if sender_account.balance < transfer_amount:
            logger.warning(f"Insufficient funds in account {sender_account_number}")
            return jsonify({"msg": "Insufficient funds"}), 400

        sender_account.balance -= transfer_amount
        recipient_account.balance += transfer_amount
        db.session.commit()

        logger.info(f"Transfer of {transfer_amount} from {sender_account_number} to {recipient_account_number} completed successfully")
        return jsonify({
            "msg": "Transfer successful",
            "sender_account": sender_account_number,
            "recipient_account": recipient_account_number,
            "amount_transferred": transfer_amount
        }), 200
    except Exception as e:
        logger.error(f"Error during transfer: {str(e)}")
        return jsonify({"error": "An error occurred"}), 500


@api.route('/accounts', methods=['GET'])
@jwt_required()
def get_accounts():
    logger.info("Get accounts endpoint accessed")
    current_user = get_jwt_identity()
    if not current_user.get("is_admin"):
        logger.warning("Non-admin user attempted to access accounts")
        return jsonify({"msg": "Admin access required"}), 403

    try:
        accounts = Account.query.all()
        logger.info(f"{len(accounts)} accounts retrieved")
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
    except Exception as e:
        logger.error(f"Error retrieving accounts: {str(e)}")
        return jsonify({"error": "An error occurred"}), 500
