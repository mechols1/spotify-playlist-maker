import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

function Callback() {
  const navigate = useNavigate();
  const location = useLocation();
  const [error, setError] = useState(null);
  const [processed, setProcessed] = useState(false);

  useEffect(() => {
    const handleCallback = () => {
      if (processed) {
        console.log('Callback already processed, skipping');
        return;
      }

      const params = new URLSearchParams(location.search);
      const authSuccess = params.get('auth');
      const userId = params.get('user_id');
      const errorMessage = params.get('error');

      console.log('Callback State:', {
        authSuccess,
        userId,
        errorMessage,
        processed,
        currentLocation: location.pathname,
        fullUrl: window.location.href,
        localStorage: { ...localStorage }
      });

      if (errorMessage) {
        console.error('Authentication error:', errorMessage);
        setError(errorMessage);
        setProcessed(true);
        setTimeout(() => navigate('/', { replace: true }), 3000);
        return;
      }

      if (authSuccess === 'success' && userId) {
        console.log('Authentication successful, storing user ID:', userId);
        localStorage.setItem('spotify_user_id', userId);
        setProcessed(true);
        navigate('/dashboard', { replace: true });
      } else {
        console.log('Authentication failed - invalid parameters');
        setError('Authentication failed - invalid parameters');
        setProcessed(true);
        setTimeout(() => navigate('/', { replace: true }), 3000);
      }
    };

    handleCallback();
  }, [navigate, location, processed]);

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="text-center p-8 bg-white rounded-lg shadow-md">
        {error ? (
          <div className="text-red-500">
            <h2 className="text-xl font-bold mb-2">Authentication Error</h2>
            <p>{error}</p>
            <p className="mt-2 text-sm">Redirecting to home...</p>
            <pre className="mt-4 text-left text-xs overflow-auto">
              {JSON.stringify({ 
                location: location.pathname,
                search: location.search,
                localStorage: { ...localStorage }
              }, null, 2)}
            </pre>
          </div>
        ) : (
          <div>
            <h2 className="text-xl font-bold mb-2">Authenticating...</h2>
            <p className="text-gray-600">Please wait while we complete the process.</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Callback;
