import React from 'react';
import PerformanceSection from '../PerformanceSection';
import { ChartCard, MonthlyChart } from '../Charts';
import { CheckCircle, AlertTriangle, XCircle, Activity } from 'lucide-react';

interface PerformanceTabProps {
  darkMode: boolean;
  apiLatencyMs?: number | null;
}

const PerformanceTab: React.FC<PerformanceTabProps> = ({ darkMode, apiLatencyMs }) => {
  const incidents = [
    { title: 'API Gateway latency spike', time: 'Dec 18, 14:32', status: 'resolved', duration: '12 min' },
    { title: 'Database connection pool exhausted', time: 'Dec 15, 09:15', status: 'resolved', duration: '28 min' },
  ];

  const currentLatency = apiLatencyMs ?? 0;

  const slaMetrics = [
    { label: 'Uptime SLA', target: '99.9%', actual: '100.0%', status: 'met' },
    { label: 'API Response SLA', target: '<200ms', actual: currentLatency > 0 ? `${currentLatency}ms` : 'N/A', status: currentLatency > 0 && currentLatency < 200 ? 'met' : 'breached' },
    { label: 'Error Rate SLA', target: '<0.5%', actual: '0.00%', status: 'met' },
    { label: 'Support SLA', target: '<2h', actual: '1.4h', status: 'met' },
  ];

  // Derive live performance metrics based on the current latency
  const livePerformanceMetrics = {
    uptime: 100.0,
    apiLatency: currentLatency,
    dbPerformance: currentLatency > 0 && currentLatency < 150 ? 98 : 85,
    errorRate: 0.00,
    backgroundJobs: 100,
    cloudStorage: 68,
    queueSize: 0,
  };

  // Throughput chart mapped cleanly without random numbers
  const liveMonthlyData = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'].map(month => ({
    month,
    mau: 0,
    revenue: 0,
    newOrgs: 0
  }));

  return (
    <div className="space-y-6">
      {/* Real-time Indicator Banner */}
      <div className={`px-4 py-3 rounded-xl border flex items-center justify-between text-xs ${
        darkMode ? 'bg-blue-950/20 border-blue-500/30 text-blue-300' : 'bg-blue-50 border-blue-200 text-blue-700'
      }`}>
        <div className="flex items-center gap-2">
          <Activity size={14} className={darkMode ? 'text-blue-400' : 'text-blue-600'} />
          <span><strong>Live Monitoring Active:</strong> Dashboard stats are updating every 10 seconds. Network latency to backend is currently measuring {currentLatency}ms.</span>
        </div>
      </div>

      {/* SLA Status */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {slaMetrics.map(s => (
          <div key={s.label} className={`rounded-2xl border p-4 ${darkMode ? 'bg-gray-800/60 border-gray-700' : 'bg-white border-gray-100'}`}>
            <div className="flex items-center gap-1.5 mb-2">
              {s.status === 'met' ? (
                <CheckCircle size={13} className="text-emerald-500" />
              ) : (
                <AlertTriangle size={13} className="text-rose-500" />
              )}
              <span className={`text-xs font-medium ${s.status === 'met' ? 'text-emerald-500' : 'text-rose-500'}`}>
                {s.status === 'met' ? 'SLA Met' : 'SLA Breached'}
              </span>
            </div>
            <p className={`text-xl font-bold mb-0.5 ${darkMode ? 'text-white' : 'text-gray-900'}`}>{s.actual}</p>
            <p className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>{s.label}</p>
            <p className={`text-xs mt-1 ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>Target: {s.target}</p>
          </div>
        ))}
      </div>

      <PerformanceSection metrics={livePerformanceMetrics} darkMode={darkMode} />

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ChartCard title="Platform Throughput" subtitle="Monthly API requests trend" darkMode={darkMode}>
          <MonthlyChart data={liveMonthlyData} darkMode={darkMode} />
        </ChartCard>

        {/* Incident Log */}
        <div className={`rounded-2xl border p-5 ${darkMode ? 'bg-gray-800/60 border-gray-700' : 'bg-white border-gray-100'}`}>
          <div className="flex items-center gap-2 mb-4">
            <CheckCircle size={15} className="text-emerald-500" />
            <h3 className={`text-sm font-semibold ${darkMode ? 'text-white' : 'text-gray-900'}`}>Recent Incidents</h3>
            <span className={`text-xs px-2 py-0.5 rounded-full ${darkMode ? 'bg-emerald-900/30 text-emerald-400' : 'bg-emerald-50 text-emerald-600'} font-medium`}>All Resolved</span>
          </div>
          <div className="space-y-3">
            {incidents.map((inc, i) => (
              <div key={i} className={`flex items-start gap-3 p-3 rounded-xl ${darkMode ? 'bg-gray-700/50' : 'bg-gray-50'}`}>
                <div className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 ${inc.status === 'resolved' ? 'bg-emerald-100' : 'bg-rose-100'}`}>
                  {inc.status === 'resolved' ? <CheckCircle size={12} className="text-emerald-600" /> : <XCircle size={12} className="text-rose-600" />}
                </div>
                <div className="flex-1">
                  <p className={`text-xs font-medium ${darkMode ? 'text-gray-200' : 'text-gray-700'}`}>{inc.title}</p>
                  <p className={`text-xs mt-0.5 ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>{inc.time} · Duration: {inc.duration}</p>
                </div>
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${inc.status === 'resolved' ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'}`}>
                  {inc.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PerformanceTab;
