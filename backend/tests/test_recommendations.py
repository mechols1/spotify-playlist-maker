# test_recommendations.py
from google.cloud import firestore
import requests
import os
import sys
import json
from datetime import datetime
from pathlib import Path

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


def test_recommendations():
    print("\n=== Starting Recommendations Test ===")
    print(f"Timestamp: {datetime.now()}")

    try:
        # 1. Environment Check
        print("\n1. Checking Environment:")
        required_env = ['GOOGLE_CLOUD_PROJECT', 'GOOGLE_APPLICATION_CREDENTIALS']
        for env in required_env:
            value = os.getenv(env)
            print(f"{env}: {'✓ Set' if value else '✗ Missing'}")
            if not value:
                raise EnvironmentError(f"Missing required environment variable: {env}")

        # 2. Firestore Connection Test
        print("\n2. Testing Firestore Connection:")
        db = firestore.Client()
        print("✓ Firestore client initialized")

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
        access_token = user_data.get("access_token")
        if not access_token:
            raise ValueError("No access token found for user")

        # 5. Test Spotify API Connection
        print("\n5. Testing Spotify API Connection:")
        auth_response = requests.get(
            "https://api.spotify.com/v1/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        print(f"Auth check status: {auth_response.status_code}")
        if auth_response.status_code != 200:
            raise ValueError(f"Failed to authenticate with Spotify. Status: {auth_response.status_code}")

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
        
        try:
            response_data = response.json()
            print("\nResponse Data:")
            if 'tracks' in response_data:
                print(f"Number of tracks received: {len(response_data['tracks'])}")
                # Print first track as example
                if response_data['tracks']:
                    print("\nExample Track:")
                    print(json.dumps(response_data['tracks'][0], indent=2))
            else:
                print("No tracks in response")
                print("Full response:")
                print(json.dumps(response_data, indent=2))
        except ValueError as e:
            print(f"Failed to parse JSON response: {str(e)}")
            print(f"Raw response: {response.text[:500]}...")

        # 7. Validate Response Data
        print("\n7. Validating Response Data:")
        if response.status_code == 200:
            if 'tracks' in response_data:
                print("✓ Response contains tracks array")
                for i, track in enumerate(response_data['tracks']):
                    required_fields = ['id', 'name', 'artists']
                    missing_fields = [field for field in required_fields if field not in track]
                    if missing_fields:
                        print(f"✗ Track {i} missing required fields: {missing_fields}")
                    else:
                        print(f"✓ Track {i} has all required fields")
            else:
                print("✗ Response missing 'tracks' array")
        else:
            print(f"✗ Request failed with status code: {response.status_code}")

    except Exception as e:
        print(f"\n❌ Error during test: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}")
        raise e



if __name__ == "__main__":
    print("Running test as main")
    test_recommendations()
