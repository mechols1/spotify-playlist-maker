import { useState, useEffect } from 'react';
import { useSpotifyToken } from './useSpotifyToken';

export const useRecommendations = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastFetched, setLastFetched] = useState(null);
  const { accessToken } = useSpotifyToken();
  const userId = localStorage.getItem('spotify_user_id');

  const CACHE_DURATION = 1000 * 60 * 60; // 1 hour cache

  const fetchRecommendations = async (forceFetch = false) => {
    if (!accessToken || !userId) {
      setError('Authentication required');
      return;
    }

    // Check cache unless force fetch
    if (!forceFetch && lastFetched && (Date.now() - lastFetched < CACHE_DURATION)) {
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

      if (!response.ok) {
        throw new Error(`Failed to fetch recommendations (${response.status})`);
      }

      const data = await response.json();
      
      if (!data.tracks || !Array.isArray(data.tracks)) {
        throw new Error('Invalid recommendations data format');
      }

      setRecommendations(data.tracks);
      setLastFetched(Date.now());
      setError(null);
    } catch (err) {
      console.error('Error fetching recommendations:', err);
      setError(err.message);
      
      // Attempt to load cached recommendations from localStorage
      const cached = localStorage.getItem('cached_recommendations');
      if (cached) {
        try {
          setRecommendations(JSON.parse(cached));
        } catch (e) {
          console.error('Error loading cached recommendations:', e);
        }
      }
    } finally {
      setLoading(false);
    }
  };

  // Cache recommendations when we get new ones
  useEffect(() => {
    if (recommendations.length > 0) {
      localStorage.setItem('cached_recommendations', JSON.stringify(recommendations));
    }
  }, [recommendations]);

  return {
    recommendations,
    recsLoading: loading,
    error,
    fetchRecommendations,
    lastFetched,
    isStale: lastFetched ? (Date.now() - lastFetched > CACHE_DURATION) : true
  };
};