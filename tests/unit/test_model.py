from iebank_api.models import Account, User
from iebank_api import app, db
from datetime import datetime
import pytest
    
@pytest.fixture
def test_client():
    flask_app = app
    
    with flask_app.test_client() as testing_client:
        with flask_app.app_context():
            db.create_all()
            yield testing_client  # TESTING
            db.session.remove()
            db.drop_all()

        
def test_create_account(test_login):
    """
    GIVEN an Account model
    WHEN a new Account is created
    THEN check the name, account_number, balance, currency, status and created_at fields are defined correctly
    """
    with app.app_context():
        account = Account(name="John Doe", currency="€", country="Spain")
        db.session.add(account)
        db.session.commit()

        retrieved_account = Account.query.filter_by(name="John Doe").first()
        assert retrieved_account.name == "John Doe"
        assert retrieved_account.currency == "€"
        assert retrieved_account.account_number is not None
        assert retrieved_account.balance == 0.0
        assert retrieved_account.status == "Active"
        assert retrieved_account.country == "Spain"

        
def test_default_balance(test_client):
    """
    DEAFAULT BALANCE FOR NEW ACCOUNT = 0.0 
    """
    account = Account(name="Jane Doe", currency="£", country="UK")
    db.session.add(account)
    db.session.commit()

    retrieved_account = Account.query.filter_by(name="Jane Doe").first()
    assert retrieved_account.balance == 0.0 
            
def test_unique_account_number(test_client):
    """
    ACCOUNT NUMBER MUST BE UNIQUE 
    """
    account1 = Account(name="User1", currency="$", country="USA")
    db.session.add(account1)
    db.session.commit()

    account2 = Account(name="User2", currency="€", country="Germany")
    db.session.add(account2)

    with pytest.raises(Exception):  
        db.session.commit()
        

def test_account_status(test_client):
    """
    ACCOUNT SHOULD BE ACTIVE STATUS
    """
    account = Account(name="Inactive User", currency="€", country="France")
    db.session.add(account)
    db.session.commit()

    retrieved_account = Account.query.filter_by(name="Inactive User").first()
    assert retrieved_account.status == "Active"  


def test_account_creation_date(test_client):
    """
    CREATED AT SHOULD BE SET TO DATE AND TIME IN MOMENT 
    """
    now = datetime.utcnow()
    account = Account(name="Timestamp User", currency="₹", country="India")
    db.session.add(account)
    db.session.commit()

    retrieved_account = Account.query.filter_by(name="Timestamp User").first()
    assert retrieved_account.created_at.date() == now.date()