// src/hooks/useListeningStats.js
import { useState, useEffect } from 'react';
import { useSpotifyToken } from './useSpotifyToken';

export const useListeningStats = () => {
  const [stats, setStats] = useState({ total_hours: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { accessToken } = useSpotifyToken();
  const userId = localStorage.getItem('spotify_user_id');

  useEffect(() => {
    const fetchStats = async () => {
      if (!accessToken || !userId) {
        setLoading(false);
        return;
      }

      try {
        const response = await fetch(
          `https://us-central1-music-curator-442401.cloudfunctions.net/get_listening_stats?user_id=${userId}`,
          {
            headers: {
              'Authorization': `Bearer ${accessToken}`,
              'Content-Type': 'application/json',
            }
          }
        );

        if (!response.ok) {
          throw new Error(`Failed to fetch listening stats: ${response.status}`);
        }

        const data = await response.json();
        setStats(data);
      } catch (err) {
        console.error('Error fetching listening stats:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [accessToken, userId]);

  return { stats, loading, error };
};