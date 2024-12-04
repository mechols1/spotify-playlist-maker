import React from 'react';
import { X } from 'lucide-react';

const PlaylistSelectionModal = ({ isOpen, onClose, playlists, onSelect, track }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Add to Playlist</h2>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-full">
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="max-h-96 overflow-y-auto">
          {playlists.map(playlist => (
            <button
              key={playlist.id}
              onClick={() => onSelect(playlist.id, track)}
              className="w-full text-left p-3 hover:bg-gray-50 rounded-lg mb-2"
            >
              <p className="font-medium">{playlist.name}</p>
              <p className="text-sm text-gray-500 truncate">{playlist.description || 'No description'}</p>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default PlaylistSelectionModal;