export const logout = () => {
    // Clear all auth-related items from localStorage
    localStorage.removeItem('spotify_user_id');
    
    // Clear any other app-specific data
    localStorage.removeItem('cached_recommendations');
    
    // Reload the page to reset all app state
    window.location.href = '/';
  };
  