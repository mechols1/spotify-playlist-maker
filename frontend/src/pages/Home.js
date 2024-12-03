// src/pages/Home.js
import React from 'react';
import LoginButton from '../components/auth/LoginButton';

function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-900 text-white">
      <h1 className="text-4xl font-bold mb-8">Spotify Playlist Curator</h1>
      
      {/* Debug information */}
      <div className="mb-4 text-sm text-gray-400">
        <p>Client ID: {process.env.REACT_APP_SPOTIFY_CLIENT_ID ? 'Present' : 'Missing'}</p>
        <p>Redirect URI: {process.env.REACT_APP_API_URI ? 'Present' : 'Missing'}</p>
      </div>
      
      <LoginButton />
    </div>
  );
}

export default Home;