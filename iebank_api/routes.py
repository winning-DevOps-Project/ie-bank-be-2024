import logging
from flask import Blueprint, request, jsonify
from iebank_api.models import Account, User, Transaction
from iebank_api import db  # Import db here
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

# Initialize logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Define the blueprint
api = Blueprint('api', __name__)

# Define a sample route for testing
@api.route('/')
def home():
    logger.info("Home route accessed")
    return "Welcome to IE Bank Backend!"

@api.route('/register/', methods=['POST'])
def register():
    logger.info("Register endpoint accessed")
    try:
        username = request.json.get("username")
        password = request.json.get("password")
        password_2 = request.json.get("password_2")
        country = request.json.get("country")
        
        if password != password_2:
            logger.warning("Passwords do not match")
            return jsonify({"msg": "Passwords do not match"}), 400
        
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

        account = Account(name=f"{username}'s Account", currency="€", country=country)
        account.user_id = user.id  # Link the account to the user
        db.session.add(account)
        db.session.commit()

        logger.info(f"Default account created for user {username}")
        
        access_token = create_access_token(identity={"username": user.username, "is_admin": user.is_admin, "id": user.id})
        refresh_token = create_refresh_token(identity={"username": user.username, "is_admin": user.is_admin, "id": user.id})

        return jsonify({
            "msg": "User registered successfully",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "is_admin": user.is_admin
        }), 201

    except Exception as e:
        logger.error(f"Error in register endpoint: {str(e)}")
        return jsonify({"error": f"An error occurred {str(e)}"}), 500


# User Login Route
@api.route('/login/', methods=['POST'])
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
            access_token = create_access_token(identity={"username": user.username, "is_admin": user.is_admin, "id": user.id})
            refresh_token = create_refresh_token(identity={"username": user.username, "is_admin": user.is_admin, "id": user.id})
            return jsonify({
            "msg": "User logged in successfully",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "is_admin": user.is_admin
        }), 201

        logger.warning(f"Login failed for user {username}")
        return jsonify({"msg": "Invalid username and/or password"}), 401
    except Exception as e:
        logger.error(f"Error in login endpoint: {str(e)}")
        return jsonify({"error": f"An error occurred {str(e)}"}), 500

@api.route('/accounts/', methods=['POST'])
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


@api.route('/transfer/', methods=['POST'])
@jwt_required()
def transfer_money():
    logger.info("Transfer endpoint accessed")

    try:
        
        sender_account_number = request.json.get('sender_account_number')
        recipient_account_number = request.json.get('recipient_account_number')
        transfer_amount = request.json.get('amount')

        if not transfer_amount or transfer_amount <= 0:
            logger.warning(f"Invalid transfer amount: {transfer_amount}")
            return jsonify({"msg": "Invalid transfer amount"}), 400

        sender_account = Account.query.filter_by(account_number=sender_account_number).first()
        recipient_account = Account.query.filter_by(account_number=recipient_account_number).first()
        
        # Check if the sender is the same as the user logged in
        current_user = get_jwt_identity()
        current_user_account = Account.query.filter_by(user_id=current_user.get("id")).first()
        
        if current_user.get("id") != current_user_account.user_id:
            logger.warning("Someone other than the account owner attempted to transfer money")
            return jsonify({"msg": "You are not authorized to make this transaction"}), 403

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
        
        transaction = Transaction(sender=sender_account_number, receiver=recipient_account_number, amount=transfer_amount)
        db.session.add(transaction)
        
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


@api.route('/accounts/', methods=['GET'])
@jwt_required()
def get_accounts():
    current_user = get_jwt_identity()
    if current_user.get("is_admin"):
        logger.info(f"Admin user {current_user.get('username')} retrieved all accounts")
        accounts = Account.query.all()
    else:
        accounts = Account.query.filter_by(user_id=current_user.get("id")).all()
    try:
        logger.info(f"{current_user}")
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

@api.route('/accounts/<account_number>/', methods=['PUT'])
@jwt_required()
def update_account(account_number):
    logger.info("Update account endpoint accessed")
    current_user = get_jwt_identity()
    
    current_user_account = Account.query.filter_by(user_id=current_user.get("id")).first()
    
    if not current_user.get("is_admin") or (current_user_account and current_user.get("id") == current_user_account.user_id):
        logger.warning("Non-admin user or wrong user attempted to update an account")
        return jsonify({"msg": "Admin access required"}), 403

    try:
        
        account = Account.query.filter_by(account_number=account_number).first()
        
        if not account:
            logger.warning(f"Account {account_number} not found")
            return jsonify({"msg": "Account not found"}), 404

        account.name = request.json.get('name', account.name)
        account.currency = request.json.get('currency', account.currency)
        account.country = request.json.get('country', account.country)
        account.status = request.json.get('status', account.status)

        db.session.commit()
        logger.info(f"Account {account_number} updated successfully")
        return jsonify({"msg": "Account updated successfully"}), 200
    except Exception as e:
        logger.error(f"Error updating account: {str(e)}")
        return jsonify({"error": "An error occurred"}), 500

