import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Activity,
  Clock,
  CheckCircle2,
  AlertCircle,
  Play,
  RefreshCw,
  X,
  Database,
  Cpu,
  Shield,
} from 'lucide-react';

export default function SchedulerStatusModal({ isOpen, onClose }) {
  const [schedulerData, setSchedulerData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [triggeringJob, setTriggeringJob] = useState(null);
  const [actionMessage, setActionMessage] = useState(null);

  const fetchStatus = async () => {
    setLoading(true);
    try {
      const resp = await axios.get('/api/admin/scheduler/status');
      setSchedulerData(resp.data);
    } catch (err) {
      console.warn('Failed to fetch scheduler status:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchStatus();
      const interval = setInterval(fetchStatus, 10000); // Poll every 10s when modal is open
      return () => clearInterval(interval);
    }
  }, [isOpen]);

  const handleTriggerJob = async (jobId) => {
    setTriggeringJob(jobId);
    setActionMessage(null);
    try {
      const resp = await axios.post('/api/admin/scheduler/trigger-job', {
        job_id: jobId,
      });
      setActionMessage({
        type: 'success',
        text: `Triggered '${jobId}' successfully!`,
      });
      fetchStatus();
    } catch (err) {
      setActionMessage({
        type: 'error',
        text: `Failed to trigger '${jobId}'.`,
      });
    } finally {
      setTriggeringJob(null);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl w-full max-w-2xl overflow-hidden flex flex-col max-h-[85vh]">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center justify-center">
              <Activity className="w-4 h-4 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-bold text-slate-100">
                  APScheduler Automation Engine
                </h3>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                  {schedulerData?.scheduler_status || 'ACTIVE'}
                </span>
              </div>
              <p className="text-[11px] text-slate-400">
                Automated Background Data Ingestion · Timezone: {schedulerData?.timezone || 'Asia/Kolkata'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={fetchStatus}
              disabled={loading}
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
              title="Refresh status"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Feedback Alert */}
        {actionMessage && (
          <div
            className={`mx-6 mt-4 p-2.5 rounded-lg text-xs flex items-center gap-2 ${
              actionMessage.type === 'success'
                ? 'bg-emerald-500/10 border border-emerald-500/30 text-emerald-300'
                : 'bg-rose-500/10 border border-rose-500/30 text-rose-300'
            }`}
          >
            {actionMessage.type === 'success' ? (
              <CheckCircle2 className="w-4 h-4 shrink-0" />
            ) : (
              <AlertCircle className="w-4 h-4 shrink-0" />
            )}
            <span>{actionMessage.text}</span>
          </div>
        )}

        {/* Job List Content */}
        <div className="p-6 space-y-3.5 overflow-y-auto flex-1">
          <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
            <Cpu className="w-3.5 h-3.5 text-blue-400" />
            Registered Scheduled Jobs ({schedulerData?.jobs?.length || 4})
          </div>

          <div className="space-y-3">
            {schedulerData?.jobs?.map((job) => (
              <div
                key={job.job_id}
                className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800/90 hover:border-slate-700 transition-colors space-y-2.5"
              >
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-emerald-400 ring-2 ring-emerald-400/20"></span>
                      <h4 className="text-xs font-bold text-slate-200">
                        {job.name}
                      </h4>
                      <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                        Every {job.interval}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400 mt-0.5">
                      {job.description}
                    </p>
                  </div>

                  <button
                    onClick={() => handleTriggerJob(job.job_id)}
                    disabled={triggeringJob === job.job_id}
                    className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 border border-blue-500/30 text-[11px] font-medium transition-all shrink-0"
                  >
                    {triggeringJob === job.job_id ? (
                      <RefreshCw className="w-3 h-3 animate-spin" />
                    ) : (
                      <Play className="w-3 h-3" />
                    )}
                    Run Now
                  </button>
                </div>

                {/* Telemetry Row */}
                <div className="grid grid-cols-3 gap-2 text-[10px] bg-slate-900/90 p-2 rounded-lg border border-slate-800/60 font-mono">
                  <div>
                    <span className="text-slate-500">Status: </span>
                    <span
                      className={
                        job.last_status === 'SUCCESS'
                          ? 'text-emerald-400 font-bold'
                          : 'text-amber-400'
                      }
                    >
                      {job.last_status}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-500">Records: </span>
                    <span className="text-slate-200">
                      {job.last_records_collected} saved
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-500">Duration: </span>
                    <span className="text-slate-200">
                      {job.last_duration_ms}ms
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/60 text-[11px] text-slate-400 flex items-center gap-2">
            <Shield className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>
              <strong>ML Model Safety:</strong> Retraining pipelines (PatchTST & CatBoost) are guarded and strictly Admin-triggered to prevent resource locks.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
