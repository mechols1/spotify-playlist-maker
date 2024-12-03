// src/config/spotify.js

const config = {
  clientId: process.env.REACT_APP_SPOTIFY_CLIENT_ID,
  redirectUri: process.env.REACT_APP_API_URI,
  scopes: [
    'user-read-private',
    'user-read-email',
    'playlist-read-private',
    'playlist-modify-public',
    'playlist-modify-private',
    'user-top-read',
    'user-read-recently-played'
  ]
};

export const getSpotifyAuthUrl = () => {
  // Debug logging
  console.log('Environment Variables:', {
    clientId: process.env.REACT_APP_SPOTIFY_CLIENT_ID ? 'Present' : 'Missing',
    redirectUri: process.env.REACT_APP_API_URI ? 'Present' : 'Missing'
  });

  if (!config.clientId) {
    console.error('Missing Spotify Client ID. Make sure REACT_APP_SPOTIFY_CLIENT_ID is set in your .env file');
    return null;
  }

  if (!config.redirectUri) {
    console.error('Missing Redirect URI. Make sure REACT_APP_API_URI is set in your .env file');
    return null;
  }
  
  const scopes = config.scopes.join(' ');
  const authUrl = `https://accounts.spotify.com/authorize?client_id=${config.clientId}&response_type=code&redirect_uri=${encodeURIComponent(config.redirectUri)}&scope=${encodeURIComponent(scopes)}`;
  
  console.log('Generated Auth URL:', authUrl); // For debugging
  return authUrl;
};

export default config;