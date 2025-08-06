import secrets
from datetime import datetime, timedelta
from typing import Optional
import requests
import os
from sqlalchemy.orm import Session
from app.models.user import User
from passlib.hash import bcrypt

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash using bcrypt"""
    return bcrypt.verify(password, hashed_password)

def generate_session_token() -> str:
    """Generate a random session token"""
    return secrets.token_urlsafe(32)

def generate_verification_token() -> str:
    """Generate a random verification token for email verification"""
    return secrets.token_urlsafe(16)

def generate_reset_token() -> str:
    """Generate a random password reset token"""
    return secrets.token_urlsafe(16)

def send_verification_email(email: str, token: str) -> bool:
    """Send verification email using Mailgun API"""
    try:
        mailgun_api_key = os.getenv("MAILGUN_API_KEY")
        mailgun_domain = os.getenv("MAILGUN_DOMAIN")
        from_email = os.getenv("MAILGUN_FROM_EMAIL")
        
        if not all([mailgun_api_key, mailgun_domain, from_email]):
            print("Mailgun configuration missing")
            return False
        
        base_url = os.getenv("BASE_URL")
        verification_url = f"{base_url}/verify-email?token={token}"
        
        subject = "Verify your AuthentiCute account"
        html_content = f"""
        <html>
        <body>
            <h2>Welcome to AuthentiCute!</h2>
            <p>
                Please click the link below to verify your email address:
                <a href="{verification_url}">Verify Email</a>
            </p>
            <p>If you didn't create this account, you can ignore this email.</p>
        </body>
        </html>
        """
        
        response = requests.post(
            f"https://api.mailgun.net/v3/{mailgun_domain}/messages",
            auth=("api", mailgun_api_key),
            data={
                "from": f"AuthentiCute <noreply@{mailgun_domain}>",
                "to": email,
                "subject": subject,
                "html": html_content
            }
        )
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_password_reset_email(email: str, token: str) -> bool:
    """Send password reset email using Mailgun API"""
    try:
        mailgun_api_key = os.getenv("MAILGUN_API_KEY")
        mailgun_domain = os.getenv("MAILGUN_DOMAIN")
        from_email = os.getenv("MAILGUN_FROM_EMAIL")
        
        if not all([mailgun_api_key, mailgun_domain, from_email]):
            print("Mailgun configuration missing")
            return False
        
        base_url = os.getenv("BASE_URL")
        reset_url = f"{base_url}/reset-password?token={token}"
        
        subject = "Reset your AuthentiCute password"
        html_content = f"""
        <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>
                Click the link below to reset your password:
                <a href="{reset_url}">Reset Password</a>
            </p>
            <p>If you didn't request this, you can ignore this email.</p>
            <p>This link will expire in 1 hour.</p>
        </body>
        </html>
        """
        
        response = requests.post(
            f"https://api.mailgun.net/v3/{mailgun_domain}/messages",
            auth=("api", mailgun_api_key),
            data={
                "from": f"AuthentiCute <noreply@{mailgun_domain}>",
                "to": email,
                "subject": subject,
                "html": html_content
            }
        )
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending email: {e}")
        return False 