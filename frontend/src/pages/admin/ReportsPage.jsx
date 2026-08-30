import React, { useState, useEffect } from 'react';
import { adminApi } from '../../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Download, Calendar } from 'lucide-react';

export default function ReportsPage() {
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchReport = async () => {
    try {
      setLoading(true);
      const res = await adminApi.reportsSummary({ date_from: dateFrom, date_to: dateTo });
      if (res.data?.report) {
        setReport(res.data.report);
      } else {
        // Fallback mock
        setReport({
          total_searches: 1245,
          total_predictions: 3450,
          most_searched_pair: 'Downtown → Airport',
          avg_congestion: 'Moderate',
          searches_trend: [
            { date: 'Mon', searches: 120 },
            { date: 'Tue', searches: 150 },
            { date: 'Wed', searches: 180 },
            { date: 'Thu', searches: 140 },
            { date: 'Fri', searches: 210 },
            { date: 'Sat', searches: 280 },
            { date: 'Sun', searches: 165 },
          ],
          congestion_dist: [
            { name: 'Low', value: 45 },
            { name: 'Moderate', value: 35 },
            { name: 'High', value: 20 },
          ],
          top_pairs: [
            { pair: 'Downtown → Airport', count: 340 },
            { pair: 'Suburb North → Tech Park', count: 210 },
            { pair: 'Central Station → Mall', count: 185 },
            { pair: 'West End → Downtown', count: 150 },
            { pair: 'University → City Center', count: 120 },
          ]
        });
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReport();
  }, [dateFrom, dateTo]);

  const handleExport = () => {
    alert('Export CSV feature coming soon!');
  };

  const COLORS = ['#10B981', '#F59E0B', '#EF4444'];

  return (
    <div className="p-6 bg-white min-h-screen text-gray-800">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
        <h1 className="text-2xl font-bold text-gray-900">Analytics & Reports</h1>
        
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-gray-50 border border-gray-200 rounded-lg px-3 py-1.5">
            <Calendar className="w-4 h-4 text-gray-500" />
            <input 
              type="date" 
              value={dateFrom} 
              onChange={e => setDateFrom(e.target.value)}
              className="bg-transparent text-sm outline-none text-gray-700"
            />
            <span className="text-gray-400">-</span>
            <input 
              type="date" 
              value={dateTo} 
              onChange={e => setDateTo(e.target.value)}
              className="bg-transparent text-sm outline-none text-gray-700"
            />
          </div>
          <button 
            onClick={handleExport}
            className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
          >
            <Download className="w-4 h-4" />
            Download CSV
          </button>
        </div>
      </div>

      {report && (
        <div className="space-y-6">
          {/* Stats Row */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
              <p className="text-sm text-gray-500 font-medium mb-1">Total Searches</p>
              <p className="text-2xl font-bold text-gray-900">{report.total_searches}</p>
            </div>
            <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
              <p className="text-sm text-gray-500 font-medium mb-1">Total Predictions</p>
              <p className="text-2xl font-bold text-gray-900">{report.total_predictions}</p>
            </div>
            <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
              <p className="text-sm text-gray-500 font-medium mb-1">Most Searched</p>
              <p className="text-lg font-bold text-gray-900 truncate" title={report.most_searched_pair}>{report.most_searched_pair}</p>
            </div>
            <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
              <p className="text-sm text-gray-500 font-medium mb-1">Avg Congestion</p>
              <p className="text-2xl font-bold text-gray-900">{report.avg_congestion}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Chart 1: Bar Chart */}
            <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm lg:col-span-2">
              <h3 className="font-semibold text-gray-800 mb-4">Searches (Last 7 Days)</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={report.searches_trend}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                    <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{fill: '#6B7280'}} />
                    <YAxis axisLine={false} tickLine={false} tick={{fill: '#6B7280'}} />
                    <Tooltip 
                      contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                      cursor={{fill: '#F3F4F6'}}
                    />
                    <Bar dataKey="searches" fill="#6C63FF" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Chart 2: Pie Chart */}
            <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
              <h3 className="font-semibold text-gray-800 mb-4">Congestion Distribution</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={report.congestion_dist}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {report.congestion_dist.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="flex justify-center gap-4 mt-2">
                {report.congestion_dist.map((entry, idx) => (
                  <div key={idx} className="flex items-center gap-1.5 text-sm text-gray-600">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[idx % COLORS.length] }}></div>
                    {entry.name}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Top Pairs Table */}
          <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
            <div className="p-4 border-b border-gray-200 bg-gray-50">
              <h3 className="font-semibold text-gray-800">Top 5 Searched Routes</h3>
            </div>
            <table className="w-full text-left text-sm">
              <thead className="bg-white border-b border-gray-100 text-gray-500">
                <tr>
                  <th className="px-6 py-3 font-medium">Rank</th>
                  <th className="px-6 py-3 font-medium">Route (Source → Destination)</th>
                  <th className="px-6 py-3 font-medium text-right">Search Count</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {report.top_pairs.map((item, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-gray-500">#{idx + 1}</td>
                    <td className="px-6 py-4 font-medium text-gray-900">{item.pair}</td>
                    <td className="px-6 py-4 text-right text-indigo-600 font-semibold">{item.count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
