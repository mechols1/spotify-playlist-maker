# test_recommendations.py
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

print("Test file is being executed")
try:
    print("Checking imports...")
    print("All imports successful")
except Exception as e:
    print(f"Import error: {e}")
print("Test file is being executed")

try:
    print("Checking imports...")
    print("All imports successful")
except Exception as e:
    print(f"Import error: {e}")


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
                        # Set environment variables from YAML
                        for key, value in env_vars.items():
                            os.environ[key] = str(value)
                        return True
            except Exception as e:
                print(f"Error loading YAML file: {e}")
                continue

    print("Warning: No .env.yaml file found in common locations")
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


def test_recommendations():
    """Test the recommendations functionality"""
    print("\n=== Starting Recommendations Test ===")
    print(f"Timestamp: {datetime.now(pytz.UTC)}")

    try:
        # First load environment variables
        print("\nLoading environment variables...")
        load_environment()

        # Then check environment
        print("\n1. Checking Environment:")
        required_env = [
            "GOOGLE_CLOUD_PROJECT",
            "GOOGLE_APPLICATION_CREDENTIALS",
            "SPOTIFY_CLIENT_ID",
            "SPOTIFY_CLIENT_SECRET",
        ]

        missing_vars = []
        env_status = {}

        for env in required_env:
            value = os.getenv(env)
            env_status[env] = value is not None
            if value:
                # For sensitive values, only show length
                if "SECRET" in env or "KEY" in env:
                    print(f"{env}: ✓ Set (length: {len(value)})")
                else:
                    print(f"{env}: ✓ Set ({value})")
            else:
                print(f"{env}: ✗ Missing")
                missing_vars.append(env)

        if missing_vars:
            print("\nMissing required environment variables:")
            print("Current working directory:", os.getcwd())
            print("Searched .env.yaml locations:")
            for yaml_path in [
                Path(__file__).parent.parent / ".env.yaml",
                Path(__file__).parent.parent / "backend" / ".env.yaml",
                Path(os.getcwd()) / ".env.yaml",
            ]:
                print(
                    f"- {yaml_path} ({'exists' if yaml_path.exists() else 'not found'})"
                )
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

        # Load environment if needed
        if not os.getenv("SPOTIFY_CLIENT_ID") or not os.getenv("SPOTIFY_CLIENT_SECRET"):
            if not load_environment():
                raise EnvironmentError(
                    "Failed to load Spotify credentials from environment"
                )

        # 2. Firestore Connection Test
        print("\n2. Testing Firestore Connection:")
        db = firestore.Client()
        print(" ✓ Firestore client initialized")

        # 3. Get Test User
        print("\n3. Fetching Test User:")
        users_ref = db.collection("users")
        users = list(users_ref.limit(1).stream())
        if not users:
            raise ValueError("No users found in Firestore")

        test_user = users[0]
        user_data = test_user.to_dict()
        print(f"✓ Found user: {test_user.id}")

        # 4. Validate Access Token
        print("\n4. Validating Access Token:")
        access_token = refresh_token_if_needed(user_data)
        if not access_token:
            raise ValueError("Failed to refresh access token")
        print("✓ Access token refreshed")

        # 5. Test Spotify API Connection
        print("\n5. Testing Spotify API Connection:")
        auth_response = requests.get(
            "https://api.spotify.com/v1/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        print(f"Auth check status: {auth_response.status_code}")
        if auth_response.status_code != 200:
            raise ValueError(
                f"Failed to authenticate with Spotify. Status: {auth_response.status_code}"
            )

        # 6. Test Recommendations Endpoint
        print("\n6. Testing Recommendations Endpoint:")
        FUNCTION_URL = "https://us-central1-music-curator-442401.cloudfunctions.net/get_recommendations"

        print(f"Making request to: {FUNCTION_URL}")
        print(f"User ID: {test_user.id}")

        params = {"user_id": test_user.id}
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        print("Sending request...")
        response = requests.get(FUNCTION_URL, params=params, headers=headers, timeout=30)

        print(f"\nResponse Details:")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {json.dumps(dict(response.headers), indent=2)}")

        # Enhanced response validation
        try:
            response_data = response.json()
            print("\nResponse Data Analysis:")
            
            if "tracks" in response_data:
                tracks = response_data["tracks"]
                print(f"Total tracks received: {len(tracks)}")
                
                # Analyze recommendation diversity
                unique_artists = set()
                genres = set()
                popularity_ranges = {
                    "high": 0,    # 70-100
                    "medium": 0,  # 40-69
                    "low": 0      # 0-39
                }
                
                print("\nAnalyzing recommendation diversity:")
                for track in tracks:
                    # Artist diversity
                    for artist in track.get("artists", []):
                        unique_artists.add(artist)
                    
                    # Popularity distribution
                    popularity = track.get("popularity", 0)
                    if popularity >= 70:
                        popularity_ranges["high"] += 1
                    elif popularity >= 40:
                        popularity_ranges["medium"] += 1
                    else:
                        popularity_ranges["low"] += 1

                print(f"Unique artists: {len(unique_artists)}")
                print("Popularity distribution:")
                for range_name, count in popularity_ranges.items():
                    print(f"- {range_name}: {count} tracks ({(count/len(tracks))*100:.1f}%)")

                # Validate required fields
                required_fields = [
                    "id", "name", "artists", "image_url", "preview_url",
                    "external_url", "popularity", "release_date"
                ]
                
                print("\nValidating track data:")
                for i, track in enumerate(tracks):
                    missing_fields = [field for field in required_fields if field not in track]
                    if missing_fields:
                        print(f"✗ Track {i} missing fields: {missing_fields}")
                    else:
                        print(f"✓ Track {i} has all required fields")

                # Check for duplicates
                track_ids = [track["id"] for track in tracks]
                duplicates = set([id for id in track_ids if track_ids.count(id) > 1])
                if duplicates:
                    print(f"\n⚠️ Found duplicate tracks: {len(duplicates)} duplicates")
                else:
                    print("\n✓ No duplicate tracks found")

            else:
                print("✗ Response missing 'tracks' array")
                print("Full response:")
                print(json.dumps(response_data, indent=2))

        except ValueError as e:
            print(f"Failed to parse JSON response: {str(e)}")
            print(f"Raw response: {response.text[:500]}...")

    except Exception as e:
        print(f"\n❌ Error during test: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}")
        raise e

if __name__ == "__main__":
    print("Running test as main")
    test_recommendations()