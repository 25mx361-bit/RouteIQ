import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Star, MapPin, Trash2, Navigation, Inbox, Clock } from 'lucide-react';
import { favoritesApi } from '../services/api';
import CongestionBadge from '../components/CongestionBadge';

export default function FavoritesPage() {
  const navigate = useNavigate();
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchFavorites = async () => {
    try {
      const res = await favoritesApi.list();
      setFavorites(res.data?.favorites || (Array.isArray(res.data) ? res.data : []));
    } catch (err) {
      console.warn('Favorites fetch notice:', err);
      setFavorites([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFavorites();
  }, []);

  const handleUseAgain = (item) => {
    const sLabel = item.source?.label || item.source || 'Source';
    const dLabel = item.destination?.label || item.dest || 'Destination';
    sessionStorage.setItem('routeiq_search_result', JSON.stringify({
      source: { label: sLabel },
      destination: { label: dLabel },
      travel_meta: {
        date: new Date().toISOString().split('T')[0],
        time: '09:00'
      },
      routes: [
        { 
          name: item.route_name || item.routeName || 'Saved Highway Route', 
          distance_km: item.distance_km || 8.5, 
          duration_min: item.duration_min || 15, 
          tci: item.congestion_level === 'HIGH' ? 2.3 : item.congestion_level === 'MEDIUM' ? 1.6 : 1.15, 
          is_recommended: true 
        }
      ]
    }));
    navigate('/map');
  };

  const handleRemove = async (id) => {
    if (window.confirm('Remove this corridor from your saved favorites?')) {
      try {
        await favoritesApi.remove(id);
        setFavorites(favorites.filter(f => (f._id || f.id) !== id));
      } catch (err) {
        setFavorites(favorites.filter(f => (f._id || f.id) !== id));
      }
    }
  };

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-8 bg-gray-50 dark:bg-slate-950 min-h-full transition-colors duration-200">
      <div>
        <h1 className="text-2xl md:text-3xl font-extrabold text-gray-800 dark:text-slate-100 tracking-tight">Saved Routes & Corridors</h1>
        <p className="text-sm text-gray-500 dark:text-slate-400 mt-1">Quick-launch frequently accessed destinations and commute routes.</p>
      </div>

      {loading ? (
        <div className="p-12 text-center text-gray-400 dark:text-slate-500 text-sm">Loading saved routes...</div>
      ) : favorites.length === 0 ? (
        <div className="bg-white dark:bg-slate-900 rounded-3xl shadow-sm border border-gray-100 dark:border-slate-800 p-16 text-center flex flex-col items-center">
          <Star size={44} className="text-gray-300 dark:text-slate-700 mb-3" />
          <h3 className="text-base font-bold text-gray-800 dark:text-slate-200">No Favorites Pinned</h3>
          <p className="text-xs text-gray-500 dark:text-slate-500 mt-1">Save optimal paths directly from the Recommendations console.</p>
          <button
            onClick={() => navigate('/plan')}
            className="mt-4 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold transition shadow-md shadow-indigo-500/20"
          >
            Find a Route
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {favorites.map((fav) => {
            const favId = fav._id || fav.id;
            const s = fav.source?.label || fav.source || 'Source';
            const d = fav.destination?.label || fav.dest || 'Destination';
            const rName = fav.route_name || fav.routeName || 'Optimal Corridor';
            const dist = fav.distance_km ? `${fav.distance_km.toFixed(1)} km` : (fav.distance || '8.5 km');
            const dur = fav.duration_min ? `${fav.duration_min.toFixed(0)} min` : (fav.duration || '15 min');

            return (
              <div 
                key={favId} 
                className="bg-white dark:bg-slate-900 rounded-3xl shadow-sm border border-gray-100 dark:border-slate-800 p-6 relative group hover:shadow-lg hover:border-indigo-200 dark:hover:border-slate-700 transition-all flex flex-col justify-between"
              >
                <div className="absolute top-5 right-5">
                  <Star className="text-amber-400 fill-amber-400" size={20} />
                </div>
                
                <div>
                  <div className="pr-8 mb-4">
                    <div className="flex items-center gap-1.5 font-bold text-gray-800 dark:text-slate-100 text-base leading-snug">
                      <span className="truncate">{s}</span>
                      <span className="text-indigo-500 shrink-0">→</span>
                      <span className="truncate text-emerald-600 dark:text-emerald-400">{d}</span>
                    </div>
                    <p className="text-xs text-gray-400 dark:text-slate-500 flex items-center gap-1 mt-1 font-medium">
                      <MapPin size={13} className="text-indigo-500 shrink-0" /> <span className="truncate">{rName}</span>
                    </p>
                  </div>

                  <div className="flex justify-between items-center mb-6 bg-gray-50 dark:bg-slate-800/60 p-3.5 rounded-2xl border border-gray-100 dark:border-slate-800">
                    <div>
                      <p className="text-[10px] text-gray-400 dark:text-slate-500 font-semibold uppercase tracking-wider">Metrics</p>
                      <p className="font-bold text-xs text-gray-700 dark:text-slate-300 mt-0.5">{dist} • {dur}</p>
                    </div>
                    <CongestionBadge level={fav.congestion_level || fav.congestion || 'LOW'} />
                  </div>
                </div>

                <div className="flex gap-2 pt-2">
                  <button 
                    onClick={() => handleUseAgain(fav)}
                    className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white py-2.5 rounded-xl text-xs font-bold transition flex items-center justify-center gap-1.5 shadow-md shadow-indigo-500/20 active:scale-95"
                  >
                    <Navigation size={14} /> Use Again
                  </button>
                  <button 
                    onClick={() => handleRemove(favId)}
                    className="bg-rose-50 dark:bg-rose-950/50 text-rose-600 dark:text-rose-400 p-2.5 rounded-xl hover:bg-rose-100 dark:hover:bg-rose-900/50 transition active:scale-95 border border-rose-100 dark:border-rose-900/30"
                    title="Remove Route"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
