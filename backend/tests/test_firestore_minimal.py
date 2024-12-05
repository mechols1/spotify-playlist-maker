# test_firestore_minimal.py
from google.cloud import firestore
import os
import sys
from pathlib import Path

def test_minimal_connection():
    # Print environment info
    print("Current directory:", os.getcwd())
    print("Python path:", sys.path)
    print(f"Project ID: {os.getenv('GOOGLE_CLOUD_PROJECT', 'Not set')}")
    
    try:
        print("\nInitializing Firestore client...")
        db = firestore.Client()
        print("Client initialized successfully")
        
        print("\nTrying to list collections...")
        collections = list(db.collections())
        print(f"Found {len(collections)} collections")
        
        for collection in collections:
            print(f"Collection: {collection.id}")
            
    except Exception as e:
        print(f"\nError occurred: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        
        if hasattr(e, 'message'):
            print(f"Detailed message: {e.message}")

if __name__ == "__main__":
    # Add parent directory to Python path
    parent_dir = str(Path(__file__).parent.parent)
    if parent_dir not in sys.path:
        sys.path.append(parent_dir)
    
    test_minimal_connection()