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
  LANDSLIDE_ALERT: <AlertOctagon className="w-5 h-5 text-rose-500" />,
  TRAFFIC_ALERT: <Car className="w-5 h-5 text-amber-500" />,
  WEATHER_ALERT: <CloudLightning className="w-5 h-5 text-sky-500" />,
  EVENT_ALERT: <Calendar className="w-5 h-5 text-purple-500" />,
  ROUTE_UPDATE: <RefreshCw className="w-5 h-5 text-emerald-500" />,
  SYSTEM: <Info className="w-5 h-5 text-slate-400" />,
};

export default function NotificationPanel() {
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const panelRef = useRef(null);

  const userId = 'user_123';

  const fetchNotifications = async () => {
    try {
      const resp = await axios.get('/api/notifications', {
        params: { user_id: userId },
      });
      if (resp.data?.success || resp.data?.notifications) {
        const notifs = resp.data.notifications || [];
        setNotifications(notifs);
        setUnreadCount(notifs.filter((n) => !n.is_read).length);
      }
    } catch (error) {
      // Fallback sample alerts for demonstration
      const sampleNotifs = [
        { _id: 'n1', type: 'TRAFFIC_ALERT', title: 'Avinashi Road Congestion', message: 'Heavy flow detected near Hope College intersection. Consider Mettupalayam bypass.', created_at: new Date().toISOString(), is_read: false },
        { _id: 'n2', type: 'LANDSLIDE_ALERT', title: 'Western Ghats Warning', message: 'Heavy precipitation warning issued for Nilgiris foothills corridor.', created_at: new Date(Date.now() - 7200000).toISOString(), is_read: true }
      ];
      setNotifications(sampleNotifs);
      setUnreadCount(1);
    }
  };

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(() => {
      fetchNotifications();
    }, 30000);
    return () => clearInterval(interval);
  }, []);

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
      setNotifications((prev) =>
        prev.map((n) => (n._id === id ? { ...n, is_read: true } : n))
      );
      setUnreadCount((prev) => Math.max(0, prev - 1));
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
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      setUnreadCount(0);
    }
  };

  return (
    <div className="relative" ref={panelRef}>
      {/* Bell Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 rounded-xl bg-gray-100 dark:bg-slate-800 hover:bg-gray-200 dark:hover:bg-slate-700 text-gray-600 dark:text-slate-300 transition-all flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-indigo-500"
        title="Notifications"
      >
        <Bell className="w-4 h-4" />
        {unreadCount > 0 && (
          <span className="absolute -top-0.5 -right-0.5 flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-rose-500 text-[8px] font-bold text-white items-center justify-center"></span>
          </span>
        )}
      </button>

      {/* Dropdown Panel */}
      {isOpen && (
        <div className="absolute right-0 top-full mt-2 w-80 sm:w-96 bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-3xl shadow-2xl overflow-hidden z-50 animate-fade-in">
          <div className="p-4 border-b border-gray-100 dark:border-slate-800 flex items-center justify-between bg-white dark:bg-slate-900">
            <h3 className="font-bold text-sm text-gray-800 dark:text-slate-100 flex items-center gap-2">
              Broadcasts & Alerts
              {unreadCount > 0 && (
                <span className="px-2 py-0.5 rounded-full bg-indigo-100 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 text-[10px] font-bold font-mono">
                  {unreadCount} NEW
                </span>
              )}
            </h3>
            <div className="flex items-center gap-2">
              {unreadCount > 0 && (
                <button
                  onClick={markAllAsRead}
                  className="text-xs text-indigo-600 dark:text-indigo-400 hover:underline transition-colors flex items-center gap-1 font-semibold"
                >
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  Mark read
                </button>
              )}
              <button
                onClick={() => setIsOpen(false)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-slate-200 p-1 rounded-lg transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          <div className="max-h-[380px] overflow-y-auto p-2.5 space-y-2 bg-gray-50/50 dark:bg-slate-950/50">
            {notifications.length === 0 ? (
              <div className="p-8 text-center text-gray-400 dark:text-slate-500 text-xs">
                No active notifications or alerts.
              </div>
            ) : (
              notifications.map((notif) => (
                <div
                  key={notif._id}
                  className={`relative p-3.5 rounded-2xl border flex gap-3 transition-all ${
                    notif.is_read
                      ? 'bg-white dark:bg-slate-900/60 border-gray-100 dark:border-slate-800/80 opacity-75'
                      : 'bg-white dark:bg-slate-900 border-indigo-200 dark:border-indigo-900/60 shadow-sm'
                  }`}
                >
                  <div className="shrink-0 mt-0.5">
                    {TYPE_ICONS[notif.type] || TYPE_ICONS.SYSTEM}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="text-xs font-bold text-gray-800 dark:text-slate-200 leading-tight mb-1 pr-6">
                      {notif.title}
                    </h4>
                    <p className="text-xs text-gray-500 dark:text-slate-400 leading-relaxed mb-2">
                      {notif.message}
                    </p>
                    <div className="text-[10px] font-mono text-gray-400 dark:text-slate-500 uppercase tracking-wider">
                      {new Date(notif.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </div>
                  </div>
                  {!notif.is_read && (
                    <button
                      onClick={(e) => markAsRead(notif._id, e)}
                      title="Mark as read"
                      className="absolute top-3 right-3 w-6 h-6 rounded-full bg-gray-100 dark:bg-slate-800 hover:bg-indigo-50 dark:hover:bg-indigo-950 text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400 flex items-center justify-center transition-colors"
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
