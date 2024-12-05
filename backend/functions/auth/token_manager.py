from google.cloud import firestore
import requests
import os
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

db = firestore.Client()

def refresh_spotify_token(user_id):
    """Refresh a user's Spotify access token"""
    try:
        logging.info(f"Attempting to refresh token for user: {user_id}")
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            logging.error(f"User {user_id} not found in database")
            return None
            
        user_data = user_doc.to_dict()
        refresh_token = user_data.get('refresh_token')
        
        if not refresh_token:
            logging.error(f"No refresh token found for user {user_id}")
            return None
            
        # Spotify token refresh request
        token_url = 'https://accounts.spotify.com/api/token'
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            logging.error("Missing Spotify API credentials")
            return None
        
        response = requests.post(
            token_url,
            data={
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token
            },
            auth=(client_id, client_secret)
        )
        
        if response.status_code != 200:
            logging.error(f"Token refresh failed with status {response.status_code}")
            logging.error(f"Response: {response.text}")
            return None
            
        token_data = response.json()
        
        # Update token in Firestore
        update_data = {
            'access_token': token_data['access_token'],
            'token_expiry': datetime.now() + timedelta(seconds=token_data['expires_in']),
            'last_token_refresh': datetime.now()
        }
        
        user_ref.update(update_data)
        logging.info(f"Successfully refreshed token for user {user_id}")
        
        return token_data['access_token']
    except Exception as e:
        logging.error(f"Error refreshing token: {str(e)}")
        return None

def validate_token(user_id):
    """Validate and refresh token if needed"""
    try:
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            return None
            
        user_data = user_doc.to_dict()
        token_expiry = user_data.get('token_expiry')
        
        if not token_expiry:
            return refresh_spotify_token(user_id)
            
        # If token expires in less than 5 minutes, refresh it
        if isinstance(token_expiry, datetime):
            if datetime.now() + timedelta(minutes=5) >= token_expiry:
                return refresh_spotify_token(user_id)
            return user_data.get('access_token')
            
        return refresh_spotify_token(user_id)
    except Exception as e:
        logging.error(f"Error validating token: {str(e)}")
        return None