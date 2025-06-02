# test_top_artists.py
from google.cloud import firestore
import requests
import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
import pytz
from dotenv import load_dotenv
import yaml

# Set environment variables if not already set
if not os.getenv("GOOGLE_CLOUD_PROJECT"):
    os.environ["GOOGLE_CLOUD_PROJECT"] = "music-curator-442401"

if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/markechols099/key.json"

# Add your project root to PYTHONPATH if needed
sys.path.append(str(Path(__file__).parent.parent))

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

def load_environment():
    """Load environment variables from YAML file"""
    project_root = Path(__file__).parent.parent
    yaml_paths = [
        project_root / ".env.yaml",
        project_root / "backend" / ".env.yaml",
        Path(os.getcwd()) / ".env.yaml",
    ]

    for yaml_path in yaml_paths:
        if yaml_path.exists():
            print(f"Found .env.yaml file at: {yaml_path}")
            try:
                with open(yaml_path, "r") as file:
                    env_vars = yaml.safe_load(file)
                    if env_vars:
                        for key, value in env_vars.items():
                            os.environ[key] = str(value)
                        return True
            except Exception as e:
                print(f"Error loading YAML file: {e}")
                continue
    return False

def refresh_token_if_needed(user_data):
    """Refresh token if expired and return the latest access token"""
    token_expiry = user_data.get("token_expiry")
    if not token_expiry:
        print("No token expiry found in user data")
        return None

    # Convert token_expiry to UTC datetime if it's a timestamp
    if isinstance(token_expiry, (int, float)):
        token_expiry = datetime.fromtimestamp(token_expiry).replace(tzinfo=pytz.UTC)
    elif isinstance(token_expiry, datetime):
        if token_expiry.tzinfo is None:
            token_expiry = token_expiry.replace(tzinfo=pytz.UTC)

    current_time = datetime.now(pytz.UTC)

    print(f"\nDebug Token Info:")
    print(f"Current Time (UTC): {current_time}")
    print(f"Token Expiry (UTC): {token_expiry}")
    print(f"Refresh Token Present: {'Yes' if user_data.get('refresh_token') else 'No'}")

    if current_time + timedelta(minutes=5) >= token_expiry:
        try:
            print("\nAttempting token refresh...")
            refresh_token = user_data.get("refresh_token")
            if not refresh_token:
                print("No refresh token found")
                return None

            # Print client credentials status (safely)
            client_id = os.getenv("SPOTIFY_CLIENT_ID", "")
            client_secret = os.getenv("SPOTIFY_CLIENT_SECRET", "")
            print(f"Client ID present: {'Yes' if client_id else 'No'}")
            print(f"Client Secret present: {'Yes' if client_secret else 'No'}")
            print(f"Client ID length: {len(client_id)}")
            print(f"Client Secret length: {len(client_secret)}")

            response = requests.post(
                "https://accounts.spotify.com/api/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": client_id,
                    "client_secret": client_secret,
                },
            )

            print(f"\nToken Refresh Response:")
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            print(f"Response Body: {response.text}")

            if response.status_code != 200:
                print("Token refresh failed")
                return None

            token_info = response.json()

            db = firestore.Client()
            user_ref = db.collection("users").document(user_data["spotify_id"])
            new_expiry = current_time + timedelta(seconds=token_info["expires_in"])

            user_ref.update(
                {
                    "access_token": token_info["access_token"],
                    "token_expiry": new_expiry,
                    "last_updated": current_time,
                }
            )

            return token_info["access_token"]
        except Exception as e:
            print(f"\nError details:")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            if hasattr(e, "__traceback__"):
                import traceback

                print(f"Traceback:\n{traceback.format_exc()}")
            return None

    return user_data.get("access_token")




def test_get_top_artists():
    """Test the get_top_artists functionality"""
    print("\n=== Starting Top Artists Test ===")
    print(f"Timestamp: {datetime.now(pytz.UTC)}")

    try:
        # Load environment
        print("\n1. Loading environment...")
        if not load_environment():
            raise EnvironmentError("Failed to load environment variables")

        # Initialize Firestore
        print("\n2. Initializing Firestore...")
        db = firestore.Client()
        print(" ✓ Firestore initialized")

        # Get test user
        print("\n3. Getting test user...")
        users_ref = db.collection("users")
        users = list(users_ref.limit(1).stream())
        if not users:
            raise ValueError("No users found in Firestore")
        
        test_user = users[0].to_dict()
        print(f" ✓ User found: {test_user.get('display_name', 'Unknown')}")

        # Refresh token
        print("\n4. Refreshing access token...")
        access_token = refresh_token_if_needed(test_user)
        if not access_token:
            raise ValueError("Failed to refresh access token")
        print(" ✓ Valid access token obtained")

        # Test get_top_artists
        print("\n5. Testing get_top_artists...")
        headers = {"Authorization": f"Bearer {access_token}"}
        top_artists = get_top_artists(headers)
        
        print(f"\nResponse Analysis:")
        print(f"Status: {'Success' if top_artists else 'Failure'}")
        print(f"Number of artists retrieved: {len(top_artists)}")
        
        if top_artists:
            print("\nArtist Details:")
            for idx, artist in enumerate(top_artists[:5], 1):  # Print first 3 for sample
                print(f"{idx}. {artist.get('name', 'Unknown')}")
                print(f"   Genres: {', '.join(artist.get('genres', []))}")
                print(f"   Popularity: {artist.get('popularity', 'N/A')}")
                print(f"   Followers: {artist.get('followers', {}).get('total', 'N/A')}")
                print(f"   Spotify URL: {artist.get('external_urls', {}).get('spotify', 'N/A')}")
                print("-" * 40)

        # Validation checks
        print("\n6. Running validation checks...")
        assert isinstance(top_artists, list), "Response should be a list"
        assert len(top_artists) <= 5, "Should return max 5 artists"
        
        if top_artists:
            first_artist = top_artists[0]
            assert 'name' in first_artist, "Artist missing name"
            assert 'id' in first_artist, "Artist missing ID"
            assert 'genres' in first_artist, "Artist missing genres"
            assert 'popularity' in first_artist, "Artist missing popularity"
            
        print(" ✓ All basic validation checks passed")

    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}")
        raise e
    finally:
        print("\n=== Test Completed ===")

if __name__ == "__main__":
    print("Running top artists test...")
    test_get_top_artists()