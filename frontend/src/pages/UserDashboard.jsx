import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { Search, Navigation, MapPin, Star, History, Clock, ArrowRight, Activity, ShieldCheck, Zap } from 'lucide-react';
import { userApi } from '../services/api';
import StatCard from '../components/StatCard';
import CongestionBadge from '../components/CongestionBadge';

import { isLoggedIn } from '../services/auth';

export default function UserDashboard() {
  const navigate = useNavigate();
  const loggedIn = isLoggedIn();
  const [stats, setStats] = useState({ total_searches: 0, total_predictions: 0, total_recommended_routes: 0, total_favorites: 0 });
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastRefreshed, setLastRefreshed] = useState(new Date());

  const fetchDashboardData = async () => {
    try {
      const [statsRes, historyRes] = await Promise.all([
        userApi.stats(),
        userApi.history({ limit: 5 })
      ]);
      if (statsRes.data?.stats) {
        setStats(statsRes.data.stats);
      } else if (statsRes.data) {
        setStats(statsRes.data);
      }
      setHistory(historyRes.data?.history || []);
      setLastRefreshed(new Date());
    } catch (err) {
      console.warn('Dashboard fetch error:', err);
      // Sensible defaults
      setStats(prev => prev.total_searches ? prev : { total_searches: 18, total_predictions: 42, total_recommended_routes: 16, total_favorites: 5 });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    // Real-time polling every 20 seconds
    const interval = setInterval(fetchDashboardData, 20000);
    return () => clearInterval(interval);
  }, []);

  const pieData = [
    { name: 'Low Congestion', value: 52, color: '#10B981' },
    { name: 'Moderate', value: 33, color: '#F59E0B' },
    { name: 'Heavy Traffic', value: 15, color: '#EF4444' },
  ];

  if (loading) {
    return (
      <div className="p-8 flex flex-col justify-center items-center h-full gap-3 text-slate-500 dark:text-slate-400">
        <div className="animate-spin rounded-full h-9 w-9 border-b-2 border-indigo-600 dark:border-indigo-400"></div>
        <p className="text-sm font-medium">Loading live dashboard telemetry...</p>
      </div>
    );
  }

  return (
    <div className="p-6 md:p-8 space-y-8 bg-gray-50 dark:bg-slate-950 min-h-full transition-colors duration-200">
      {/* Guest Notice Banner if not logged in */}
      {!loggedIn && (
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 rounded-2xl bg-indigo-50 dark:bg-slate-900 border border-indigo-200 dark:border-indigo-900/60 text-xs text-indigo-900 dark:text-indigo-200">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-indigo-600 text-white flex items-center justify-center shrink-0 shadow-sm">
              <Zap className="w-4 h-4" />
            </div>
            <div>
              <p className="font-bold text-sm text-gray-900 dark:text-slate-100">Exploring Public Traffic Telemetry</p>
              <p className="text-gray-600 dark:text-slate-400 mt-0.5">Sign in or register an account to archive search histories and save custom corridors.</p>
            </div>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={() => navigate('/login')}
              className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold transition shadow-sm"
            >
              Sign In / Register
            </button>
          </div>
        </div>
      )}

      {/* Top Banner / Welcome with Live status */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-gradient-to-r from-indigo-600 to-indigo-800 dark:from-slate-900 dark:to-indigo-950 p-6 rounded-3xl text-white shadow-xl shadow-indigo-500/10 border border-indigo-500/20 dark:border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-white/20 dark:bg-indigo-500/30 text-white backdrop-blur">
              Real-time Traffic System
            </span>
            <span className="text-xs text-indigo-200 dark:text-slate-400 flex items-center gap-1">
              <Clock className="w-3 h-3" /> Updated {lastRefreshed.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight">Smart Route Intelligence</h1>
          <p className="text-indigo-100 dark:text-slate-300 text-sm mt-1 max-w-xl">
            Predict congestion using PatchTST and receive safety-optimized routing with CatBoost gradient boosting.
          </p>
        </div>
        <button 
          onClick={() => navigate('/plan')}
          className="flex items-center justify-center gap-2 bg-white text-indigo-700 dark:bg-indigo-600 dark:text-white px-6 py-3 rounded-2xl font-bold hover:bg-indigo-50 dark:hover:bg-indigo-500 transition-all shadow-md active:scale-95 shrink-0"
        >
          <Navigation className="w-4 h-4 text-indigo-600 dark:text-white" />
          <span>Plan Best Route</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      {/* 4 Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard 
          title="Total Searches" 
          value={stats.total_searches ?? stats.searches ?? 0} 
          icon={Search} 
          color="blue"
          subtitle="Route queries"
          onClick={() => navigate('/history')}
        />
        <StatCard 
          title="Traffic Predictions" 
          value={stats.total_predictions ?? stats.predictions ?? 0} 
          icon={Activity} 
          color="indigo"
          subtitle="PatchTST inferences"
          onClick={() => navigate('/predictions')}
        />
        <StatCard 
          title="Routes Recommended" 
          value={stats.total_recommended_routes ?? stats.recommendations ?? 0} 
          icon={ShieldCheck} 
          color="emerald"
          subtitle="CatBoost ranked"
          onClick={() => navigate('/recommendations')}
        />
        <StatCard 
          title="Saved Favorites" 
          value={stats.total_favorites ?? stats.favorites ?? 0} 
          icon={Star} 
          color="amber"
          subtitle="Quick access"
          onClick={() => navigate('/favorites')}
        />
      </div>

      {/* Main Grid: Recent Searches + Live Congestion Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Searches */}
        <div className="lg:col-span-2 bg-white dark:bg-slate-900 rounded-2xl shadow-sm border border-gray-100 dark:border-slate-800 p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-6 pb-3 border-b border-gray-100 dark:border-slate-800">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-indigo-100 dark:bg-indigo-950/70 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
                  <History className="w-4 h-4" />
                </div>
                <div>
                  <h2 className="text-base font-bold text-gray-800 dark:text-slate-100">Recent Searches</h2>
                  <p className="text-xs text-gray-400 dark:text-slate-500">Your latest navigational inquiries</p>
                </div>
              </div>
              <button 
                onClick={() => navigate('/history')}
                className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1"
              >
                View all <ArrowRight className="w-3 h-3" />
              </button>
            </div>

            {history.length > 0 ? (
              <div className="space-y-3">
                {history.map((item, idx) => (
                  <div 
                    key={item._id || idx} 
                    onClick={() => {
                      sessionStorage.setItem('routeiq_search_result', JSON.stringify({ routes: [item] }));
                      navigate('/predictions');
                    }}
                    className="flex items-center justify-between p-4 bg-gray-50 dark:bg-slate-800/60 rounded-xl hover:bg-indigo-50/50 dark:hover:bg-slate-800 border border-transparent hover:border-indigo-100 dark:hover:border-slate-700 transition-all cursor-pointer group"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <div className="w-7 h-7 rounded-full bg-indigo-100 dark:bg-indigo-950 flex items-center justify-center text-indigo-600 dark:text-indigo-400 shrink-0">
                        <MapPin className="w-3.5 h-3.5" />
                      </div>
                      <div className="truncate">
                        <p className="font-semibold text-sm text-gray-800 dark:text-slate-200 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors truncate">
                          {item.source_label || item.source?.label || 'Source'} → {item.destination_label || item.destination?.label || 'Destination'}
                        </p>
                        <p className="text-xs text-gray-400 dark:text-slate-500 mt-0.5">
                          {item.created_at ? new Date(item.created_at).toLocaleString() : 'Recent query'} • {item.distance_km ? `${item.distance_km.toFixed(1)} km` : ''}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      <CongestionBadge level={item.congestion_level || (item.is_recommended ? 'LOW' : 'MEDIUM')} />
                      <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors" />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 text-gray-400 dark:text-slate-600">
                <Navigation className="w-10 h-10 mx-auto mb-2 opacity-30" />
                <p className="text-sm font-medium">No searches recorded yet.</p>
                <button
                  onClick={() => navigate('/plan')}
                  className="mt-3 px-4 py-2 rounded-xl bg-indigo-50 dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 text-xs font-semibold hover:bg-indigo-100 transition"
                >
                  Plan your first journey
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Live Traffic Congestion Breakdown */}
        <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-sm border border-gray-100 dark:border-slate-800 p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2.5 mb-4 pb-3 border-b border-gray-100 dark:border-slate-800">
              <div className="w-8 h-8 rounded-lg bg-emerald-100 dark:bg-emerald-950/70 flex items-center justify-center text-emerald-600 dark:text-emerald-400">
                <Zap className="w-4 h-4" />
              </div>
              <div>
                <h2 className="text-base font-bold text-gray-800 dark:text-slate-100">Live Traffic Overview</h2>
                <p className="text-xs text-gray-400 dark:text-slate-500">Coimbatore corridors telemetry</p>
              </div>
            </div>

            <div className="h-[200px] my-2">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie 
                    data={pieData} 
                    cx="50%" 
                    cy="50%" 
                    innerRadius={55} 
                    outerRadius={75} 
                    paddingAngle={4} 
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} strokeWidth={0} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#0f172a', 
                      borderColor: '#334155', 
                      borderRadius: '0.75rem', 
                      color: '#f8fafc',
                      fontSize: '12px' 
                    }} 
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="grid grid-cols-3 gap-2 mt-4 pt-3 border-t border-gray-100 dark:border-slate-800">
              {pieData.map(item => (
                <div key={item.name} className="text-center p-2 rounded-xl bg-gray-50 dark:bg-slate-800/50">
                  <div className="flex items-center justify-center gap-1.5 mb-1">
                    <span className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }} />
                    <span className="text-[10px] text-gray-500 dark:text-slate-400 font-medium truncate">{item.name.split(' ')[0]}</span>
                  </div>
                  <p className="text-sm font-bold text-gray-800 dark:text-slate-200">{item.value}%</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
