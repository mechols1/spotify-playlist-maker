import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../ui/card';
import { Loader, Music, ListPlus } from 'lucide-react';
import { useRecommendations } from '../../hooks/useRecommendations';
import { useSpotifyToken } from '../../hooks/useSpotifyToken';

const RecommendationSection = () => {
  const { recommendations, recsLoading, error, fetchRecommendations } = useRecommendations();
  const { accessToken } = useSpotifyToken();
  const [creatingPlaylist, setCreatingPlaylist] = useState(false);

  const handleCreatePlaylist = async () => {
    if (!accessToken || !recommendations.length) return;
    setCreatingPlaylist(true);

    try {
      // First, get the user's Spotify ID
      const userResponse = await fetch('https://api.spotify.com/v1/me', {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      const userData = await userResponse.json();

      // Create a new playlist
      const date = new Date().toLocaleDateString();
      const playlistResponse = await fetch(
        `https://api.spotify.com/v1/users/${userData.id}/playlists`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            name: `Recommended Tracks - ${date}`,
            description: 'Playlist created from personalized recommendations',
            public: false
          })
        }
      );
      const playlistData = await playlistResponse.json();

      // Add tracks to the playlist
      const trackUris = recommendations.map(track => `spotify:track:${track.id}`);
      await fetch(
        `https://api.spotify.com/v1/playlists/${playlistData.id}/tracks`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            uris: trackUris
          })
        }
      );

      // Open the playlist in Spotify
      window.open(playlistData.external_urls.spotify, '_blank');
    } catch (err) {
      console.error('Error creating playlist:', err);
    } finally {
      setCreatingPlaylist(false);
    }
  };

  if (error) {
    return (
      <Card className="col-span-full">
        <CardHeader>
          <CardTitle>Recommended Tracks</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-red-500">Error loading recommendations</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="col-span-full">
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>Recommended Tracks</CardTitle>
          <CardDescription>Discover new music based on your taste</CardDescription>
        </div>
        <div className="flex gap-4">
          {!recommendations.length && (
            <button
              onClick={fetchRecommendations}
              className="bg-green-500 hover:bg-green-600 text-white px-6 py-2 rounded-full"
            >
              Get Recommendations
            </button>
          )}
          {recommendations.length > 0 && (
            <button
              onClick={handleCreatePlaylist}
              disabled={creatingPlaylist}
              className="flex items-center gap-2 bg-green-500 hover:bg-green-600 disabled:bg-green-300 text-white px-6 py-2 rounded-full"
            >
              <ListPlus className="w-5 h-5" />
              {creatingPlaylist ? 'Creating Playlist...' : 'Create Playlist from Recommendations'}
            </button>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {recsLoading ? (
          <div className="flex justify-center p-8">
            <Loader className="w-8 h-8 animate-spin text-green-500" />
          </div>
        ) : recommendations.length > 0 ? (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {recommendations.map((track) => (
                <a
                  key={track.id}
                  href={track.external_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex flex-col bg-white hover:bg-gray-50 rounded-lg shadow-sm transition-colors p-4 border"
                >
                  <img
                    src={track.image_url || "/api/placeholder/200/200"}
                    alt={track.name}
                    className="w-full aspect-square rounded-md object-cover mb-3"
                  />
                  <div>
                    <h3 className="font-medium text-gray-900 truncate">{track.name}</h3>
                    <p className="text-gray-500 text-sm truncate">{track.artists.join(', ')}</p>
                  </div>
                </a>
              ))}
            </div>
          </div>
        ) : (
          <div className="text-center p-8 space-y-4">
            <Music className="w-16 h-16 text-gray-300 mx-auto" />
            <p className="text-gray-500">Click the button above to get personalized recommendations</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default RecommendationSection;