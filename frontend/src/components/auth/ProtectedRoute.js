import React, { useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';

const ProtectedRoute = ({ children }) => {
  const location = useLocation();
  const userId = localStorage.getItem('spotify_user_id');
  
  useEffect(() => {
    console.log('ProtectedRoute Check:', {
      path: location.pathname,
      userId: userId,
      localStorage: { ...localStorage }
    });
  }, [location, userId]);

  if (!userId) {
    console.log('No userId found, redirecting to home');
    return <Navigate to="/" replace state={{ from: location }} />;
  }

  return children;
};

export default ProtectedRoute;