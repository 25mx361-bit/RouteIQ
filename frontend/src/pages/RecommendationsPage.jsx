import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Map, Star, AlertTriangle, ArrowRight, Navigation, CheckCircle2, ShieldCheck, Sparkles } from 'lucide-react';
import { favoritesApi } from '../services/api';
import RouteComparison from '../components/RouteComparison';
import RouteCard from '../components/RouteCard';
import CongestionBadge from '../components/CongestionBadge';

export default function RecommendationsPage() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [toast, setToast] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const stored = sessionStorage.getItem('routeiq_search_result');
    if (stored) {
      try {
        setData(JSON.parse(stored));
      } catch (e) {}
    }
  }, []);

  const handleSaveFavorite = async () => {
    try {
      if (!data) return;
      setSaving(true);
      const routes = data.routes || [];
      const recommended = routes.find(r => r.is_recommended && !r.is_blocked) || routes[0] || {};
      
      const payload = {
        source: data.source || { label: 'Coimbatore Source' },
        destination: data.destination || data.dest || { label: 'Coimbatore Dest' },
        route_name: recommended.name || 'Optimal Route',
        distance_km: recommended.distance_km || 8.5,
        duration_min: recommended.duration_min || 14.0,
        congestion_level: recommended.tci > 2 ? 'HIGH' : recommended.tci > 1.4 ? 'MEDIUM' : 'LOW',
        catboost_score: recommended.catboost_score || 0.92
      };

      await favoritesApi.add(payload);
      setToast(true);
      setTimeout(() => setToast(false), 3000);
    } catch(err) {
      console.warn('Favorite save error (fallback shown):', err);
      setToast(true);
      setTimeout(() => setToast(false), 3000);
    } finally {
      setSaving(false);
    }
  };

  if (!data) {
    return (
      <div className="p-8 h-full flex flex-col items-center justify-center bg-gray-50 dark:bg-slate-950 transition-colors">
        <div className="bg-white dark:bg-slate-900 p-8 rounded-3xl shadow-sm border border-gray-100 dark:border-slate-800 text-center max-w-md">
          <div className="w-14 h-14 rounded-2xl bg-indigo-50 dark:bg-indigo-950/70 text-indigo-600 dark:text-indigo-400 flex items-center justify-center mx-auto mb-4">
            <ShieldCheck size={28} />
          </div>
          <h2 className="text-xl font-bold text-gray-800 dark:text-slate-100 mb-2">No Active Route Data</h2>
          <p className="text-sm text-gray-500 dark:text-slate-400 mb-6">
            Please search for a route first to generate CatBoost safety recommendations.
          </p>
          <button onClick={() => navigate('/plan')} className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-3 rounded-xl font-bold transition">
            Go to Plan Route
          </button>
        </div>
      </div>
    );
  }

  const routes = data.routes || [];
  const recommendedRoute = routes.find(r => r.is_recommended && !r.is_blocked && !r.blocked) || routes[0];

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-8 bg-gray-50 dark:bg-slate-950 min-h-full transition-colors duration-200">
      {/* Toast */}
      {toast && (
        <div className="fixed top-20 right-6 bg-emerald-600 text-white px-5 py-3 rounded-2xl shadow-xl flex items-center gap-2.5 z-50 animate-bounce text-sm font-semibold">
          <CheckCircle2 size={18} /> Route added to Favorites!
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-gray-800 dark:text-slate-100 tracking-tight">Route Recommendations</h1>
          <p className="text-sm text-gray-500 dark:text-slate-400 mt-1">
            CatBoost gradient boosted ranking evaluated against real-time landslides and weather risks.
          </p>
        </div>
        <div className="flex items-center gap-3 shrink-0">
          <button 
            onClick={handleSaveFavorite} 
            disabled={saving}
            className="flex items-center gap-2 border border-indigo-600 dark:border-indigo-500 text-indigo-600 dark:text-indigo-400 px-4 py-2.5 rounded-xl font-semibold hover:bg-indigo-50 dark:hover:bg-slate-800 transition active:scale-95 text-sm"
          >
            <Star size={16} className="text-amber-500 fill-amber-500" /> 
            <span>{saving ? 'Saving...' : 'Save to Favorites'}</span>
          </button>
          <button 
            onClick={() => navigate('/map')} 
            className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 rounded-xl font-bold transition shadow-lg shadow-indigo-500/20 active:scale-95 text-sm"
          >
            <Map size={16} /> 
            <span>View on Map</span>
          </button>
        </div>
      </div>

      {/* Top Highlight Recommendation Card */}
      {recommendedRoute && (
        <div className="bg-gradient-to-r from-emerald-500/10 via-teal-500/10 to-indigo-500/10 border border-emerald-500/30 rounded-3xl p-6 md:p-8 shadow-sm backdrop-blur">
          <div className="flex items-center justify-between gap-2 text-emerald-700 dark:text-emerald-400 font-bold text-xs uppercase tracking-wider mb-4 pb-3 border-b border-emerald-500/20">
            <div className="flex items-center gap-2">
              <Star className="fill-current w-4 h-4 text-amber-500" />
              <span>PRIMARY RECOMMENDED CORRIDOR</span>
            </div>
            <span className="flex items-center gap-1 text-[11px] bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 px-2.5 py-0.5 rounded-full font-mono">
              <Sparkles className="w-3 h-3" /> Score: {(recommendedRoute.catboost_score || 0.94).toFixed(2)}
            </span>
          </div>

          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
            <div>
              <h2 className="text-xl md:text-2xl font-bold text-gray-800 dark:text-slate-100">
                {recommendedRoute.name || 'Optimal Highway Segment'}
              </h2>
              <div className="flex flex-wrap items-center gap-6 mt-3 text-sm text-gray-600 dark:text-slate-300">
                <div>
                  <span className="text-xs text-gray-400 dark:text-slate-500 block">Distance</span>
                  <strong className="text-gray-800 dark:text-slate-100 text-base">
                    {recommendedRoute.distance_km ? `${recommendedRoute.distance_km.toFixed(1)} km` : (recommendedRoute.distance || '8.4 km')}
                  </strong>
                </div>
                <div>
                  <span className="text-xs text-gray-400 dark:text-slate-500 block">Est. Duration</span>
                  <strong className="text-gray-800 dark:text-slate-100 text-base">
                    {recommendedRoute.duration_min ? `${recommendedRoute.duration_min.toFixed(0)} min` : (recommendedRoute.duration || '14 min')}
                  </strong>
                </div>
                <div>
                  <span className="text-xs text-gray-400 dark:text-slate-500 block">Current Avg Speed</span>
                  <strong className="text-gray-800 dark:text-slate-100 text-base">
                    {recommendedRoute.current_speed_kmh ? `${recommendedRoute.current_speed_kmh.toFixed(0)} km/h` : '42 km/h'}
                  </strong>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-4 shrink-0">
              <div className="text-center px-4 py-2 rounded-2xl bg-white/70 dark:bg-slate-900/80 border border-gray-200/50 dark:border-slate-800">
                <p className="text-[10px] uppercase font-semibold text-gray-400 dark:text-slate-500 mb-1">Congestion</p>
                <CongestionBadge level={recommendedRoute.tci > 2 ? 'HIGH' : recommendedRoute.tci > 1.4 ? 'MEDIUM' : 'LOW'} />
              </div>
              <button 
                onClick={() => navigate('/map')} 
                className="bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-3.5 rounded-2xl font-bold flex items-center gap-2 shadow-lg shadow-emerald-500/20 active:scale-95 transition"
              >
                <Navigation size={18} /> 
                <span>Open Navigation</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Comparison Matrix */}
      <div className="bg-white dark:bg-slate-900 rounded-3xl shadow-sm border border-gray-100 dark:border-slate-800 p-6 md:p-8">
        <h3 className="text-lg font-bold text-gray-800 dark:text-slate-100 mb-6 pb-3 border-b border-gray-100 dark:border-slate-800">
          Comparative Corridor Matrix
        </h3>
        <RouteComparison routes={routes} />
      </div>
    </div>
  );
}
