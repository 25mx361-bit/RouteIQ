import { useState, useCallback } from 'react';
import axios from 'axios';

// Coimbatore landmarks for instant offline/autocomplete suggestion
export const COIMBATORE_SUGGESTIONS = [
  'Gandhipuram',
  'RS Puram',
  'Coimbatore Railway Station',
  'PSG Tech',
  'Peelamedu',
  'Coimbatore Airport',
  'Saravanampatti',
  'Singanallur',
  'Saibaba Colony',
  'Ukkadam',
  'Hope College',
  'Race Course',
  'Marudhamalai',
];

export function useGeocoding() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const geocodeLocation = useCallback(async (query) => {
    if (!query || !query.trim()) {
      setError('Please enter a location to search.');
      return null;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.get(`/api/geocode`, {
        params: { q: query.trim() },
        timeout: 8000,
      });

      if (response.data && response.data.latitude && response.data.longitude) {
        return {
          latitude: response.data.latitude,
          longitude: response.data.longitude,
          displayName: response.data.display_name,
          source: response.data.source,
        };
      } else {
        throw new Error('Coordinates not found for this location.');
      }
    } catch (err) {
      const msg =
        err.response?.data?.message ||
        err.message ||
        'Unable to geocode location. Please try again.';
      setError(msg);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const clearError = useCallback(() => setError(null), []);

  return {
    geocodeLocation,
    loading,
    error,
    clearError,
    suggestions: COIMBATORE_SUGGESTIONS,
  };
}