@api.route('/accounts/<account_number>/', methods=['DELETE'])
@jwt_required()
def delete_account(account_number):
    logger.info("Delete account endpoint accessed")
    current_user = get_jwt_identity()
    if not current_user.get("is_admin"):
        logger.warning("Non-admin user attempted to delete an account")
        return jsonify({"msg": "Admin access required"}), 403

    try:
        account = Account.query.filter_by(account_number=account_number).first()
        if not account:
            logger.warning(f"Account {account_number} not found")
            return jsonify({"msg": "Account not found"}), 404

        db.session.delete(account)
        db.session.commit()
        logger.info(f"Account {account_number} deleted successfully")
        return jsonify({"msg": "Account deleted successfully"}), 200
    except Exception as e:
        logger.error(f"Error deleting account: {str(e)}")
        return jsonify({"error": "An error occurred"}), 500
    
@api.route('/deposit/', methods=['POST'])
@jwt_required()
def deposit():
    logger.info("Deposit endpoint accessed")
    current_user = get_jwt_identity()
    # a user deposits money into their account as if they were making a deposit at an ATM
    try:
        account_number = request.json.get('account_number')
        deposit_amount = request.json.get('amount')
        if not deposit_amount or deposit_amount <= 0:
            logger.warning(f"Invalid deposit amount: {deposit_amount}")
            return jsonify({"msg": "Invalid deposit amount"}), 400

        account = Account.query.filter_by(account_number=account_number).first()
        if not account:
            logger.warning(f"Account {account_number} not found")
            return jsonify({"msg": "Account not found"}), 404

        account.balance += deposit_amount
        
        transaction = Transaction(sender=account_number, receiver=account_number, amount=deposit_amount)
        
        db.session.add(transaction)
        
        db.session.commit()

        logger.info(f"Deposit of {deposit_amount} to account {account_number} completed successfully")
        return jsonify({
            "msg": "Deposit successful",
            "account_number": account_number,
            "amount_deposited": deposit_amount
        }), 200
    except Exception as e:
        logger.error(f"Error during deposit: {str(e)}")
        return jsonify({"error": "An error occurred"}), 500
    

@api.route('/user/accounts/', methods=['GET'])
@jwt_required()
def get_user_accounts():
    logger.info("Get user's accounts endpoint accessed")
    try:
        current_user = get_jwt_identity()
        username = current_user.get("username")

        user = User.query.filter_by(username=username).first()
        if not user:
            logger.warning(f"User {username} not found")
            return jsonify({"msg": "User not found"}), 404
        
        accounts = Account.query.filter_by(user_id=user.id).all()
        logger.info(f"{len(accounts)} accounts retrieved for user {username}")

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
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving user's accounts: {str(e)}")
        return jsonify({"error": "An error occurred"}), 500

@api.route('/user/transactions/', methods=['GET'])
@jwt_required()
def get_user_transactions():
    logger.info("Get user's transactions endpoint accessed")
    try:
        current_user = get_jwt_identity()
        username = current_user.get("username")

        user = User.query.filter_by(username=username).first()
        if not user:
            logger.warning(f"User {username} not found")
            return jsonify({"msg": "User not found"}), 404

        accounts = Account.query.filter_by(user_id=user.id).all()
        account_numbers = [account.account_number for account in accounts]

        # Now we order by transaction_date descending
        transactions = Transaction.query\
            .filter(Transaction.sender.in_(account_numbers) | Transaction.receiver.in_(account_numbers))\
            .order_by(Transaction.transaction_date.desc())\
            .all()

        logger.info(f"{len(transactions)} transactions retrieved for user {username}")

        return jsonify({
            "transactions": [
                {
                    "id": transaction.id,
                    "sender": transaction.sender,
                    "receiver": transaction.receiver,
                    "amount": transaction.amount,
                    "timestamp": transaction.transaction_date
                }
                for transaction in transactions
            ]
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving user's transactions: {str(e)}")
        return jsonify({"error": "An error occurred"}), 500