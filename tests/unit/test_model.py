from iebank_api.models import Account, User, Transaction
import pytest

import datetime

def test_account_default_values():
    """
    GIVEN an Account model
    WHEN a new Account is created without optional values
    THEN check the default values are set correctly
    """
    account = Account('Jane Doe', '€', 'France')
    assert account.balance == 0.0
    assert account.status == 'Active'
    assert account.account_number is not None
    assert len(account.account_number) == 20
    assert account.country == 'France'

def test_account_repr():
    """
    GIVEN an Account model
    WHEN an Account object is created
    THEN check its __repr__ method returns the correct string
    """
    account = Account('Jane Doe', '€', 'Germany')
    assert repr(account) == f'<Account {account.account_number}>'

def test_user_creation():
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the username and is_admin fields are defined correctly
    """
    user = User(username='testuser', is_admin=True)
    assert user.username == 'testuser'
    assert user.is_admin is True

def test_set_password():
    """
    GIVEN a User model
    WHEN a password is set
    THEN check the password is hashed and stored correctly
    """
    user = User(username='testuser')
    user.set_password('TestPassword123')
    assert user.password_hash is not None
    assert user.verify_password('TestPassword123') is True
    assert user.verify_password('WrongPassword') is False

def test_user_relationship_with_account():
    """
    GIVEN a User and Account model
    WHEN a User has related Accounts
    THEN check the relationship is set correctly
    """
    user = User(username='testuser')
    account = Account('Jane Doe', '€', 'Spain')
    user.account.append(account)
    assert account.user == user

def test_transaction_creation():
    """
    GIVEN a Transaction model
    WHEN a new Transaction is created
    THEN check the sender, receiver, amount, and transaction_date are defined correctly
    """
    transaction = Transaction('SenderAccount123', 'ReceiverAccount456', 250.0)
    assert transaction.sender == 'SenderAccount123'
    assert transaction.receiver == 'ReceiverAccount456'
    assert transaction.amount == 250.0

def test_transaction_repr():
    """
    GIVEN a Transaction model
    WHEN a Transaction object is created
    THEN check its __repr__ method returns the correct string
    """
    transaction = Transaction('SenderAccount123', 'ReceiverAccount456', 250.0)
    assert repr(transaction) == f'<Transaction {transaction.id}>'
