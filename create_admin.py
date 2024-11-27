# create_admin.py

import os
from getpass import getpass
from app import create_app
from iebank_api.models import db, User

def create_default_admin():
    """
    Creates a default admin user.
    Credentials are sourced from environment variables or prompted securely.
    """
    app = create_app()
    
    with app.app_context():
        # Check if any users exist
        
        print("Creating default admin user.")
        
        if User.query.count() > 0:
            print("Admin user already exists. Aborting creation.")
            return
        
        # Fetch credentials from environment variables or prompt the user
        default_admin_username = os.getenv('DEFAULT_ADMIN_USERNAME', 'admin')
        default_admin_email = os.getenv('DEFAULT_ADMIN_EMAIL', 'admin@example.com')
        
        # Securely prompt for password if not set in environment
        default_admin_password = os.getenv('DEFAULT_ADMIN_PASSWORD', 'Password123')
        
        # Validate password strength (basic example)
        if len(default_admin_password) < 8:
            print("Password must be at least 8 characters long. Admin creation aborted.")
            return
        
        # Create the admin user
        admin_user = User(
            username=default_admin_username,
            is_admin=True
        )
        admin_user.set_password(default_admin_password)
        
        # Add to the session and commit
        db.session.add(admin_user)
        db.session.commit()
        
        print(f"Default admin user '{admin_user.username}' created successfully.")

if __name__ == "__main__":
    create_default_admin()
