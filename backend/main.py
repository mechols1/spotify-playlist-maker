import os
import functions_framework
import time
from flask import jsonify, redirect, request
import requests
from datetime import datetime, timedelta
from google.cloud import firestore
from flask_cors import cross_origin
from functions.analytics.history_operations import (
    process_listening_history,
    get_listening_stats as get_user_stats,
)
from google.api_core import retry
from functions.recommendations.recommendation_operations import (
    get_user_top_items,
    get_spotify_recommendations,
    process_recommendations,
)
import random
db = firestore.Client()


# Common CORS configuration
CORS_CONFIG = {
    "origins": [
        "http://localhost:3000",
        "https://localhost:3000",
        # Add your production domains here when deployed
    ],
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": [
        "Content-Type",
        "Authorization",
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Methods",
    ],
    "max_age": 3600,
    "supports_credentials": True,
}


def get_user_data(user_id):
    """Get user data without retry logic"""
    try:
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()  # Remove _retry parameter
        if not user_doc.exists:
            raise ValueError("User not found")
        return user_doc.to_dict()
    except Exception as e:
        print(f"Error getting user data: {str(e)}")
        raise


@functions_framework.http
@cross_origin(**CORS_CONFIG)
def spotify_auth(request):
    """Handles Spotify OAuth callback."""
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")

    # Handle the callback from Spotify
    if request.args.get("code"):
        try:
            code = request.args.get("code")

            # Exchange code for access token
            token_url = "https://accounts.spotify.com/api/token"
            token_data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": os.getenv("REDIRECT_URI"),
                "client_id": os.getenv("SPOTIFY_CLIENT_ID"),
                "client_secret": os.getenv("SPOTIFY_CLIENT_SECRET"),
            }

            token_response = requests.post(token_url, data=token_data)
            token_info = token_response.json()

            if token_response.status_code != 200:
                return redirect(f"{frontend_url}/callback?error=token_error")

            # Get user profile
            profile_response = requests.get(
                "https://api.spotify.com/v1/me",
                headers={"Authorization": f"Bearer {token_info['access_token']}"},
            )
            profile = profile_response.json()

            # Store in Firestore
            user_ref = db.collection("users").document(profile["id"])
            user_ref.set(
                {
                    "spotify_id": profile["id"],
                    "access_token": token_info["access_token"],
                    "refresh_token": token_info["refresh_token"],
                    "token_expiry": datetime.now()
                    + timedelta(seconds=token_info["expires_in"]),
                    "display_name": profile["display_name"],
                    "email": profile.get("email"),
                    "last_updated": datetime.now(),
                }
            )

            return redirect(
                f"{frontend_url}/callback/success?auth=success&user_id={profile['id']}"
            )

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
        if not request_json or "user_id" not in request_json:
            return jsonify({"error": "Missing user_id"}), 400

        user_id = request_json["user_id"]

        # Get user from Firestore
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()

        if not user_doc.exists:
            return jsonify({"error": "User not found"}), 404

        user_data = user_doc.to_dict()

        # Refresh token
        token_url = "https://accounts.spotify.com/api/token"
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": user_data["refresh_token"],
            "client_id": os.getenv("SPOTIFY_CLIENT_ID"),
            "client_secret": os.getenv("SPOTIFY_CLIENT_SECRET"),
        }

        response = requests.post(token_url, data=payload)
        token_info = response.json()

        if response.status_code != 200:
            return jsonify({"error": "Failed to refresh token"}), 400

        # Update user in Firestore
        user_ref.update(
            {
                "access_token": token_info["access_token"],
                "token_expiry": datetime.now()
                + timedelta(seconds=token_info["expires_in"]),
                "last_updated": datetime.now(),
            }
        )

        return jsonify(
            {
                "access_token": token_info["access_token"],
                "expires_in": token_info["expires_in"],
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@functions_framework.http
@cross_origin(**CORS_CONFIG)
def get_listening_history(request):
    """Get processed listening history for a user."""
    try:
        if request.method == "OPTIONS":
            return ("", 204)

        user_id = request.args.get("user_id")
        if not user_id:
            return jsonify({"error": "Missing user_id"}), 400

        # Get user's access token
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()

        if not user_doc.exists:
            return jsonify({"error": "User not found"}), 404

        user_data = user_doc.to_dict()
        access_token = user_data.get("access_token")

        # Fetch recently played tracks from Spotify
        response = requests.get(
            "https://api.spotify.com/v1/me/player/recently-played?limit=50",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch tracks"}), response.status_code

        tracks_data = response.json().get("items", [])

        # Process and store history
        history = process_listening_history(user_id, tracks_data)

        # Just return the response - @cross_origin will handle CORS headers
        return jsonify({"history": history}), 200

    except Exception as e:
        print(f"Error in get_listening_history: {str(e)}")
        return jsonify({"error": str(e)}), 500


@functions_framework.http
@cross_origin(**CORS_CONFIG)
def get_listening_stats(request):
    """Get listening statistics for a user."""
    try:
        # Handle both GET and POST methods
        user_id = (
            request.args.get("user_id")
            if request.method == "GET"
            else request.get_json(silent=True).get("user_id")
        )

        if not user_id:
            return jsonify({"error": "Missing user_id"}), 400

        # Get stats using the renamed imported function
        stats = get_user_stats(user_id)

        return jsonify({"total_hours": stats.get("total_hours", 0)}), 200

    except Exception as e:
        print(f"Error in get_listening_stats: {str(e)}")
        return jsonify({"error": str(e)}), 500


@functions_framework.http
@cross_origin(**CORS_CONFIG)
def get_listening_history(request):
    """Get processed listening history for a user."""
    try:
        if request.method == "OPTIONS":
            return ("", 204)

        user_id = request.args.get("user_id")
        if not user_id:
            return jsonify({"error": "Missing user_id"}), 400

        # Get user's access token
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()

        if not user_doc.exists:
            return jsonify({"error": "User not found"}), 404

        user_data = user_doc.to_dict()
        access_token = user_data.get("access_token")

        # Fetch recently played tracks from Spotify
        response = requests.get(
            "https://api.spotify.com/v1/me/player/recently-played?limit=50",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch tracks"}), response.status_code

        tracks_data = response.json().get("items", [])

        # Process and store history
        processed_data = process_listening_history(user_id, tracks_data)
        
        # Extract directly from processed_data to avoid nesting
        return jsonify({
            "history": processed_data["history"],  # This should be the array directly
            "totalHours": processed_data["total_hours"]
        }), 200

    except Exception as e:
        print(f"Error in get_listening_history: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
@functions_framework.http
@cross_origin(**CORS_CONFIG)
def get_recommendations(request):
    """Get personalized track recommendations using multiple strategies"""
    try:
        user_id = request.args.get("user_id")
        print(f"Processing recommendations for user_id: {user_id}")
        
        # Get user data and validate
        user_data = get_user_data(user_id)
        access_token = user_data.get("access_token")
        
        if not access_token:
            return jsonify({"error": "No access token found"}), 401
            
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Initialize recommendation engine
        recommender = SpotifyRecommender(headers)
        
        # Get seed data
        top_artists = recommender.get_top_artists(limit=3)
        top_tracks = recommender.get_top_tracks(limit=2)
        
        # Generate recommendations using different strategies
        recommendations = []
        seen_tracks = set()
        
        # Strategy 1: Genre-based discovery
        genre_tracks = recommender.get_genre_based_tracks(top_artists)
        recommendations.extend(filter_unique_tracks(genre_tracks, seen_tracks))
        
        # Strategy 2: Similar artists' tracks
        similar_artist_tracks = recommender.get_similar_artist_tracks(top_artists)
        recommendations.extend(filter_unique_tracks(similar_artist_tracks, seen_tracks))
        
        # Strategy 3: New releases in preferred genres
        new_releases = recommender.get_new_releases_in_genres(extract_genres(top_artists))
        recommendations.extend(filter_unique_tracks(new_releases, seen_tracks))
        
        # Strategy 4: Rising artists in similar genres
        rising_tracks = recommender.get_rising_artist_tracks(extract_genres(top_artists))
        recommendations.extend(filter_unique_tracks(rising_tracks, seen_tracks))
        
        # Balance and diversify recommendations
        final_recommendations = balance_recommendations(recommendations)
        
        # Log recommendation metrics
        log_recommendation_metrics(final_recommendations, user_id)
        
        return jsonify({"tracks": final_recommendations}), 200
        
    except Exception as e:
        print(f"Error in get_recommendations: {str(e)}")
        return jsonify({"error": str(e)}), 500

class SpotifyRecommender:
    def __init__(self, headers):
        self.headers = headers
        
    def get_top_artists(self, limit=3):
        response = requests.get(
            f"https://api.spotify.com/v1/me/top/artists",
            headers=self.headers,
            params={"limit": limit, "time_range": "medium_term"}
        )
        return response.json().get('items', []) if response.status_code == 200 else []
        
    def get_top_tracks(self, limit=2):
        response = requests.get(
            f"https://api.spotify.com/v1/me/top/tracks",
            headers=self.headers,
            params={"limit": limit, "time_range": "medium_term"}
        )
        return response.json().get('items', []) if response.status_code == 200 else []
        
    def get_genre_based_tracks(self, seed_artists, tracks_per_genre=3):
        genres = extract_genres(seed_artists)
        tracks = []
        
        for genre in genres[:3]:  # Limit to top 3 genres
            search_response = requests.get(
                "https://api.spotify.com/v1/search",
                headers=self.headers,
                params={
                    "q": f"genre:{genre}",
                    "type": "track",
                    "limit": tracks_per_genre,
                    "market": "US"
                }
            )
            if search_response.status_code == 200:
                tracks.extend(process_track_results(search_response.json().get('tracks', {}).get('items', [])))
                
        return tracks
        
    def get_similar_artist_tracks(self, seed_artists):
        tracks = []
        for artist in seed_artists:
            # Get related artists
            related_response = requests.get(
                f"https://api.spotify.com/v1/artists/{artist['id']}/related-artists",
                headers=self.headers
            )
            if related_response.status_code == 200:
                related_artists = related_response.json().get('artists', [])[:3]
                for related_artist in related_artists:
                    # Get their top tracks
                    top_tracks_response = requests.get(
                        f"https://api.spotify.com/v1/artists/{related_artist['id']}/top-tracks?market=US",
                        headers=self.headers
                    )
                    if top_tracks_response.status_code == 200:
                        tracks.extend(process_track_results(top_tracks_response.json().get('tracks', [])[:2]))
        
        return tracks
        
    def get_new_releases_in_genres(self, genres):
        tracks = []
        for genre in genres[:3]:
            search_response = requests.get(
                "https://api.spotify.com/v1/search",
                headers=self.headers,
                params={
                    "q": f"genre:{genre} year:{datetime.now().year}",
                    "type": "track",
                    "limit": 3,
                    "market": "US"
                }
            )
            if search_response.status_code == 200:
                tracks.extend(process_track_results(search_response.json().get('tracks', {}).get('items', [])))
        
        return tracks
        
    def get_rising_artist_tracks(self, genres):
        tracks = []
        for genre in genres[:3]:
            search_response = requests.get(
                "https://api.spotify.com/v1/search",
                headers=self.headers,
                params={
                    "q": f"genre:{genre}",
                    "type": "artist",
                    "limit": 3,
                    "market": "US"
                }
            )
            if search_response.status_code == 200:
                rising_artists = [
                    artist for artist in search_response.json().get('artists', {}).get('items', [])
                    if 20 <= artist.get('popularity', 0) <= 60  # Medium popularity artists
                ]
                for artist in rising_artists:
                    top_tracks_response = requests.get(
                        f"https://api.spotify.com/v1/artists/{artist['id']}/top-tracks?market=US",
                        headers=self.headers
                    )
                    if top_tracks_response.status_code == 200:
                        tracks.extend(process_track_results(top_tracks_response.json().get('tracks', [])[:1]))
        
        return tracks

def process_track_results(tracks):
    """Process track results into a standardized format"""
    return [{
        'id': track['id'],
        'name': track['name'],
        'artists': [artist['name'] for artist in track['artists']],
        'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None,
        'preview_url': track['preview_url'],
        'external_url': track['external_urls']['spotify'],
        'popularity': track['popularity'],
        'release_date': track['album']['release_date']
    } for track in tracks]

def filter_unique_tracks(tracks, seen_tracks):
    """Filter out tracks that have already been seen"""
    unique_tracks = []
    for track in tracks:
        if track['id'] not in seen_tracks:
            unique_tracks.append(track)
            seen_tracks.add(track['id'])
    return unique_tracks

def balance_recommendations(tracks, target_size=20):
    """Balance recommendations for diversity"""
    if not tracks:
        return []
    
    # Sort by multiple factors
    def score_track(track):
        popularity = track['popularity']
        is_recent = track['release_date'].startswith(str(datetime.now().year))
        return (
            0.4 * popularity +  # Weight popularity less
            0.3 * (100 if is_recent else 50) +  # Boost recent tracks
            0.3 * random.randint(0, 100)  # Add randomness
        )
    
    tracks.sort(key=score_track, reverse=True)
    
    # Ensure genre diversity
    genres_seen = set()
    diverse_tracks = []
    
    for track in tracks:
        artist_genres = set()  # You'd need to fetch this from artist data
        if len(genres_seen.intersection(artist_genres)) < 2:  # Allow some genre overlap
            diverse_tracks.append(track)
            genres_seen.update(artist_genres)
    
    return diverse_tracks[:target_size]


def get_top_artists(headers):
    """Get user's top artists"""
    response = requests.get(
        "https://api.spotify.com/v1/me/top/artists",
        headers=headers,
        params={"limit": 5, "time_range": "medium_term"}
    )
    if response.status_code != 200:
        return []
    return response.json().get('items', [])

def extract_genres(artists):
    """Extract unique genres from artists"""
    genres = set()
    for artist in artists:
        genres.update(artist.get('genres', []))
    return list(genres)

def perform_search(headers, query, filters=None):
    """Perform a Spotify search with filters"""
    params = {
        "q": query,
        "type": "track",
        "limit": 5,
        "market": "US"
    }
    if filters:
        params["q"] = f"{params['q']} {filters}"
    
    return requests.get(
        "https://api.spotify.com/v1/search",
        headers=headers,
        params=params
    )

def process_search_results(response, all_tracks, seen_ids, seen_artists, max_per_artist=1):
    """Process search results with artist and duplicate filtering"""
    if response.status_code != 200:
        return
        
    tracks = response.json().get('tracks', {}).get('items', [])
    for track in tracks:
        if track['id'] not in seen_ids:
            primary_artist = track['artists'][0]['name']
            if seen_artists.get(primary_artist, 0) < max_per_artist:
                all_tracks.append({
                    'id': track['id'],
                    'name': track['name'],
                    'artists': [artist['name'] for artist in track['artists']],
                    'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None,
                    'preview_url': track['preview_url'],
                    'external_url': track['external_urls']['spotify'],
                    'popularity': track['popularity'],
                    'release_date': track['album']['release_date']
                })
                seen_ids.add(track['id'])
                seen_artists[primary_artist] = seen_artists.get(primary_artist, 0) + 1

def balance_recommendations(tracks, target_size=20):
    """Balance recommendations by popularity and release date"""
    if not tracks:
        return []
        
    # Sort by popularity and date
    tracks.sort(key=lambda x: (x['popularity'], x['release_date']), reverse=True)
    
    # Create balanced selection
    high_pop = [t for t in tracks if t['popularity'] >= 70][:4]
    med_pop = [t for t in tracks if 40 <= t['popularity'] < 70][:4]
    low_pop = [t for t in tracks if t['popularity'] < 40][:2]
    
    balanced = high_pop + med_pop + low_pop
    
    # Ensure we have enough tracks
    while len(balanced) < target_size and tracks:
        remaining = [t for t in tracks if t not in balanced]
        if not remaining:
            break
        balanced.append(remaining[0])
    
    # Shuffle the final selection
    import random
    random.shuffle(balanced)
    
    return balanced[:target_size]

def log_recommendation_metrics(tracks, user_id):
    """Log recommendation metrics to Firestore"""
    metrics = {
        'timestamp': datetime.now(),
        'total_tracks': len(tracks),
        'tracks_with_preview': len([t for t in tracks if t['preview_url']]),
        'unique_artists': len(set(artist for t in tracks for artist in t['artists'])),
        'avg_popularity': sum(t['popularity'] for t in tracks) / len(tracks),
        'popularity_distribution': {
            'high': len([t for t in tracks if t['popularity'] >= 70]),
            'medium': len([t for t in tracks if 40 <= t['popularity'] < 70]),
            'low': len([t for t in tracks if t['popularity'] < 40])
        },
        'release_dates': {
            'newest': max(t['release_date'] for t in tracks),
            'oldest': min(t['release_date'] for t in tracks)
        }
    }
    
    db = firestore.Client()
    metrics_ref = db.collection('metrics').document(user_id).collection('recommendations')
    metrics_ref.add(metrics)
    