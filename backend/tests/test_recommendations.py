# test_recommendations.py
import requests
import os
from google.cloud import firestore
import time

def test_recommendations():
    print("Starting test...")
    
    # Initialize Firestore client
    print("Connecting to Firestore...")
    db = firestore.Client()
    
    # Get a test user from Firestore
    print("Fetching test user...")
    users_ref = db.collection('users')
    users = users_ref.limit(1).stream()
    test_user = next(users)
    user_data = test_user.to_dict()
    
    print(f"Found user: {test_user.id}")
    print("Access token available:", bool(user_data.get('access_token')))
    
    FUNCTION_URL = "https://us-central1-music-curator-442401.cloudfunctions.net/get_recommendations"
    
    params = {
        "user_id": test_user.id
    }
    
    headers = {
        "Authorization": f"Bearer {user_data.get('access_token')}",
        "Content-Type": "application/json"
    }
    
    try:
        print("\nMaking request to function...")
        start_time = time.time()
        
        # Set a longer timeout (30 seconds)
        response = requests.get(FUNCTION_URL, 
                              params=params, 
                              headers=headers, 
                              timeout=30)
        
        end_time = time.time()
        print(f"Request took {end_time - start_time:.2f} seconds")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\nSuccessful Response:")
            for i, track in enumerate(data.get('tracks', []), 1):
                print(f"\nTrack {i}:")
                print(f"Name: {track.get('name')}")
                print(f"Artists: {', '.join(track.get('artists', []))}")
        else:
            print("\nError Response:")
            print(response.text)
            
    except requests.exceptions.Timeout:
        print("Request timed out after 30 seconds")
    except Exception as e:
        print(f"Error testing function: {str(e)}")

if __name__ == "__main__":
    test_recommendations()