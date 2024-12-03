// /frontend/src/hooks/useSpotifyToken.js
import { useState, useEffect, useCallback } from 'react';

export const useSpotifyToken = () => {
  const [accessToken, setAccessToken] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const refreshToken = useCallback(async () => {
    try {
      const userId = localStorage.getItem('spotify_user_id');
      console.log('Attempting token refresh for user:', userId);
      
      if (!userId) {
        console.log('No user ID found in localStorage');
        throw new Error('No user ID found');
      }

      console.log('Making refresh token request...');
      const response = await fetch('https://us-central1-music-curator-442401.cloudfunctions.net/refresh-token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: userId })
      });

      console.log('Refresh token response status:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Refresh token error:', errorText);
        throw new Error('Failed to refresh token');
      }

      const data = await response.json();
      console.log('Token refreshed successfully');
      setAccessToken(data.access_token);

      // Schedule next refresh
      setTimeout(() => {
        refreshToken();
      }, (data.expires_in - 300) * 1000); // Refresh 5 minutes before expiry

      return data.access_token;
    } catch (err) {
      console.error('Token refresh error:', err);
      setError(err.message);
      return null;
    }
  }, []); // No dependencies since it doesn't use any external values

  useEffect(() => {
    refreshToken()
      .finally(() => setLoading(false));
  }, [refreshToken]); // Now refreshToken is properly included in dependencies

  return {
    accessToken,
    loading,
    error,
    refreshToken
  };
};

export default useSpotifyToken;