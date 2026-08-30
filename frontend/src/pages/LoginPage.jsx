import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Eye, EyeOff, MapPin, Lock, Mail, User, Compass, Sun, Moon, ArrowRight, ShieldCheck, Sparkles } from 'lucide-react';
import { setSession } from '../services/auth';
import { useTheme } from '../contexts/ThemeContext';

export default function LoginPage() {
  const [tab, setTab] = useState('login');
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({ fullName: '', email: '', password: '', confirmPassword: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const navigate = useNavigate();
  const { theme, toggleTheme, isDark } = useTheme();

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      if (tab === 'login') {
        const res = await axios.post('/api/auth/login', {
          email: formData.email.trim(),
          password: formData.password
        });
        const token = res.data.access_token || res.data.token;
        setSession(token, res.data.user);
        if (res.data.user?.role === 'admin') navigate('/admin');
        else navigate('/dashboard');
      } else {
        if (formData.password !== formData.confirmPassword) {
          setError("Passwords do not match");
          setLoading(false);
          return;
        }
        const res = await axios.post('/api/auth/register', {
          name: formData.fullName.trim(),
          email: formData.email.trim(),
          password: formData.password
        });
        const token = res.data.access_token || res.data.token;
        setSession(token, res.data.user);
        navigate('/dashboard');
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Authentication failed. Please check credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col md:flex-row w-full bg-white dark:bg-slate-950 text-gray-900 dark:text-slate-100 transition-colors duration-200">
      {/* Left Branding Hero */}
      <div className="w-full md:w-1/2 bg-gradient-to-br from-indigo-600 via-indigo-700 to-purple-900 dark:from-slate-900 dark:via-indigo-950 dark:to-slate-900 flex flex-col justify-between p-8 md:p-14 text-white relative overflow-hidden">
        {/* Ambient background blur blobs */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/20 rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none"></div>
        <div className="absolute bottom-0 left-0 w-80 h-80 bg-purple-500/20 rounded-full blur-3xl -ml-20 -mb-20 pointer-events-none"></div>

        {/* Top Logo */}
        <div className="flex items-center gap-3 relative z-10">
          <div className="w-10 h-10 rounded-2xl bg-white dark:bg-indigo-600 flex items-center justify-center shadow-lg">
            <Compass className="w-6 h-6 text-indigo-600 dark:text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white">RouteIQ</h1>
            <p className="text-[10px] text-indigo-200 dark:text-slate-400 uppercase tracking-widest font-mono">Intelligent Transit System</p>
          </div>
        </div>

        {/* Center Pitch */}
        <div className="my-12 relative z-10 max-w-lg">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 dark:bg-indigo-500/20 border border-white/20 dark:border-indigo-500/30 text-xs font-semibold mb-6 backdrop-blur">
            <Sparkles className="w-3.5 h-3.5 text-amber-300" /> Real-Time Traffic & Safety Forecasting
          </div>
          <h1 className="text-3xl md:text-5xl font-extrabold tracking-tight leading-tight mb-4">
            Predict congestion before you hit the road.
          </h1>
          <p className="text-sm md:text-base text-indigo-100 dark:text-slate-300 leading-relaxed">
            PatchTST deep time-series neural models paired with CatBoost gradient boosted safety evaluation for Coimbatore and South Indian corridors.
          </p>
        </div>

        {/* Bottom Metrics Pill */}
        <div className="grid grid-cols-3 gap-4 pt-6 border-t border-white/15 dark:border-slate-800 text-xs relative z-10">
          <div>
            <p className="text-indigo-200 dark:text-slate-400 text-[10px] uppercase font-semibold">Forecasting</p>
            <p className="font-extrabold text-sm md:text-base mt-0.5">PatchTST</p>
          </div>
          <div>
            <p className="text-indigo-200 dark:text-slate-400 text-[10px] uppercase font-semibold">Ranking</p>
            <p className="font-extrabold text-sm md:text-base mt-0.5">CatBoost</p>
          </div>
          <div>
            <p className="text-indigo-200 dark:text-slate-400 text-[10px] uppercase font-semibold">Telemetry</p>
            <p className="font-extrabold text-sm md:text-base mt-0.5">Live ORS</p>
          </div>
        </div>
      </div>

      {/* Right Login / Register Box */}
      <div className="w-full md:w-1/2 flex flex-col justify-center items-center p-8 md:p-14 relative bg-gray-50/50 dark:bg-slate-950">
        {/* Top Right Dark/Light Toggle */}
        <div className="absolute top-6 right-6">
          <button
            onClick={toggleTheme}
            className="p-2.5 rounded-2xl bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 text-gray-700 dark:text-amber-400 shadow-sm hover:scale-105 transition"
            title={isDark ? "Light Mode" : "Dark Mode"}
          >
            {isDark ? <Sun size={18} /> : <Moon size={18} />}
          </button>
        </div>

        <div className="w-full max-w-md bg-white dark:bg-slate-900 p-8 md:p-10 rounded-3xl shadow-xl shadow-slate-200/50 dark:shadow-none border border-gray-100 dark:border-slate-800">
          {/* Header Tabs */}
          <div className="flex border-b border-gray-100 dark:border-slate-800 mb-8">
            <button 
              className={`flex-1 pb-4 text-center font-bold text-base transition-colors border-b-2 ${tab === 'login' ? 'border-indigo-600 text-indigo-600 dark:text-indigo-400' : 'border-transparent text-gray-400 dark:text-slate-500 hover:text-gray-600'}`}
              onClick={() => { setTab('login'); setError(''); }}
            >
              Sign In
            </button>
            <button 
              className={`flex-1 pb-4 text-center font-bold text-base transition-colors border-b-2 ${tab === 'signup' ? 'border-indigo-600 text-indigo-600 dark:text-indigo-400' : 'border-transparent text-gray-400 dark:text-slate-500 hover:text-gray-600'}`}
              onClick={() => { setTab('signup'); setError(''); }}
            >
              Register Account
            </button>
          </div>

          {error && (
            <div className="mb-6 p-3.5 rounded-2xl bg-rose-50 dark:bg-rose-950/50 border border-rose-200 dark:border-rose-900/50 text-xs font-semibold text-rose-600 dark:text-rose-400">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {tab === 'signup' && (
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 dark:text-slate-400 mb-1.5">Full Name</label>
                <div className="relative">
                  <User className="absolute left-3.5 top-3.5 text-gray-400" size={18} />
                  <input 
                    required 
                    type="text" 
                    name="fullName" 
                    value={formData.fullName} 
                    onChange={handleInputChange} 
                    className="pl-10 w-full p-3 bg-gray-50 dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-xl text-sm font-medium text-gray-800 dark:text-slate-200 focus:ring-2 focus:ring-indigo-500 focus:outline-none transition" 
                    placeholder="Sanjana M" 
                  />
                </div>
              </div>
            )}

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 dark:text-slate-400 mb-1.5">Email Address</label>
              <div className="relative">
                <Mail className="absolute left-3.5 top-3.5 text-gray-400" size={18} />
                <input 
                  required 
                  type="email" 
                  name="email" 
                  value={formData.email} 
                  onChange={handleInputChange} 
                  className="pl-10 w-full p-3 bg-gray-50 dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-xl text-sm font-medium text-gray-800 dark:text-slate-200 focus:ring-2 focus:ring-indigo-500 focus:outline-none transition" 
                  placeholder="admin@goload.com" 
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 dark:text-slate-400 mb-1.5">Password</label>
              <div className="relative">
                <Lock className="absolute left-3.5 top-3.5 text-gray-400" size={18} />
                <input 
                  required 
                  type={showPassword ? 'text' : 'password'} 
                  name="password" 
                  value={formData.password} 
                  onChange={handleInputChange} 
                  className="pl-10 pr-10 w-full p-3 bg-gray-50 dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-xl text-sm font-medium text-gray-800 dark:text-slate-200 focus:ring-2 focus:ring-indigo-500 focus:outline-none transition" 
                  placeholder="••••••••" 
                />
                <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3.5 top-3.5 text-gray-400 hover:text-gray-600 dark:hover:text-slate-300">
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            {tab === 'signup' && (
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 dark:text-slate-400 mb-1.5">Confirm Password</label>
                <div className="relative">
                  <Lock className="absolute left-3.5 top-3.5 text-gray-400" size={18} />
                  <input 
                    required 
                    type={showPassword ? 'text' : 'password'} 
                    name="confirmPassword" 
                    value={formData.confirmPassword} 
                    onChange={handleInputChange} 
                    className="pl-10 w-full p-3 bg-gray-50 dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-xl text-sm font-medium text-gray-800 dark:text-slate-200 focus:ring-2 focus:ring-indigo-500 focus:outline-none transition" 
                    placeholder="••••••••" 
                  />
                </div>
              </div>
            )}
            
            {tab === 'login' && (
              <div className="flex items-center justify-between text-xs pt-1">
                <label className="flex items-center text-gray-600 dark:text-slate-400 cursor-pointer">
                  <input type="checkbox" className="mr-2 rounded text-indigo-600 focus:ring-indigo-500 dark:bg-slate-800 dark:border-slate-700" defaultChecked />
                  Remember me
                </label>
                <a href="#" onClick={(e) => { e.preventDefault(); alert("Admin password can be reset via: python scripts/create_admin.py"); }} className="text-indigo-600 dark:text-indigo-400 hover:underline font-semibold">Forgot Password?</a>
              </div>
            )}
            
            <button 
              type="submit" 
              disabled={loading}
              className="w-full mt-6 bg-indigo-600 hover:bg-indigo-700 text-white p-3.5 rounded-xl font-bold transition-all shadow-lg shadow-indigo-500/20 active:scale-98 disabled:opacity-50 text-sm flex items-center justify-center gap-2"
            >
              {loading ? (
                <span>Authenticating...</span>
              ) : (
                <>
                  <span>{tab === 'login' ? 'Sign In to RouteIQ' : 'Create My Account'}</span>
                  <ArrowRight size={16} />
                </>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
