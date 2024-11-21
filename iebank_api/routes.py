from flask import Flask, request, jsonify
from iebank_api import db, app
from iebank_api.models import Account
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['JWT_SECRET_KEY'] = 'input secret key'
db = SQLAlchemy(app)
jwt = JWTManager(app)

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
    text = text +'<br/>Database URL:' + db.engine.url.database
    if db.engine.url.host:
        text = text +'<br/>Database host:' + db.engine.url.host
    if db.engine.url.port:
        text = text +'<br/>Database port:' + db.engine.url.port
    if db.engine.url.username:
        text = text +'<br/>Database user:' + db.engine.url.username
    if db.engine.url.password:
        text = text +'<br/>Database password:' + db.engine.url.password
    return text
  
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

def create_default_admin():
    if not User.query.filter_by(username="admin").first(): # have to check if user exist
        admin_user = User(
            username="admin",
            password=generate_password_hash("1234"),  # this is the password by default
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("default admin made with username = admin and password = 1234")


@app.route('/accounts', methods=['POST'])
@jwt_required()
def create_account():
    current_user = get_jwt_identity()
    if not current_user.get("is_admin"):
        return jsonify({"msg": "Admin access required"}), 403

    name = request.json['name']
    currency = request.json['currency']
    country = request.json['country']
    account = Account(name=name, currency=currency, country=country)
    db.session.add(account)
    db.session.commit()


@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    user = User.query.filter_by(username=username).first()
    
    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity={"username": user.username, "is_admin": user.is_admin})
        return jsonify(access_token=access_token), 200
    return jsonify({"msg": "Invalid username and/or password"}), 401


@app.route('/admin-only', methods=['GET'])
@jwt_required()
def admin_only():
    current_user = get_jwt_identity()
    if not current_user.get("is_admin"):
        return jsonify({"msg": "Admin access needed"}), 403
    return jsonify({"msg": "Welcome, Admin!"}), 200

@app.route('/accounts', methods=['GET'])
@jwt_required()
def get_accounts():
    current_user = get_jwt_identity()
    if not current_user.get("is_admin"):
        return jsonify({"msg": "Admin access required"}), 403

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


@app.route('/accounts/<int:id>', methods=['PUT'])
@jwt_required()
def update_account(id):
    current_user = get_jwt_identity()
    if not current_user.get("is_admin"):
        return jsonify({"msg": "Admin access required"}), 403

    account = Account.query.get(id)
    if not account:
        return jsonify({"msg": "Account not found"}), 404

    account.name = request.json['name']
    account.country = request.json['country']
    db.session.commit()


@app.route('/accounts/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_account(id):
    current_user = get_jwt_identity()
    if not current_user.get("is_admin"):
        return jsonify({"msg": "Admin access required"}), 403

    account = Account.query.get(id)
    if not account:
        return jsonify({"msg": "Account not found"}), 404

    db.session.delete(account)
    db.session.commit()
    return jsonify({"msg": "Account deleted successfully"})

@app.route('/users', methods=['GET'])
@jwt_required()
def list_users():
    current_user = get_jwt_identity()
    if not current_user.get("is_admin"):
        return jsonify({"msg": "Admin access required"}), 403

    users = User.query.all()
    return jsonify([{"id": user.id, "username": user.username, "is_admin": user.is_admin} for user in users])

@app.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    current_user = get_jwt_identity()
    if not current_user.get("is_admin"):
        return jsonify({"msg": "Admin access required"}), 403

    username = request.json['username']
    password = generate_password_hash(request.json['password'])
    is_admin = request.json.get('is_admin', False)

    new_user = User(username=username, password=password, is_admin=is_admin)
    db.session.add(new_user)
    db.session.commit()
    return {"msg": "User created successfully"}

@app.route('/users/<int:id>', methods=['PUT'])
@jwt_required()
def update_user(id):
    current_user = get_jwt_identity()
    if not current_user.get("is_admin"):
        return jsonify({"msg": "Admin access required"}), 403

    user = User.query.get(id)
    if not user:
        return {"msg": "User not found"}, 404

    user.username = request.json.get('username', user.username)
    user.password = generate_password_hash(request.json.get('password', user.password))
    user.is_admin = request.json.get('is_admin', user.is_admin)
    db.session.commit()
    return {"msg": "User updated successfully"}

@app.route('/users/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    current_user = get_jwt_identity()
    if not current_user.get("is_admin"):
        return jsonify({"msg": "Admin access required"}), 403

    user = User.query.get(id)
    if not user:
        return {"msg": "User not found"}, 404

    db.session.delete(user)
    db.session.commit()
    return {"msg": "User deleted successfully"}

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

import os

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  
        create_default_admin() 
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']
    app.run(debug=debug_mode)
