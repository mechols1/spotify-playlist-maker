from datetime import datetime, timedelta
from google.cloud import firestore
from google.api_core import retry
import pytz

# Initialize Firestore with retry configuration
db = firestore.Client()

def process_listening_history(user_id, tracks_data):
    """Process and store listening history for a user"""
    # Make sure we use UTC timezone consistently
    now = datetime.now(pytz.UTC)
    history = []
    total_ms = 0
    
    # Initialize 7-day history
    for i in range(7):
        date = now - timedelta(days=i)
        history.append({
            'date': date.strftime('%a'),
            'count': 0,
            'duration_ms': 0,
            'timestamp': date.timestamp()  # UTC timestamp
        })
    
    # Process tracks
    for track in tracks_data:
        # Convert the played_at string to a timezone-aware datetime
        played_at = datetime.fromisoformat(track['played_at'].replace('Z', '+00:00'))
        if played_at.tzinfo is None:
            played_at = pytz.UTC.localize(played_at)
            
        duration_ms = track['track']['duration_ms']
        total_ms += duration_ms
        
        days_ago = (now - played_at).days
        if 0 <= days_ago < 7:
            history[days_ago]['count'] += 1
            history[days_ago]['duration_ms'] += duration_ms
    
    total_hours = round(total_ms / (1000 * 60 * 60), 1)
    
    # Store in Firestore
    analytics_ref = db.collection('users').document(user_id).collection('analytics')
    
    # Store daily history - convert to dict for Firestore
    analytics_ref.document('listening_history').set({
        'daily_counts': [{
            'date': day['date'],
            'count': day['count'],
            'duration_ms': day['duration_ms'],
            'timestamp': day['timestamp']
        } for day in history[::-1]],
        'last_updated': now
    })
    
    # Store listening time
    analytics_ref.document('listening_stats').set({
        'total_listening_time_ms': total_ms,
        'total_listening_hours': total_hours,
        'last_updated': now
    })
    
    return {
        'history': [{
            'date': day['date'],
            'count': day['count'],
            'duration_ms': day['duration_ms'],
            'timestamp': day['timestamp']
        } for day in history[::-1]],
        'total_hours': total_hours
    }
    
def get_listening_stats(user_id):
    """Get user's listening statistics"""
    try:
        stats_ref = db.collection('users').document(user_id)\
                     .collection('analytics').document('listening_stats')
        stats = stats_ref.get()
        
        if not stats.exists:
            return {'total_hours': 0}
            
        data = stats.to_dict()
        return {
            'total_hours': data.get('total_listening_hours', 0)
        }
    except Exception as e:
        print(f"Error fetching listening stats: {e}")
        return {'total_hours': 0}