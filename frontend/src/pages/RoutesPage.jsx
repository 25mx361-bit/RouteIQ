import React, { useState, useEffect, useCallback } from 'react';
import {
  Layers,
  MapPin,
  Clock,
  Compass,
  TrendingUp,
  AlertCircle,
  RefreshCw,
  Activity,
  Calendar,
  Flame,
  AlertOctagon,
  ShieldAlert,
  BarChart2,
  Table2, Settings,
} from 'lucide-react';
import MapView from '../components/MapView';
import SearchForm from '../components/SearchForm';
import RouteCard from '../components/RouteCard';
import RouteComparison from '../components/RouteComparison';
import PredictionChart from '../components/PredictionChart';
import TrafficCard from '../components/TrafficCard';
import WeatherCard from '../components/WeatherCard';
import SchedulerStatusModal from '../components/SchedulerStatusModal';
import NotificationPanel from '../components/NotificationPanel';
import FestivalCard from '../components/FestivalCard';
import MarriageEventCard from '../components/MarriageEventCard';
import EventCard from '../components/EventCard';
import LandslideAlert from '../components/LandslideAlert';
import EventsPage from './admin/EventsPage';
import LandslidesPage from './admin/LandslidesPage';
import AdminDashboard from './admin/AdminDashboard';
import UsersPage from './admin/UsersPage';
import ModelsPage from './admin/ModelsPage';
import LogsPage from './admin/LogsPage';
import {
  routesApi,
  trafficApi,
  weatherApi,
  eventsApi,
  landslideApi,
} from '../services/api';

