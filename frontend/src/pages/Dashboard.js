import React, { useState, useEffect } from 'react';
import { useSpotifyToken } from '../hooks/useSpotifyToken';
import { AlertCircle, Loader, PlayCircle, Plus, Clock, BarChart3, PieChart, Activity } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { useListeningHistory } from '../hooks/useListeningHistory';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip } from 'recharts';
import { useListeningStats } from '../hooks/useListeningStats';
import RecommendationSection from '../components/RecommendationSection';

const Dashboard = () => {
  const { accessToken, loading, error } = useSpotifyToken();
  const [playlists, setPlaylists] = useState([]);
  const [recentTracks, setRecentTracks] = useState([]);
  const [topArtists, setTopArtists] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const { history: listeningHistory, loading: historyLoading } = useListeningHistory();
  const { stats, loading: statsLoading } = useListeningStats();
  const { recommendations, loading: recsLoading, fetchRecommendations } = useRecommendations();
  useEffect(() => {
    const fetchUserData = async () => {
      if (!accessToken) return;

      try {
        const [playlistsRes, recentRes, artistsRes] = await Promise.all([
          fetch('https://api.spotify.com/v1/me/playlists', {
            headers: { 'Authorization': `Bearer ${accessToken}` }
          }),
          fetch('https://api.spotify.com/v1/me/player/recently-played', {
            headers: { 'Authorization': `Bearer ${accessToken}` }
          }),
          fetch('https://api.spotify.com/v1/me/top/artists', {
            headers: { 'Authorization': `Bearer ${accessToken}` }
          })
        ]);

        const [playlistsData, recentData, artistsData] = await Promise.all([
          playlistsRes.json(),
          recentRes.json(),
          artistsRes.json()
        ]);

        setPlaylists(playlistsData.items || []);
        setRecentTracks(recentData.items || []);
        setTopArtists(artistsData.items || []);
      } catch (err) {
        console.error('Error fetching user data:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchUserData();
  }, [accessToken]);

  if (loading || isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader className="w-8 h-8 animate-spin text-green-500" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <AlertCircle className="w-8 h-8 text-red-500" />
        <p className="ml-2 text-red-500">Error loading dashboard</p>
      </div>
    );
  }



  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navigation/Stats Bar */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto py-4 px-6">
          <h1 className="text-2xl font-bold text-gray-800">Music Analytics Dashboard</h1>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Top Artists Section - Moved to top */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Top Artists</CardTitle>
            <CardDescription>Your most listened artists</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-6">
              {topArtists?.slice(0, 6).map(artist => (
                <div key={artist.id} className="text-center group cursor-pointer">
                  <div className="relative">
                    <img
                      src={(artist.images?.[0]?.url) || "/api/placeholder/128/128"}
                      alt={artist.name}
                      className="w-32 h-32 rounded-full mx-auto transition-transform group-hover:scale-105"
                    />
                    <div className="absolute inset-0 rounded-full bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all" />
                  </div>
                  <p className="mt-3 font-medium text-sm">{artist.name}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Left Column - Stats & Analytics */}
          <div className="lg:col-span-3 grid gap-6">
            {/* Quick Stats Row */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-500">Total Listening Time</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center">
                    <Clock className="w-5 h-5 text-green-500 mr-2" />
                    <span className="text-2xl font-bold">
                      {statsLoading ? (
                        <Loader className="w-4 h-4 animate-spin" />
                      ) : (
                        `${stats.total_hours}h`
                      )}
                    </span>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-500">Tracks This Week</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center">
                    <Activity className="w-5 h-5 text-blue-500 mr-2" />
                    <span className="text-2xl font-bold">0</span>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-500">Playlists Created</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center">
                    <PieChart className="w-5 h-5 text-purple-500 mr-2" />
                    <span className="text-2xl font-bold">{playlists?.length || 0}</span>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Analytics Placeholder */}
            <Card className="col-span-full">
              <CardHeader>
                <CardTitle>Listening History</CardTitle>
                <CardDescription>Tracks played over the last 7 days</CardDescription>
              </CardHeader>
              <CardContent className="h-80">
                {historyLoading ? (
                  <div className="h-full flex items-center justify-center">
                    <Loader className="w-8 h-8 animate-spin text-green-500" />
                  </div>
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={listeningHistory}>
                      {/* ... chart configuration ... */}
                    </LineChart>
                  </ResponsiveContainer>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Recommended Tracks */}
          <Card className="col-span-full">
            <CardHeader>
              <CardTitle>Recommended Tracks</CardTitle>
              <CardDescription>Based on your listening history</CardDescription>
              {!recommendations.length && (
                <button
                  onClick={fetchRecommendations}
                  className="mt-4 bg-green-500 hover:bg-green-600 text-white px-6 py-2 rounded-full"
                >
                  Get Recommendations
                </button>
              )}
            </CardHeader>
            <CardContent>
              {recsLoading ? (
                <div className="flex justify-center p-8">
                  <Loader className="w-8 h-8 animate-spin text-green-500" />
                </div>
              ) : recommendations.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {recommendations.map((track) => (
                    <div key={track.id} className="flex items-center p-3 bg-gray-50 rounded-lg">
                      <img
                        src={track.image_url || "/api/placeholder/48/48"}
                        alt={track.name}
                        className="w-12 h-12 rounded"
                      />
                      <div className="ml-3">
                        <p className="font-medium truncate">{track.name}</p>
                        <p className="text-sm text-gray-500 truncate">{track.artists.join(', ')}</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : null}
            </CardContent>
          </Card>

          {/* Right Column - Recent Activity & Playlists */}
          <div className="space-y-6">
            {/* Recently Played Card */}
            <Card>
              <CardHeader>
                <CardTitle>Recently Played</CardTitle>
                <CardDescription>Your latest tracks</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {recentTracks?.slice(0, 5).map(item => (
                    <div key={item.played_at} className="flex items-center p-2 -mx-2 rounded-lg hover:bg-gray-50 cursor-pointer">
                      <PlayCircle className="w-8 h-8 text-green-500 flex-shrink-0" />
                      <div className="ml-3 overflow-hidden">
                        <p className="font-medium truncate">{item.track?.name}</p>
                        <p className="text-sm text-gray-500 truncate">
                          {item.track?.artists?.map(artist => artist.name).join(', ')}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Playlists Card */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Your Playlists</CardTitle>
                  <CardDescription>Quick access</CardDescription>
                </div>
                <button className="p-2 hover:bg-gray-100 rounded-full">
                  <Plus className="w-5 h-5" />
                </button>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {playlists?.slice(0, 5).map(playlist => (
                    <div key={playlist.id} className="flex items-center p-2 -mx-2 rounded-lg hover:bg-gray-50 cursor-pointer">
                      <img
                        src={(playlist.images?.[0]?.url) || "/api/placeholder/40/40"}
                        alt={playlist.name}
                        className="w-10 h-10 rounded"
                      />
                      <div className="ml-3 overflow-hidden">
                        <p className="font-medium truncate">{playlist.name}</p>
                        <p className="text-sm text-gray-500">{playlist.tracks?.total || 0} tracks</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;