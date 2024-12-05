# test_recommendations.py
from google.cloud import firestore
import requests
import os
import sys
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
    print("Starting recommendations test...")
    print("Test function started")

    try:
        print("\nChecking environment...")
        print(f"Current working directory: {os.getcwd()}")
        print(f"GOOGLE_CLOUD_PROJECT: {os.getenv('GOOGLE_CLOUD_PROJECT')}")
        print(
            f"GOOGLE_APPLICATION_CREDENTIALS: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}"
        )

        # Initialize Firestore client
        print("\nInitializing Firestore client...")
        db = firestore.Client()
        print("✓ Firestore client initialized successfully")

        # Get test user
        print("\nAttempting to access users collection...")
        users_ref = db.collection("users")
        users = list(users_ref.limit(1).stream())

        if not users:
            print("No users found in the collection!")
            return

        test_user = users[0]
        user_data = test_user.to_dict()
        print(f"✓ Found user: {test_user.id}")

        # Validate access token
        access_token = user_data.get("access_token")
        if not access_token:
            print("⚠ No access token found for user!")
            return

        print("\nAccess token is available")

        # Test recommendations endpoint
        print("\nTesting recommendations endpoint...")
        FUNCTION_URL = "https://us-central1-music-curator-442401.cloudfunctions.net/get_recommendations"

        params = {"user_id": test_user.id}
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        print(f"Making request for user_id: {test_user.id}")
        response = requests.get(
            FUNCTION_URL, params=params, headers=headers, timeout=30
        )

        print(f"Response Status Code: {response.status_code}")

        try:
            response_data = response.json()
            print("Response Data:", response_data)
        except ValueError:
            print("Could not parse JSON response")
            print("Raw Response:", response.text)

        if response.status_code != 200:
            print("Error Response Headers:", dict(response.headers))

    except Exception as e:
        print(f"\n⚠ Error during test: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        raise e


# This is crucial - it makes sure the test runs when you execute the file
if __name__ == "__main__":
    print("Running test as main")
    test_recommendations()