export default function RoutesPage() {
  const [currentView, setCurrentView] = useState('DASHBOARD');
  const [sidebarTab, setSidebarTab] = useState('cards'); // 'cards' | 'compare' | 'chart'

  // Default Coimbatore locations
  const [sourceCoords, setSourceCoords] = useState({
    lat: 11.0168,
    lng: 76.9558,
    label: 'Gandhipuram, Coimbatore, Tamil Nadu, India',
  });
  const [destCoords, setDestCoords] = useState({
    lat: 11.0094,
    lng: 76.9458,
    label: 'R.S. Puram, Coimbatore, Tamil Nadu, India',
  });
  const [travelMeta, setTravelMeta] = useState({
    date: new Date().toISOString().split('T')[0],
    time: new Date().toTimeString().slice(0, 5),
  });

  const [routes, setRoutes] = useState([]);
  const [selectedRoute, setSelectedRoute] = useState(0);
  const [loadingRoutes, setLoadingRoutes] = useState(false);
  const [routeError, setRouteError] = useState(null);

  // Landslide state
  const [activeLandslides, setActiveLandslides] = useState([]);
  const [blockedLandslideHazard, setBlockedLandslideHazard] = useState(null);

  // Ancillary data
  const [trafficData, setTrafficData] = useState(null);
  const [loadingTraffic, setLoadingTraffic] = useState(false);
  const [weatherData, setWeatherData] = useState(null);
  const [loadingWeather, setLoadingWeather] = useState(false);
  const [routeEvents, setRouteEvents] = useState([]);

  const [isSchedulerModalOpen, setIsSchedulerModalOpen] = useState(false);

  const fetchActiveLandslides = useCallback(async () => {
    try {
      const resp = await landslideApi.list({ status: 'ACTIVE' });
      setActiveLandslides(resp.data.landslides || []);
    } catch (err) {
      console.warn('Could not fetch landslides:', err);
    }
  }, []);

  const fetchTrafficFlow = async (coordinates) => {
    if (!coordinates?.length) return;
    setLoadingTraffic(true);
    try {
      const resp = await trafficApi.routeFlow(coordinates);
      if (resp.data) {
        setTrafficData({
          currentSpeed: resp.data.averageCurrentSpeed,
          freeFlowSpeed: resp.data.averageFreeFlowSpeed,
          delayMinutes: resp.data.totalDelayMinutes,
          roadStatus: resp.data.roadStatus,
          confidence: 0.94,
          roadClosure: false,
          speedRatio: resp.data.speedRatio,
        });
      }
    } catch (err) {
      console.warn('Traffic error:', err);
    } finally {
      setLoadingTraffic(false);
    }
  };

  const fetchWeatherForecast = async (lat, lng, date, time) => {
    setLoadingWeather(true);
    try {
      const resp = await weatherApi.forecast(lat, lng, date, time);
      if (resp.data) setWeatherData(resp.data);
    } catch (err) {
      console.warn('Weather error:', err);
    } finally {
      setLoadingWeather(false);
    }
  };

  const fetchRouteEvents = async (coordinates, targetDt) => {
    if (!coordinates?.length) return;
    try {
      const resp = await eventsApi.routeImpact(coordinates, targetDt);
      if (resp.data?.events) setRouteEvents(resp.data.events);
    } catch (err) {
      console.warn('Events error:', err);
    }
  };

  const fetchRoutes = useCallback(async (source, dest, date, time) => {
    setLoadingRoutes(true);
    setRouteError(null);
    setBlockedLandslideHazard(null);
    try {
      const response = await routesApi.search({
        source_lat: source.lat,
        source_lng: source.lng,
        dest_lat: dest.lat,
        dest_lng: dest.lng,
        source_label: source.label,
        dest_label: dest.label,
        date,
        time,
      });
      if (response.data?.routes) {
        const fetchedRoutes = response.data.routes;
        setRoutes(fetchedRoutes);
        const recIdx = response.data.recommended_route_index ?? 0;
        setSelectedRoute(recIdx);
        const recRoute = fetchedRoutes[recIdx];
        if (recRoute?.is_blocked && recRoute?.landslide_hazard) {
          setBlockedLandslideHazard(recRoute.landslide_hazard);
        }
        const safeRoute = fetchedRoutes.find((r) => !r.is_blocked && r.is_recommended);
        if (safeRoute?.coordinates) {
          fetchTrafficFlow(safeRoute.coordinates);
          fetchRouteEvents(safeRoute.coordinates, `${date}T${time}:00Z`);
        }
        fetchWeatherForecast(source.lat, source.lng, date, time);
      } else {
        throw new Error('No routes returned.');
      }
    } catch (err) {
      setRouteError(err.message || 'Failed to generate routes.');
    } finally {
      setLoadingRoutes(false);
    }
  }, []);

  useEffect(() => {
    fetchActiveLandslides();
    fetchRoutes(sourceCoords, destCoords, travelMeta.date, travelMeta.time);
  }, []);

  const handleLocationsResolved = ({ source, destination, date, time }) => {
    setSourceCoords(source);
    setDestCoords(destination);
    setTravelMeta({ date, time });
    fetchRoutes(source, destination, date, time);
  };

  const handleSelectRoute = (idx) => {
    const route = routes[idx];
    if (!route || route.is_blocked) return;
    setSelectedRoute(idx);
    setBlockedLandslideHazard(null);
    if (route.coordinates) {
      fetchTrafficFlow(route.coordinates);
      fetchRouteEvents(route.coordinates, `${travelMeta.date}T${travelMeta.time}:00Z`);
    }
  };

  const safeRouteName =
    routes.find((r) => !r.is_blocked && r.is_recommended)?.name ||
    routes.find((r) => !r.is_blocked)?.name ||
    'Alternative Safe Bypass';

  const hasBlockedRoutes = routes.some((r) => r.is_blocked);

  if (currentView === 'ADMIN_MAIN') {
    return (
      <AdminDashboard 
        onBackToDashboard={() => setCurrentView('DASHBOARD')} 
        onNavigate={(view) => setCurrentView(view)}
      />
    );
  }
  if (currentView === 'ADMIN_USERS') {
    return <UsersPage onBack={() => setCurrentView('ADMIN_MAIN')} />;
  }
  if (currentView === 'ADMIN_MODELS') {
    return <ModelsPage onBack={() => setCurrentView('ADMIN_MAIN')} />;
  }
  if (currentView === 'ADMIN_LOGS') {
    return <LogsPage onBack={() => setCurrentView('ADMIN_MAIN')} />;
  }
  if (currentView === 'ADMIN_EVENTS') {
    return <EventsPage onBackToDashboard={() => setCurrentView('ADMIN_MAIN')} />;
  }
  if (currentView === 'ADMIN_LANDSLIDES') {
    return (
      <LandslidesPage
        onBackToDashboard={() => {
          setCurrentView('ADMIN_MAIN');
          fetchActiveLandslides();
          fetchRoutes(sourceCoords, destCoords, travelMeta.date, travelMeta.time);
        }}
      />
    );
  }

  return (
    <div className="flex flex-col h-screen w-screen bg-slate-950 text-slate-100 overflow-hidden">
      {/* ── Header ─────────────────────────────────────────────────────────── */}
      <header className="h-16 shrink-0 bg-slate-900/80 backdrop-blur border-b border-slate-800 px-6 flex items-center justify-between z-20">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-teal-600 to-emerald-500 flex items-center justify-center shadow-lg shadow-teal-900/30">
            <Compass className="w-5 h-5 text-white animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-bold tracking-tight bg-gradient-to-r from-teal-400 via-emerald-300 to-sky-400 bg-clip-text text-transparent">
                RouteIQ
              </h1>
              <span className="text-[10px] uppercase font-mono px-2 py-0.5 bg-teal-500/10 text-teal-400 border border-teal-500/20 rounded-full">
                Live ORS · TomTom · Meteo · Events · CatBoost
              </span>
            </div>
            <p className="text-[11px] text-slate-400">
              Smart Traffic Congestion Prediction &amp; Route Recommendation
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {activeLandslides.length > 0 && (
            <button
              onClick={() => setCurrentView('ADMIN_LANDSLIDES')}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-red-500/10 hover:bg-red-500/20 border border-red-500/40 text-xs text-red-300 font-semibold transition-all animate-pulse"
            >
              <AlertOctagon className="w-3.5 h-3.5 text-red-400" />
              <span>{activeLandslides.length} Active Hazard{activeLandslides.length > 1 ? 's' : ''}</span>
            </button>
          )}
          <button
            onClick={() => setCurrentView('ADMIN_LANDSLIDES')}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 text-xs text-rose-300 font-semibold transition-all"
          >
            <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
            <span className="hidden sm:inline">Landslides</span>
          </button>
          <button
            onClick={() => setCurrentView('ADMIN_EVENTS')}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-purple-500/10 hover:bg-purple-500/20 border border-purple-500/30 text-xs text-purple-300 font-semibold transition-all"
          >
            <Calendar className="w-3.5 h-3.5 text-purple-400" />
            <span className="hidden sm:inline">Events</span>
          </button>
          <button
            onClick={() => setIsSchedulerModalOpen(true)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 text-xs text-emerald-300 font-medium transition-all"
          >
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
            </span>
            <Activity className="w-3.5 h-3.5 text-emerald-400" />
            <span className="hidden sm:inline">APScheduler</span>
          </button>
          <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs text-slate-300">
            <Layers className="w-3.5 h-3.5 text-emerald-400" />
            <span>{routes.length} Routes</span>
          </div>
          <NotificationPanel />
        </div>
      </header>

      {/* ── Main Workspace ─────────────────────────────────────────────────── */}
      <div className="flex-1 flex overflow-hidden">
        {/* ── Left Sidebar ────────────────────────────────────────────────── */}
        <aside className="w-full md:w-[420px] lg:w-[460px] shrink-0 border-r border-slate-800 bg-slate-950/95 flex flex-col overflow-y-auto p-4 space-y-4">
          <SearchForm onLocationsResolved={handleLocationsResolved} />

          {routeError && (
            <div className="flex items-start gap-2 p-3 bg-rose-500/10 border border-rose-500/30 rounded-lg text-rose-300 text-xs">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <div className="flex-1">{routeError}</div>
            </div>
          )}

          {blockedLandslideHazard && (
            <LandslideAlert
              hazard={blockedLandslideHazard}
              recommendedRouteName={safeRouteName}
            />
          )}

          <WeatherCard forecastWeather={weatherData} loading={loadingWeather} />
          <TrafficCard trafficData={trafficData} loading={loadingTraffic} />

          {routeEvents.length > 0 && (
            <div className="space-y-2">
              <div className="text-xs font-semibold uppercase tracking-wider text-amber-400 flex items-center gap-1.5">
                <Flame className="w-3.5 h-3.5" />
                Active Gatherings on Route ({routeEvents.length})
              </div>
              <div className="space-y-2">
                {routeEvents.map((ev, idx) => (
                  <div key={idx} className="p-3 bg-amber-500/10 border border-amber-500/30 rounded-xl text-xs space-y-1.5">
                    <div className="flex items-center justify-between font-bold text-slate-100">
                      <span>{ev.title}</span>
                      <span className="px-2 py-0.5 rounded text-[10px] bg-amber-500/20 text-amber-300 border border-amber-500/40">
                        {Math.round(ev.impact_score * 100)}% Impact
                      </span>
                    </div>
                    <div className="text-[11px] text-slate-300 flex items-center justify-between">
                      <span>Dist: {ev.min_distance_m}m</span>
                      <span className="text-amber-400 font-semibold">{ev.delay_multiplier}x delay</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ── Tab Switcher: Cards / Compare / Chart ───────────────────── */}
          <div className="flex items-center rounded-xl overflow-hidden border border-slate-800 bg-slate-900/60 text-xs shrink-0">
            {[
              { id: 'cards', label: 'Route Cards', icon: <Layers className="w-3 h-3" /> },
              { id: 'compare', label: 'Compare', icon: <Table2 className="w-3 h-3" /> },
              { id: 'chart', label: 'Chart', icon: <BarChart2 className="w-3 h-3" /> },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setSidebarTab(tab.id)}
                className={`flex-1 flex items-center justify-center gap-1.5 py-2 font-medium transition-all ${
                  sidebarTab === tab.id
                    ? 'bg-teal-500/20 text-teal-300 border-b-2 border-teal-500'
                    : 'text-slate-500 hover:text-slate-300'
                }`}
              >
                {tab.icon}
                <span className="hidden sm:inline">{tab.label}</span>
              </button>
            ))}
          </div>

          {/* Route Cards */}
          {sidebarTab === 'cards' && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                  <Layers className="w-3.5 h-3.5 text-blue-400" />
                  {hasBlockedRoutes
                    ? `Routes — ${routes.filter((r) => r.is_blocked).length} Hazard Blocked`
                    : `Available Routes (${routes.length})`}
                </h3>
                {loadingRoutes && (
                  <div className="flex items-center gap-1 text-[11px] text-blue-400 animate-pulse">
                    <RefreshCw className="w-3 h-3 animate-spin" />
                    Generating...
                  </div>
                )}
              </div>
              <div className="space-y-2.5">
                {routes.map((route, idx) => (
                  <RouteCard
                    key={idx}
                    route={route}
                    index={idx}
                    isSelected={selectedRoute === idx}
                    onSelect={handleSelectRoute}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Route Comparison Cards */}
          {sidebarTab === 'compare' && (
            <RouteComparison
              routes={routes}
              selectedRoute={selectedRoute}
              onSelect={handleSelectRoute}
            />
          )}

          {/* Prediction Chart */}
          {sidebarTab === 'chart' && (
            <PredictionChart
              routes={routes}
              title="Speed & Travel Time Predictions"
            />
          )}

          {/* Congestion Legend */}
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5 space-y-2">
            <div className="text-[11px] font-semibold text-slate-400 flex items-center gap-1">
              <TrendingUp className="w-3 h-3 text-emerald-400" />
              Route Status Benchmark
            </div>
            <div className="grid grid-cols-5 gap-1.5 text-center text-[9px]">
              <div className="p-1 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-bold">SAFE</div>
              <div className="p-1 rounded bg-blue-500/10 border border-blue-500/20 text-blue-400 font-bold">LOW</div>
              <div className="p-1 rounded bg-amber-500/10 border border-amber-500/20 text-amber-400 font-bold">MEDIUM</div>
              <div className="p-1 rounded bg-orange-500/10 border border-orange-500/20 text-orange-400 font-bold">HIGH</div>
              <div className="p-1 rounded bg-rose-500/10 border border-rose-500/20 text-rose-400 font-bold">BLOCKED</div>
            </div>
          </div>
        </aside>

        {/* ── Right Map Canvas ───────────────────────────────────────────── */}
        <main className="flex-1 relative bg-slate-950 p-3 flex flex-col min-w-0">
          <MapView
            sourceCoords={sourceCoords}
            destCoords={destCoords}
            routes={routes}
            landslides={activeLandslides}
            selectedRoute={selectedRoute}
            onSelectRoute={handleSelectRoute}
          />
        </main>
      </div>

      <SchedulerStatusModal
        isOpen={isSchedulerModalOpen}
        onClose={() => setIsSchedulerModalOpen(false)}
      />
    </div>
  );
}
