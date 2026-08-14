import React from 'react';
import { Server, Wifi, Database, AlertTriangle, Cpu, HardDrive, List } from 'lucide-react';

interface PerformanceSectionProps {
  metrics: {
    uptime: number;
    apiLatency: number;
    dbPerformance: number;
    errorRate: number;
    backgroundJobs: number;
    cloudStorage: number;
    queueSize: number;
  };
  darkMode: boolean;
}

interface GaugeProps {
  value: number;
  max: number;
  label: string;
  unit: string;
  color: string;
  icon: React.ReactNode;
  inverse?: boolean;
  darkMode: boolean;
}

const Gauge: React.FC<GaugeProps> = ({ value, max, label, unit, color, icon, inverse, darkMode }) => {
  const percent = Math.min((value / max) * 100, 100);
  const isGood = inverse ? percent < 20 : percent > 70;
  const statusColor = isGood ? 'text-emerald-500' : percent > 50 ? 'text-amber-500' : 'text-rose-500';

  return (
    <div className={`rounded-2xl p-4 border transition-all hover:shadow-md ${
      darkMode ? 'bg-gray-800/60 border-gray-700' : 'bg-white border-gray-100'
    }`}>
      <div className="flex items-center justify-between mb-3">
        <div className={`flex items-center gap-2 text-xs font-medium ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
          <span style={{ color }}>{icon}</span>
          {label}
        </div>
        <span className={`text-xs font-bold ${statusColor}`}>
          {value}{unit}
        </span>
      </div>
      <div className={`h-2 rounded-full ${darkMode ? 'bg-gray-700' : 'bg-gray-100'} overflow-hidden`}>
        <div
          className="h-full rounded-full transition-all duration-1000"
          style={{ width: `${percent}%`, background: `linear-gradient(90deg, ${color}, ${color}cc)` }}
        />
      </div>
      <div className="flex justify-between mt-1.5">
        <span className={`text-xs ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>0</span>
        <span className={`text-xs ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>{max}{unit}</span>
      </div>
    </div>
  );
};

const PerformanceSection: React.FC<PerformanceSectionProps> = ({ metrics, darkMode }) => {
  const gauges: GaugeProps[] = [
    { value: metrics.uptime, max: 100, label: 'Server Uptime', unit: '%', color: '#10b981', icon: <Server size={13} />, darkMode },
    { value: metrics.apiLatency, max: 500, label: 'API Latency', unit: 'ms', color: '#6366f1', icon: <Wifi size={13} />, inverse: true, darkMode },
    { value: metrics.dbPerformance, max: 100, label: 'DB Performance', unit: '%', color: '#8b5cf6', icon: <Database size={13} />, darkMode },
    { value: metrics.errorRate, max: 5, label: 'Error Rate', unit: '%', color: '#ef4444', icon: <AlertTriangle size={13} />, inverse: true, darkMode },
    { value: metrics.backgroundJobs, max: 100, label: 'Background Jobs', unit: '%', color: '#f59e0b', icon: <Cpu size={13} />, darkMode },
    { value: metrics.cloudStorage, max: 100, label: 'Cloud Storage', unit: '%', color: '#3b82f6', icon: <HardDrive size={13} />, darkMode },
  ];

  return (
    <div>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-4">
        {gauges.map((g) => (
          <Gauge key={g.label} {...g} />
        ))}
      </div>

      {/* Queue Size */}
      <div className={`rounded-2xl p-4 border flex items-center gap-4 ${darkMode ? 'bg-gray-800/60 border-gray-700' : 'bg-white border-gray-100'}`}>
        <div className="w-10 h-10 rounded-xl bg-violet-100 flex items-center justify-center">
          <List size={18} className="text-violet-600" />
        </div>
        <div className="flex-1">
          <div className="flex items-center justify-between mb-1">
            <span className={`text-sm font-medium ${darkMode ? 'text-gray-200' : 'text-gray-700'}`}>Job Queue Size</span>
            <span className={`text-sm font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>{metrics.queueSize} jobs</span>
          </div>
          <div className={`h-1.5 rounded-full ${darkMode ? 'bg-gray-700' : 'bg-gray-100'} overflow-hidden`}>
            <div className="h-full rounded-full bg-gradient-to-r from-violet-500 to-purple-500" style={{ width: `${Math.min((metrics.queueSize / 1000) * 100, 100)}%` }} />
          </div>
        </div>
        <div className={`text-xs px-2 py-1 rounded-lg ${metrics.queueSize < 500 ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'}`}>
          {metrics.queueSize < 500 ? 'Normal' : 'High'}
        </div>
      </div>
    </div>
  );
};

export default PerformanceSection;
