# backend/functions/recommendations/recommendation_operations.py
from google.cloud import firestore
import requests
from datetime import datetime, timedelta

db = firestore.Client()

def get_user_top_items(access_token, item_type='tracks', limit=5):
    response = requests.get(
        f'https://api.spotify.com/v1/me/top/{item_type}',
        headers={'Authorization': f'Bearer {access_token}'},
        params={'limit': limit, 'time_range': 'medium_term'}
    )
    return response.json()['items'] if response.ok else []

def get_spotify_recommendations(access_token, seed_tracks, seed_artists):
    params = {
        'limit': 20,
        'seed_tracks': ','.join(seed_tracks[:2]),
        'seed_artists': ','.join(seed_artists[:3]),
        'min_popularity': 20,
        'target_popularity': 70
    }
    
    response = requests.get(
        'https://api.spotify.com/v1/recommendations',
        headers={'Authorization': f'Bearer {access_token}'},
        params=params
    )
    return response.json()['tracks'] if response.ok else []

def process_recommendations(user_id, tracks_data):
    recommendations_ref = db.collection('users').document(user_id)\
                          .collection('recommendations').document('current')
    
    recommendations = [{
        'id': track['id'],
        'name': track['name'],
        'artists': [artist['name'] for artist in track['artists']],
        'album': track['album']['name'],
        'preview_url': track['preview_url'],
        'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None
    } for track in tracks_data]
    
    recommendations_ref.set({
        'tracks': recommendations,
        'generated_at': datetime.now(),
        'expires_at': datetime.now() + timedelta(hours=24)
    })
    
    return recommendations