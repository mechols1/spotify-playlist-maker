import { useState } from 'react';
import { useSpotifyToken } from './useSpotifyToken';

export const useRecommendations = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { accessToken } = useSpotifyToken();
  const userId = localStorage.getItem('spotify_user_id');

  const fetchRecommendations = async () => {
    if (!accessToken || !userId) {
      console.error('Access Token or User ID is missing');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(
        `https://us-central1-music-curator-442401.cloudfunctions.net/get_recommendations?user_id=${userId}`,
        {
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) throw new Error(`Failed to fetch recommendations. Status: ${response.status}`);

      const data = await response.json();
      setRecommendations(data.tracks || []);
    } catch (err) {
      console.error('Error fetching recommendations:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return { 
    recommendations, 
    recsLoading: loading, 
    error,
    fetchRecommendations 
  };
};