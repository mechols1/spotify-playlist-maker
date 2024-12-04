import React from 'react';
import { PlusCircle } from 'lucide-react';

const RecommendationCard = ({ track, onAddToPlaylist }) => {
  return (
    <div className="flex items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
      <img
        src={track.image_url || "/placeholder.png"}
        alt={track.name}
        className="w-12 h-12 rounded-lg"
      />
      <div className="ml-3 flex-grow">
        <p className="font-medium text-sm truncate">{track.name}</p>
        <p className="text-sm text-gray-500 truncate">{track.artists.join(', ')}</p>
      </div>
      <button 
        onClick={() => onAddToPlaylist(track)}
        className="p-2 hover:bg-green-100 rounded-full text-green-500"
      >
        <PlusCircle className="w-5 h-5" />
      </button>
    </div>
  );
};

export default RecommendationCard;