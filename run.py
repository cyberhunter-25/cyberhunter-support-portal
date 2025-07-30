#!/usr/bin/env python
"""
Run the CyberHunter Security Portal application
"""
import os
from app import create_app, db
from app.models import Company, User, AdminUser

app = create_app(os.environ.get('FLASK_ENV', 'development'))


@app.cli.command()
def init_db():
    """Initialize the database"""
    db.create_all()
    print("Database initialized!")


@app.cli.command()
def create_admin():
    """Create an admin user"""
    from getpass import getpass
    
    username = input("Admin username: ")
    email = input("Admin email: ")
    password = getpass("Admin password: ")
    
    # Check if admin already exists
    if AdminUser.find_by_username(username) or AdminUser.find_by_email(email):
        print("Admin user already exists!")
        return
    
    # Create admin
    admin = AdminUser(
        username=username.lower(),
        email=email.lower(),
        role='admin'
    )
    admin.set_password(password)
    
    db.session.add(admin)
    db.session.commit()
    
    print(f"Admin user '{username}' created successfully!")
    print("Note: MFA setup will be required on first login.")


@app.cli.command()
def create_test_company():
    """Create a test company"""
    company = Company(
        name="Test Company",
        domain="test.com",
        contact_info={
            "email": "contact@test.com",
            "phone": "+1-555-555-5555"
        },
        active=True,
        allow_local_auth=True
    )
    
    db.session.add(company)
    db.session.commit()
    
    print(f"Test company '{company.name}' created with domain '{company.domain}'")


if __name__ == '__main__':
    app.run()