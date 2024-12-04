import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';
import { Loader } from 'lucide-react';
import { useRecommendations } from '../../hooks/useRecommendations';

const RecommendationSection = () => {
  const { recommendations, recsLoading, error, fetchRecommendations } = useRecommendations();
  
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
      <CardHeader>
        <CardTitle>Recommended Tracks</CardTitle>
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
          <div className="space-y-4">
            <p className="text-gray-600 mb-4">Here are some recommendations based on your listening history:</p>
            {recommendations.map((track) => (
              <a
                key={track.id}
                href={track.external_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center p-4 bg-white hover:bg-gray-50 rounded-lg shadow-sm transition-colors"
              >
                <img
                  src={track.image_url || "/api/placeholder/48/48"}
                  alt={track.name}
                  className="w-12 h-12 rounded-md object-cover"
                />
                <div className="ml-4 flex-grow">
                  <h3 className="font-medium text-gray-900">{track.name}</h3>
                  <p className="text-gray-500 text-sm">{track.artists.join(', ')}</p>
                </div>
              </a>
            ))}
          </div>
        ) : (
          <p className="text-center text-gray-500">Click the button above to get personalized recommendations</p>
        )}
      </CardContent>
    </Card>
  );
};

export default RecommendationSection;