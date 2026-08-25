import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import {
  Bell,
  AlertOctagon,
  CloudLightning,
  Calendar,
  Car,
  Info,
  CheckCircle2,
  X,
  RefreshCw,
} from 'lucide-react';

const TYPE_ICONS = {
  LANDSLIDE_ALERT: <AlertOctagon className="w-5 h-5 text-rose-400" />,
  TRAFFIC_ALERT: <Car className="w-5 h-5 text-amber-400" />,
  WEATHER_ALERT: <CloudLightning className="w-5 h-5 text-sky-400" />,
  EVENT_ALERT: <Calendar className="w-5 h-5 text-purple-400" />,
  ROUTE_UPDATE: <RefreshCw className="w-5 h-5 text-emerald-400" />,
  SYSTEM: <Info className="w-5 h-5 text-slate-400" />,
};

export default function NotificationPanel() {
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const panelRef = useRef(null);

  // Default simulated user for Phase 11
  const userId = 'user_123';

  const fetchNotifications = async () => {
    try {
      const resp = await axios.get('/api/notifications', {
        params: { user_id: userId },
      });
      if (resp.data.success) {
        const notifs = resp.data.notifications || [];
        setNotifications(notifs);
        setUnreadCount(notifs.filter((n) => !n.is_read).length);
      }
    } catch (error) {
      console.warn('Failed to fetch notifications:', error);
    }
  };

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(() => {
      fetchNotifications();
    }, 60000); // Poll every 60s
    return () => clearInterval(interval);
  }, []);

  // Close when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (panelRef.current && !panelRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const markAsRead = async (id, e) => {
    e.stopPropagation();
    try {
      await axios.put(`/api/notifications/${id}/read`, null, {
        params: { user_id: userId },
      });
      setNotifications((prev) =>
        prev.map((n) => (n._id === id ? { ...n, is_read: true } : n))
      );
      setUnreadCount((prev) => Math.max(0, prev - 1));
    } catch (error) {
      console.warn('Failed to mark notification as read:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      await axios.put('/api/notifications/read-all', null, {
        params: { user_id: userId },
      });
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch (error) {
      console.warn('Failed to mark all as read:', error);
    }
  };

  return (
    <div className="relative" ref={panelRef}>
      {/* Bell Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 rounded-xl hover:bg-slate-800 transition-colors flex items-center justify-center text-slate-400 hover:text-slate-200"
      >
        <Bell className="w-5 h-5" />
        {unreadCount > 0 && (
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-rose-500 rounded-full animate-pulse border border-slate-900"></span>
        )}
      </button>

      {/* Dropdown Panel */}
      {isOpen && (
        <div className="absolute right-0 top-full mt-2 w-80 sm:w-96 bg-slate-900 border border-slate-700/60 rounded-2xl shadow-2xl overflow-hidden z-50 animate-in fade-in slide-in-from-top-2 duration-200">
          <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/90 backdrop-blur">
            <h3 className="font-bold text-sm text-slate-100 flex items-center gap-2">
              Notifications
              {unreadCount > 0 && (
                <span className="px-2 py-0.5 rounded-full bg-teal-500/20 text-teal-400 text-[10px] font-mono">
                  {unreadCount} NEW
                </span>
              )}
            </h3>
            <div className="flex items-center gap-3">
              {unreadCount > 0 && (
                <button
                  onClick={markAllAsRead}
                  className="text-xs text-slate-400 hover:text-teal-400 transition-colors flex items-center gap-1 font-medium"
                >
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  Mark all read
                </button>
              )}
              <button
                onClick={() => setIsOpen(false)}
                className="text-slate-500 hover:text-slate-300 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          <div className="max-h-[400px] overflow-y-auto p-2 space-y-1 bg-slate-950/50">
            {notifications.length === 0 ? (
              <div className="p-8 text-center text-slate-500 text-sm">
                No notifications yet.
              </div>
            ) : (
              notifications.map((notif) => (
                <div
                  key={notif._id}
                  className={`relative p-3 rounded-xl border flex gap-3 transition-colors ${
                    notif.is_read
                      ? 'bg-slate-900/50 border-transparent opacity-70'
                      : 'bg-slate-800/80 border-slate-700/60 shadow-lg'
                  }`}
                >
                  <div className="shrink-0 mt-0.5">
                    {TYPE_ICONS[notif.type] || TYPE_ICONS.SYSTEM}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-semibold text-slate-200 leading-tight mb-1 pr-6">
                      {notif.title}
                    </h4>
                    <p className="text-xs text-slate-400 leading-relaxed mb-2">
                      {notif.message}
                    </p>
                    <div className="text-[10px] font-mono text-slate-500 uppercase tracking-wider">
                      {new Date(notif.created_at).toLocaleString()}
                    </div>
                  </div>
                  {!notif.is_read && (
                    <button
                      onClick={(e) => markAsRead(notif._id, e)}
                      title="Mark as read"
                      className="absolute top-3 right-3 w-5 h-5 rounded-full bg-slate-700/50 hover:bg-teal-500/20 text-slate-400 hover:text-teal-400 flex items-center justify-center transition-colors"
                    >
                      <CheckCircle2 className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
