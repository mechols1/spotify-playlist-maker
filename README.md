# Spotify Playlist Curator - Development Guide

## Quick Start
# Local Development Setup
1. Install required tools:
   - Node.js (v16+)
   - Python 3.9+
   - Google Cloud CLI

2. Clone and configure:
   ```bash
   git clone [repo-url]
   cd spotify-playlist-curator
    ```
3. Frontend Setup
    ```bash
    cd frontend
    npm install
    cp .env.example .env
    ```

4. Backend setup
    ```bash
    cd backend
    pip install -r requirements.txt
   ```
5. Environment Variables:
    - Create env.yaml for Cloud Functions
    Required variables:

    SPOTIFY_CLIENT_ID
    SPOTIFY_CLIENT_SECRET
    FRONTEND_URL
    REDIRECT_URI
6. Google Cloud Setup:

    - Install gcloud CLI
    - Configure project: gcloud config set project [PROJECT_ID]
    - Enable required APIs
    - Set up Firebase
7. Setup Spotify Developer Account (If you already have a spotify account just log in with that)
    Needed Variables: 
    - SPOTIFY_CLIENT_ID
    - SPOTIFY_CLIENT_SECRET

## Project Structure
- `/frontend`: React application
- `/backend`: Cloud Functions
- `/firebase`: Firestore rules

## Development Workflow
1. Branch from `dev`
2. Create PR for review
3. Merge to `dev` after approval

## Common Issues & Solutions
