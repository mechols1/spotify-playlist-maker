import { useState, useEffect } from 'react';
import { useSpotifyToken } from './useSpotifyToken';

export const useListeningHistory = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { accessToken } = useSpotifyToken();
  const userId = localStorage.getItem('spotify_user_id');

  useEffect(() => {
    const fetchHistory = async () => {
      if (!accessToken || !userId) {
        setLoading(false);
        return;
      }

      try {
        const response = await fetch(
          `https://us-central1-music-curator-442401.cloudfunctions.net/get_listening_history?user_id=${userId}`,
          {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            },
            mode: 'cors',
            credentials: 'omit'  // Add this line
          }
        );

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
          throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        if (Array.isArray(data.history)) {
          const processedHistory = data.history.map(item => ({
            date: item.date || '',
            day: item.day || '',
            count: item.count || 0,
            timestamp: item.timestamp || 0
          }));
          setHistory(processedHistory);
        } else {
          console.warn('Invalid history data format:', data);
          setHistory([]);
        }
      } catch (err) {
        console.error('Error fetching listening history:', err);
        setError(err.message);
        setHistory([]);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [accessToken, userId]);

  return { 
    history, 
    loading, 
    error,
    refresh: () => setLoading(true)
  };
};

export default useListeningHistory;