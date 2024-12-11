from iebank_api.models import Account, User

from iebank_api import db

# Test registration endpoint
def test_register(client):
    """
    Test user registration.
    """
    response = client.post('/api/register/', json={
        "username": "newuser",
        "password": "Password123",
        "password_2": "Password123"
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['msg'] == "User registered successfully"
    assert 'access_token' in data
    assert 'refresh_token' in data
    
def test_wrong_register(client):
    """
    Test user registration.
    """
    response = client.post('/api/register/', json={
        "username": "newuser",
        "password": "password",
        "password_2": "password"
    })
    assert response.status_code == 400


# Test login endpoint
def test_login(client, create_user):
    """
    Test user login with valid credentials.
    """
    response = client.post('/api/login/', json={
        "username": "testuser",
        "password": "testpassword"
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['msg'] == "User logged in successfully"
    assert 'access_token' in data
    assert 'refresh_token' in data


def test_create_account(client, create_user):
    """
    Test account creation for an admin user.
    """

    login_response = client.post('/api/login/', json={
        "username": "testuser",
        "password": "testpassword"
    })
    access_token = login_response.get_json()['access_token']


    response = client.post('/api/accounts/', json={
        "name": "Savings Account",
        "currency": "€",
        "country": "Germany"
    }, headers={"Authorization": f"Bearer {access_token}"})
    
    # Log the response for debugging
    print(response.get_json())

    assert response.status_code == 201
    data = response.get_json()
    assert data['msg'] == "Account created successfully"

def test_deposit_money(client, create_user, create_account):
    """
    Test deposit money into an account.
    """
    # Log in to get access token
    login_response = client.post('/api/login/', json={
        "username": "testuser",
        "password": "testpassword"
    })
    access_token = login_response.get_json()['access_token']
    
    # fetch the first account
    account = Account.query.first()

    response = client.post('/api/deposit/', json={
        "account_number": account.account_number,
        "amount": 100.0
    }, headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    data = response.get_json()
    assert data['msg'] == "Deposit successful"
    assert data['amount_deposited'] == 100.0


# Test transfer money endpoint
def test_transfer_money(client, create_user):
    """
    Test money transfer between accounts.
    """
    # Log in to get access token
    login_response = client.post('/api/login/', json={
        "username": "testuser",
        "password": "testpassword"
    })
    access_token = login_response.get_json()['access_token']
    
    user = User.query.filter_by(username="testuser").first()

    # Create recipient account
    with client.application.app_context():
        
        
        
        recipient_account = Account(
            name="Recipient Account",
            currency="€",
            country="France"
        )
        recipient_account.user_id = user.id
        db.session.add(recipient_account)
        db.session.commit()
        
        sender_account = Account(
            name="Sender Account",
            currency="€",
            country="Germany",
        )
        sender_account.user_id = user.id
        db.session.add(sender_account)
        db.session.commit()
        
    sender_number = Account.query.filter_by(name="Sender Account").first().account_number
        
    client.post('api/deposit/', json={
        "account_number": sender_number,
        "amount": 100.0
    }, headers={"Authorization": f"Bearer {access_token}"}
    )
    
    recipient = Account.query.filter_by(name="Recipient Account").first()
        
    recipient_number = recipient.account_number
    

    # Perform transfer
    response = client.post('/api/transfer/', json={
        "sender_account_number": sender_number,
        "recipient_account_number": recipient_number,
        "amount": 100.0
    }, headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    data = response.get_json()
    assert data['msg'] == "Transfer successful"
    assert data['amount_transferred'] == 100.0
    assert recipient.balance == 100.0


# Test get accounts endpoint
def test_get_accounts(client, create_user, create_account):
    """
    Test retrieval of all accounts.
    """
    # Log in to get access token
    login_response = client.post('/api/login/', json={
        "username": "testuser",
        "password": "testpassword"
    })
    access_token = login_response.get_json()['access_token']

    # Retrieve accounts
    response = client.get('/api/accounts/', headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    data = response.get_json()
    assert "accounts" in data
    assert len(data["accounts"]) > 0
