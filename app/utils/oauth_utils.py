import os
import requests
from typing import Optional, Dict, Any
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from google_auth_oauthlib.flow import Flow
from sqlalchemy.orm import Session
from app.utils.db_utils import get_user_by_email, create_user
from app.models.user import User

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]

def get_google_oauth_url() -> str:
    """Generate Google OAuth URL for login"""
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [GOOGLE_REDIRECT_URI]
            }
        },
        scopes=GOOGLE_SCOPES
    )
    
    flow.redirect_uri = GOOGLE_REDIRECT_URI
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    
    return authorization_url

def verify_google_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify Google ID token and return user info"""
    try:
        idinfo = id_token.verify_oauth2_token(
            token, 
            google_requests.Request(), 
            GOOGLE_CLIENT_ID
        )
        
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
        
        return {
            'sub': idinfo['sub'],
            'email': idinfo['email'],
            'name': idinfo.get('name', ''),
            'picture': idinfo.get('picture', ''),
            'email_verified': idinfo.get('email_verified', False)
        }
    except Exception as e:
        return None

def get_or_create_google_user(db: Session, google_user_info: Dict[str, Any]) -> User:
    """Get existing user or create new user from Google OAuth data"""
    existing_user = db.query(User).filter(
        User.oauth_provider == 'google',
        User.oauth_id == google_user_info['sub']
    ).first()
    
    if existing_user:
        return existing_user
    
    existing_user = get_user_by_email(db, google_user_info['email'])
    if existing_user:
        existing_user.oauth_provider = 'google'
        existing_user.oauth_id = google_user_info['sub']
        existing_user.oauth_email = google_user_info['email']
        existing_user.is_verified = True
        db.commit()
        return existing_user
    
    user = create_user(
        db=db,
        email=google_user_info['email'],
        hashed_password=None,
        name=google_user_info['name'],
        oauth_provider='google',
        oauth_id=google_user_info['sub'],
        oauth_email=google_user_info['email'],
        is_verified=True
    )
    
    return user

def handle_google_callback(db: Session, authorization_code: str) -> Optional[User]:
    """Handle Google OAuth callback and return user"""
    try:
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'code': authorization_code,
            'grant_type': 'authorization_code',
            'redirect_uri': GOOGLE_REDIRECT_URI
        }
        
        token_response = requests.post(token_url, data=token_data)
        
        if token_response.status_code != 200:
            return None
        
        token_info = token_response.json()
        access_token = token_info.get('access_token')
        
        if not access_token:
            return None
        
        userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {'Authorization': f'Bearer {access_token}'}
        
        userinfo_response = requests.get(userinfo_url, headers=headers)
        
        if userinfo_response.status_code != 200:
            return None
        
        user_info = userinfo_response.json()
        
        google_user_info = {
            'sub': user_info.get('id'),
            'email': user_info.get('email'),
            'name': user_info.get('name', ''),
            'picture': user_info.get('picture', ''),
            'email_verified': user_info.get('verified_email', False)
        }
        
        if not google_user_info['sub'] or not google_user_info['email']:
            return None
        
        user = get_or_create_google_user(db, google_user_info)
        return user
        
    except Exception as e:
        return None 