import React from 'react';
import { X, ExternalLink, MessageSquare, Activity, Users, FolderOpen, Bot, HardDrive, DollarSign, Clock } from 'lucide-react';
import { Lead } from '../types';
import { ResponsiveContainer, AreaChart, Area } from 'recharts';

interface CustomerPanelProps {
  customer: Lead | null;
  onClose: () => void;
  darkMode: boolean;
}

const statusColors: Record<string, string> = {
  Active: 'bg-emerald-100 text-emerald-700',
  Trial: 'bg-blue-100 text-blue-700',
  'At Risk': 'bg-amber-100 text-amber-700',
  Churned: 'bg-rose-100 text-rose-700',
};

const CustomerPanel: React.FC<CustomerPanelProps> = ({ customer, onClose, darkMode }) => {
  if (!customer) return null;

  const trendData = Array.from({ length: 8 }, (_, i) => ({
    i,
    v: 50 + Math.sin(i * 0.8) * 20
  }));

  const stats = [
    { icon: <Users size={13} />, label: 'Users', value: customer.users?.toLocaleString() ?? '—' },
    { icon: <FolderOpen size={13} />, label: 'Projects', value: customer.projects ?? '—' },
    { icon: <Bot size={13} />, label: 'AI Requests', value: customer.ai_requests?.toLocaleString() ?? '—' },
    { icon: <HardDrive size={13} />, label: 'Storage', value: `${customer.storage ?? 0} GB` },
    { icon: <DollarSign size={13} />, label: 'Revenue', value: `₹${((customer.revenue ?? 0) / 1000).toFixed(1)}K` },
    { icon: <Activity size={13} />, label: 'Health Score', value: `${customer.health_score ?? 0}%` },
  ];

  return (
    <div className="fixed inset-y-0 right-0 z-50 flex">
      {/* Backdrop */}
      <div className="flex-1 bg-black/20 backdrop-blur-sm" onClick={onClose} />

      {/* Panel */}
      <div className={`w-80 h-full overflow-y-auto shadow-2xl border-l ${
        darkMode ? 'bg-gray-900 border-gray-700' : 'bg-white border-gray-200'
      }`}>
        {/* Header */}
        <div className={`sticky top-0 flex items-center justify-between p-4 border-b backdrop-blur-xl ${
          darkMode ? 'bg-gray-900/95 border-gray-700' : 'bg-white/95 border-gray-100'
        }`}>
          <span className={`text-sm font-semibold ${darkMode ? 'text-white' : 'text-gray-900'}`}>Customer Profile</span>
          <button onClick={onClose} className={`p-1.5 rounded-lg transition-all ${darkMode ? 'hover:bg-gray-800 text-gray-400' : 'hover:bg-gray-100 text-gray-400'}`}>
            <X size={15} />
          </button>
        </div>

        <div className="p-4 space-y-4">
          {/* Avatar + Name */}
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-brand-blue to-blue-500 flex items-center justify-center shadow-lg">
              <span className="text-white font-bold text-lg">{customer.name?.slice(0, 1) ?? '?'}</span>
            </div>
            <div>
              <p className={`font-semibold text-sm ${darkMode ? 'text-white' : 'text-gray-900'}`}>{customer.name}</p>
              <p className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>{customer.organization}</p>
              <span className={`text-xs px-2 py-0.5 rounded-full font-medium mt-1 inline-block ${statusColors[customer.status ?? ''] ?? 'bg-gray-100 text-gray-600'}`}>
                {customer.status}
              </span>
            </div>
          </div>

          {/* Details */}
          <div className={`rounded-xl p-3 space-y-2 ${darkMode ? 'bg-gray-800' : 'bg-gray-50'}`}>
            {[
              { label: 'Industry', value: customer.industry },
              { label: 'Plan', value: customer.plan },
              { label: 'Region', value: customer.region },
              { label: 'City', value: customer.city },
              { label: 'Email', value: customer.email },
            ].map(item => (
              <div key={item.label} className="flex items-center justify-between">
                <span className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>{item.label}</span>
                <span className={`text-xs font-medium ${darkMode ? 'text-gray-200' : 'text-gray-700'} max-w-[140px] truncate text-right`}>{item.value ?? '—'}</span>
              </div>
            ))}
            <div className="flex items-center justify-between">
              <span className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Last Active</span>
              <div className={`flex items-center gap-1 text-xs font-medium ${darkMode ? 'text-gray-200' : 'text-gray-700'}`}>
                <Clock size={10} />
                {customer.last_active ? new Date(customer.last_active).toLocaleDateString() : '—'}
              </div>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 gap-2">
            {stats.map(stat => (
              <div key={stat.label} className={`rounded-xl p-3 ${darkMode ? 'bg-gray-800' : 'bg-gray-50'}`}>
                <div className={`flex items-center gap-1 text-xs mb-1 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                  {stat.icon}
                  {stat.label}
                </div>
                <p className={`text-sm font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>{stat.value}</p>
              </div>
            ))}
          </div>

          {/* Health Score Bar */}
          <div className={`rounded-xl p-3 ${darkMode ? 'bg-gray-800' : 'bg-gray-50'}`}>
            <div className="flex items-center justify-between mb-2">
              <span className={`text-xs font-medium ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>Health Score</span>
              <span className={`text-sm font-bold ${
                (customer.health_score ?? 0) >= 80 ? 'text-emerald-500' :
                (customer.health_score ?? 0) >= 65 ? 'text-amber-500' : 'text-rose-500'
              }`}>{customer.health_score ?? 0}%</span>
            </div>
            <div className={`h-2 rounded-full ${darkMode ? 'bg-gray-700' : 'bg-gray-200'} overflow-hidden`}>
              <div
                className="h-full rounded-full transition-all"
                style={{
                  width: `${customer.health_score ?? 0}%`,
                  background: (customer.health_score ?? 0) >= 80 ? '#10b981' : (customer.health_score ?? 0) >= 65 ? '#f59e0b' : '#ef4444'
                }}
              />
            </div>
          </div>

          {/* Usage Trend */}
          <div className={`rounded-xl p-3 ${darkMode ? 'bg-gray-800' : 'bg-gray-50'}`}>
            <p className={`text-xs font-medium mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>Usage Trend (8 weeks)</p>
            <div className="h-16">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={trendData} margin={{ top: 2, right: 0, bottom: 2, left: 0 }}>
                  <defs>
                    <linearGradient id="cpTrend" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#0076eb" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#0076eb" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <Area type="monotone" dataKey="v" stroke="#0076eb" strokeWidth={2} fill="url(#cpTrend)" dot={false} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col gap-2">
            <button
              onClick={() => alert(`Opening full profile details for ${customer.name}...`)}
              className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-brand-blue hover:bg-brand-blue-hover text-white text-sm font-semibold shadow-md shadow-brand-blue/10 transition-all cursor-pointer"
            >
              <ExternalLink size={13} /> View Full Profile
            </button>
            <div className="flex gap-2">
              <button
                onClick={() => alert(`Opening workspace folder for ${customer.organization}...`)}
                className={`flex-1 flex items-center justify-center gap-1.5 py-2 rounded-xl text-xs font-medium border transition-all cursor-pointer ${
                  darkMode ? 'border-gray-700 text-gray-300 hover:bg-gray-800' : 'border-gray-200 text-gray-600 hover:bg-gray-50'
                }`}
              >
                <FolderOpen size={12} /> Workspace
              </button>
              <button
                onClick={() => {
                  if (customer.email) window.location.href = `mailto:${customer.email}`;
                  else alert(`Contacting ${customer.name}`);
                }}
                className={`flex-1 flex items-center justify-center gap-1.5 py-2 rounded-xl text-xs font-medium border transition-all cursor-pointer ${
                  darkMode ? 'border-gray-700 text-gray-300 hover:bg-gray-800' : 'border-gray-200 text-gray-600 hover:bg-gray-50'
                }`}
              >
                <MessageSquare size={12} /> Contact
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CustomerPanel;
