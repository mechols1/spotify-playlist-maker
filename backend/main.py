import os
import functions_framework
from flask import jsonify, redirect, request
import requests
from datetime import datetime, timedelta
from google.cloud import firestore
from flask_cors import cross_origin
from functions.analytics.history_operations import process_listening_history, get_listening_stats as get_user_stats
from google.api_core import retry


db = firestore.Client()


# Common CORS configuration
CORS_CONFIG = {
    'origins': [
        'http://localhost:3000',
        'https://localhost:3000',
        # Add your production domains here when deployed
    ],
    'methods': ['GET', 'POST', 'OPTIONS'],
    'allow_headers': [
        'Content-Type',
        'Authorization',
        'Access-Control-Allow-Origin',
        'Access-Control-Allow-Headers',
        'Access-Control-Allow-Methods'
    ],
    'max_age': 3600,
    'supports_credentials': True
}

@retry.Retry(predicate=retry.if_exception_type(Exception))
def get_user_data(user_id):
    """Get user data with retry logic"""
    user_ref = db.collection('users').document(user_id)
    user_doc = user_ref.get(_retry=True)
    if not user_doc.exists:
        raise ValueError('User not found')
    return user_doc.to_dict()

@functions_framework.http
@cross_origin(**CORS_CONFIG)
def spotify_auth(request):
    """Handles Spotify OAuth callback."""
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    
    # Handle the callback from Spotify
    if request.args.get('code'):
        try:
            code = request.args.get('code')
            
            # Exchange code for access token
            token_url = 'https://accounts.spotify.com/api/token'
            token_data = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': os.getenv('REDIRECT_URI'),
                'client_id': os.getenv('SPOTIFY_CLIENT_ID'),
                'client_secret': os.getenv('SPOTIFY_CLIENT_SECRET')
            }
            
            token_response = requests.post(token_url, data=token_data)
            token_info = token_response.json()
            
            if token_response.status_code != 200:
                return redirect(f"{frontend_url}/callback?error=token_error")
            
            # Get user profile
            profile_response = requests.get(
                'https://api.spotify.com/v1/me',
                headers={'Authorization': f"Bearer {token_info['access_token']}"}
            )
            profile = profile_response.json()
            
            # Store in Firestore
            user_ref = db.collection('users').document(profile['id'])
            user_ref.set({
                'spotify_id': profile['id'],
                'access_token': token_info['access_token'],
                'refresh_token': token_info['refresh_token'],
                'token_expiry': datetime.now() + timedelta(seconds=token_info['expires_in']),
                'display_name': profile['display_name'],
                'email': profile.get('email'),
                'last_updated': datetime.now()
            })
            
            return redirect(f"{frontend_url}/callback/success?auth=success&user_id={profile['id']}")
            
        except Exception as e:
            print(f"Error during authentication: {str(e)}")
            return redirect(f"{frontend_url}/callback?error={str(e)}")
    
    return redirect(f"{frontend_url}/callback?error=no_code")

@functions_framework.http
@cross_origin(**CORS_CONFIG)
def refresh_token(request):
    """HTTP endpoint to refresh access token."""
    try:
        request_json = request.get_json()
        if not request_json or 'user_id' not in request_json:
            return jsonify({'error': 'Missing user_id'}), 400
            
        user_id = request_json['user_id']
        
        # Get user from Firestore
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            return jsonify({'error': 'User not found'}), 404
            
        user_data = user_doc.to_dict()
        
        # Refresh token
        token_url = 'https://accounts.spotify.com/api/token'
        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': user_data['refresh_token'],
            'client_id': os.getenv('SPOTIFY_CLIENT_ID'),
            'client_secret': os.getenv('SPOTIFY_CLIENT_SECRET')
        }
        
        response = requests.post(token_url, data=payload)
        token_info = response.json()
        
        if response.status_code != 200:
            return jsonify({'error': 'Failed to refresh token'}), 400
        
        # Update user in Firestore
        user_ref.update({
            'access_token': token_info['access_token'],
            'token_expiry': datetime.now() + timedelta(seconds=token_info['expires_in']),
            'last_updated': datetime.now()
        })
        
        return jsonify({
            'access_token': token_info['access_token'],
            'expires_in': token_info['expires_in']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@functions_framework.http
@cross_origin(**CORS_CONFIG)
def get_listening_history(request):
    """Get processed listening history for a user."""
    try:
        if request.method == 'OPTIONS':
            return ('', 204)

        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'Missing user_id'}), 400
            
        # Get user's access token
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            return jsonify({'error': 'User not found'}), 404
            
        user_data = user_doc.to_dict()
        access_token = user_data.get('access_token')
        
        # Fetch recently played tracks from Spotify
        response = requests.get(
            'https://api.spotify.com/v1/me/player/recently-played?limit=50',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch tracks'}), response.status_code
            
        tracks_data = response.json().get('items', [])
        
        # Process and store history
        history = process_listening_history(user_id, tracks_data)
        
        # Just return the response - @cross_origin will handle CORS headers
        return jsonify({'history': history}), 200
        
    except Exception as e:
        print(f"Error in get_listening_history: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@functions_framework.http
@cross_origin(**CORS_CONFIG)
def get_listening_stats(request):
    """Get listening statistics for a user."""
    try:
        # Handle both GET and POST methods
        user_id = request.args.get('user_id') if request.method == 'GET' else request.get_json(silent=True).get('user_id')
            
        if not user_id:
            return jsonify({'error': 'Missing user_id'}), 400
            
        # Get stats using the renamed imported function
        stats = get_user_stats(user_id)
        
        return jsonify({
            'total_hours': stats.get('total_hours', 0)
        }), 200
        
    except Exception as e:
        print(f"Error in get_listening_stats: {str(e)}")
        return jsonify({'error': str(e)}), 500