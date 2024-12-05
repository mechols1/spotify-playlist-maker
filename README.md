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
```
GOOGLE_CLOUD_PROJECT=your-project-id-here
SPOTIFY_CLIENT_ID=your-spotify-client-id
SPOTIFY_CLIENT_SECRET=your-spotify-client-secret
```
6. Google Cloud Setup:

    - Install gcloud CLI
    - Configure project: gcloud config set project [PROJECT_ID]
    - Enable required APIs
    - Set up Firebase
    - Enable required APIS:
        ```bash
        gcloud services enable \
        cloudfunctions.googleapis.com \
        cloudbuild.googleapis.com \
        artifactregistry.googleapis.com
        ```
    - When you change functions, make sure they're redeployed. Some examples:
        ```bash
        # Auth Functions
        gcloud functions deploy refresh-token \
        --runtime python39 \
        --trigger-http \
        --allow-unauthenticated \
        --env-vars-file env.yaml \
        --entry-point refresh_spotify_token

        # Analytics Functions
        gcloud functions deploy get_listening_history \
        --runtime python39 \
        --trigger-http \
        --allow-unauthenticated \
        --env-vars-file env.yaml \
        --entry-point get_listening_history

        gcloud functions deploy get_listening_stats \
        --runtime python39 \
        --trigger-http \
        --allow-unauthenticated \
        --env-vars-file env.yaml \
        --entry-point get_listening_stats
        ```
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
