import React from 'react';
import { Card, CardContent } from '../components/ui/card';
import LoginButton from '../components/auth/LoginButton';
import { Music, PlayCircle, ListMusic, BarChart2 } from 'lucide-react';

const FeatureCard = ({ icon: Icon, title, description }) => (
  <Card className="bg-gray-800 border-gray-700">
    <CardContent className="p-6">
      <div className="flex items-center space-x-4">
        <div className="p-3 bg-green-500 bg-opacity-10 rounded-lg">
          <Icon className="w-6 h-6 text-green-500" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-white mb-1">{title}</h3>
          <p className="text-gray-400">{description}</p>
        </div>
      </div>
    </CardContent>
  </Card>
);

function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-black text-white">
      <div className="max-w-6xl mx-auto px-4 py-16 sm:px-6 lg:px-8">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-green-400 to-green-600">
            Spotify Playlist Curator
          </h1>
          <p className="text-xl text-gray-400 mb-8 max-w-2xl mx-auto">
            Discover, create, and organize your perfect playlists with powerful analytics and personalized recommendations.
          </p>
          <LoginButton />
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 gap-6 mt-12">
          <FeatureCard
            icon={PlayCircle}
            title="Smart Recommendations"
            description="Get personalized music suggestions based on your listening history and preferences"
          />
          <FeatureCard
            icon={ListMusic}
            title="Playlist Management"
            description="Create, organize, and customize your playlists with an intuitive interface"
          />
          <FeatureCard
            icon={BarChart2}
            title="Listening Analytics"
            description="Understand your music taste with detailed listening statistics and trends"
          />
          <FeatureCard
            icon={Music}
            title="Music Discovery"
            description="Explore new artists and genres tailored to your unique taste"
          />
        </div>

        {/* Debug Info - Only show in development */}
        {process.env.NODE_ENV === 'development' && (
          <div className="mt-8 text-sm text-gray-500 text-center">
            <p>Client ID: {process.env.REACT_APP_SPOTIFY_CLIENT_ID ? 'Present' : 'Missing'}</p>
            <p>Redirect URI: {process.env.REACT_APP_API_URI ? 'Present' : 'Missing'}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Home;