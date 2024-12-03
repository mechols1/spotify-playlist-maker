// src/components/auth/LoginButton.js
import React, { useState, useEffect } from 'react';
import { getSpotifyAuthUrl } from '../../config/spotify';

function LoginButton() {
  const [error, setError] = useState(null);
  const [debugInfo, setDebugInfo] = useState({});

  useEffect(() => {
    // Collect debug information
    setDebugInfo({
      clientId: process.env.REACT_APP_SPOTIFY_CLIENT_ID ? 'Present' : 'Missing',
      redirectUri: process.env.REACT_APP_API_URI ? 'Present' : 'Missing',
      nodeEnv: process.env.NODE_ENV
    });
  }, []);

  const handleLogin = () => {
    try {
      const authUrl = getSpotifyAuthUrl();
      if (!authUrl) {
        setError('Failed to generate authentication URL');
        return;
      }
      console.log('Redirecting to:', authUrl);
      window.location.href = authUrl;
    } catch (err) {
      console.error('Login error:', err);
      setError(`Login error: ${err.message}`);
    }
  };

  return (
    <div className="flex flex-col items-center">
      <button
        onClick={handleLogin}
        className="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded mb-4"
      >
        Login with Spotify
      </button>
      
      {error && (
        <div className="mt-2 p-2 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}
      
      {/* Debug information */}
      <div className="mt-4 p-4 bg-gray-800 rounded text-sm text-gray-300">
        <pre>{JSON.stringify(debugInfo, null, 2)}</pre>
      </div>
    </div>
  );
}

export default LoginButton;