import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Database, Play, CheckCircle2, AlertTriangle, RefreshCw } from 'lucide-react';
import { adminApi } from '../../services/api';

export default function ModelsPage() {
  const navigate = useNavigate();
  const [patchMetrics, setPatchMetrics] = useState(null);
  const [catMetrics, setCatMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [trainingState, setTrainingState] = useState({}); // { patch: bool, cat: bool }

  useEffect(() => {
    fetchMetrics();
  }, []);

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      const [pRes, cRes] = await Promise.allSettled([
        adminApi.patchtstMetrics(),
        adminApi.catboostMetrics()
      ]);

      if (pRes.status === 'fulfilled') {
        setPatchMetrics(pRes.value.data.metrics);
      } else {
        setPatchMetrics(null);
      }

      if (cRes.status === 'fulfilled') {
        setCatMetrics(cRes.value.data.metrics);
      } else {
        setCatMetrics(null);
      }
    } finally {
      setLoading(false);
    }
  };

  const trainModel = async (modelName) => {
    try {
      setTrainingState(prev => ({ ...prev, [modelName]: true }));
      if (modelName === 'patch') {
        await adminApi.patchtstTrain();
      } else {
        await adminApi.catboostTrain();
      }
      alert(`${modelName.toUpperCase()} training started in background. Refresh later to see new metrics.`);
    } catch (err) {
      alert(`Failed to start training: ${err.message}`);
    } finally {
      setTrainingState(prev => ({ ...prev, [modelName]: false }));
    }
  };

  const MetricCard = ({ label, value }) => (
    <div className="bg-slate-950/50 p-4 rounded-lg border border-slate-800">
      <div className="text-[11px] text-slate-500 uppercase tracking-wider mb-1">{label}</div>
      <div className="text-xl font-bold text-slate-200">{value ?? '—'}</div>
    </div>
  );

  return (
    <div className="flex flex-col h-screen bg-slate-950 text-slate-100 overflow-y-auto">
      <header className="shrink-0 h-16 bg-slate-900/80 backdrop-blur border-b border-slate-800 px-6 flex items-center justify-between sticky top-0 z-10">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate('/admin')} className="p-2 -ml-2 rounded-lg hover:bg-slate-800 text-slate-400">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-lg font-bold flex items-center gap-2">
              <Database className="w-5 h-5 text-emerald-400" />
              ML Models Management
            </h1>
          </div>
        </div>
        <button onClick={fetchMetrics} className="p-2 rounded-lg hover:bg-slate-800 text-slate-400">
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </header>

      <div className="max-w-4xl w-full mx-auto p-6 space-y-6">
        {/* PatchTST Section */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h2 className="text-xl font-bold text-teal-400 mb-1">PatchTST</h2>
              <p className="text-sm text-slate-400">Time-series forecasting for traffic flow and speed.</p>
            </div>
            <button
              onClick={() => trainModel('patch')}
              disabled={trainingState.patch}
              className="flex items-center gap-2 px-4 py-2 bg-teal-500/10 hover:bg-teal-500/20 text-teal-400 border border-teal-500/30 rounded-lg text-sm font-semibold transition-colors disabled:opacity-50"
            >
              <Play className="w-4 h-4" />
              {trainingState.patch ? 'Training...' : 'Train PatchTST'}
            </button>
          </div>

          {!patchMetrics ? (
            <div className="flex items-center gap-2 text-slate-500 text-sm">
              <AlertTriangle className="w-4 h-4" />
              Not trained yet. No metrics available.
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-sm text-slate-400">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                Last trained: {new Date(patchMetrics.trained_at || patchMetrics.timestamp).toLocaleString()}
              </div>
              <div className="grid grid-cols-3 gap-4">
                <MetricCard label="MAE" value={patchMetrics.mae?.toFixed(4) || patchMetrics.metrics?.mae?.toFixed(4)} />
                <MetricCard label="RMSE" value={patchMetrics.rmse?.toFixed(4) || patchMetrics.metrics?.rmse?.toFixed(4)} />
                <MetricCard label="MAPE" value={patchMetrics.mape?.toFixed(4) || patchMetrics.metrics?.mape?.toFixed(4)} />
              </div>
            </div>
          )}
        </div>

        {/* CatBoost Section */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h2 className="text-xl font-bold text-orange-400 mb-1">CatBoost</h2>
              <p className="text-sm text-slate-400">Gradient boosting classifier for route recommendation ranking.</p>
            </div>
            <button
              onClick={() => trainModel('cat')}
              disabled={trainingState.cat}
              className="flex items-center gap-2 px-4 py-2 bg-orange-500/10 hover:bg-orange-500/20 text-orange-400 border border-orange-500/30 rounded-lg text-sm font-semibold transition-colors disabled:opacity-50"
            >
              <Play className="w-4 h-4" />
              {trainingState.cat ? 'Training...' : 'Train CatBoost'}
            </button>
          </div>

          {!catMetrics ? (
            <div className="flex items-center gap-2 text-slate-500 text-sm">
              <AlertTriangle className="w-4 h-4" />
              Not trained yet. No metrics available.
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-sm text-slate-400">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                Last trained: {new Date(catMetrics.trained_at).toLocaleString()}
              </div>
              <div className="grid grid-cols-3 gap-4">
                <MetricCard label="Accuracy" value={catMetrics.accuracy} />
                <MetricCard label="F1 Score" value={catMetrics.f1} />
                <MetricCard label="AUC" value={catMetrics.auc} />
              </div>
              <div className="mt-4 text-xs text-slate-500 bg-slate-950 p-3 rounded-lg border border-slate-800 font-mono">
                {catMetrics.labelling_rule}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
