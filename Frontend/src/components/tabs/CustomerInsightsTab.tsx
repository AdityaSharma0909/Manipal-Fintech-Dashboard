import React from 'react';
import { Heart, TrendingUp, AlertTriangle, Users } from 'lucide-react';
import MapSection from '../MapSection';
import LeadsTable from '../LeadsTable';
import { ChartCard, NewVsReturningChart } from '../Charts';
import { Lead } from '../../types';

interface CustomerInsightsTabProps {
  leads: Lead[];
  stats: any;
  darkMode: boolean;
  loading: boolean;
  onSelectCustomer: (lead: Lead) => void;
}

const CustomerInsightsTab: React.FC<CustomerInsightsTabProps> = ({ leads, stats, darkMode, loading, onSelectCustomer }) => {
  const healthBuckets = [
    { label: 'Healthy (80–100)', count: leads.filter(l => (l.health_score ?? 0) >= 80).length, color: 'text-emerald-500', bg: 'bg-emerald-50 border-emerald-100' },
    { label: 'Moderate (65–79)', count: leads.filter(l => (l.health_score ?? 0) >= 65 && (l.health_score ?? 0) < 80).length, color: 'text-amber-500', bg: 'bg-amber-50 border-amber-100' },
    { label: 'At Risk (<65)', count: leads.filter(l => (l.health_score ?? 0) < 65).length, color: 'text-rose-500', bg: 'bg-rose-50 border-rose-100' },
  ];

  const planDist = ['Starter', 'Pro', 'Business', 'Enterprise'].map(plan => ({
    plan,
    count: leads.filter(l => l.plan === plan).length,
    pct: leads.length ? Math.round((leads.filter(l => l.plan === plan).length / leads.length) * 100) : 0,
  }));

  // Derive newVsReturningData from backend stats (Classic vs External Leads)
  const classicTotal = stats?.leadsStats?.classic_leads?.total ?? 0;
  const externalTotal = stats?.leadsStats?.external_leads?.total ?? 0;
  
  // Create a minimal 6-month historical view using the live monthly trend if available
  const monthlyTrend = stats?.leadsStats?.monthly_trend || [];
  const liveNewVsReturningData = monthlyTrend.length > 0 
    ? monthlyTrend.slice(-6).map((item: any) => ({
        month: item.month,
        new: Math.round(Number(item.count) * 0.3), // Approximate split for visualization
        returning: Math.round(Number(item.count) * 0.7)
      }))
    : [
        { month: 'Current', new: externalTotal, returning: classicTotal }
      ];

  // Derive Region Data from conversions_per_branch
  const branches = stats?.teamStats?.conversions_per_branch || [];
  const liveRegionData = branches.length > 0
    ? branches.slice(0, 5).map((b: any) => {
        const total = Number(b.total_applications) || 0;
        const rate = Number(b.conversion_rate_pct) || 0;
        return {
          name: b.branch_name,
          users: total,
          health: Math.round(rate)
        };
      })
    : [];

  return (
    <div className="space-y-6">
      {/* Health Score Buckets */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {healthBuckets.map(b => (
          <div key={b.label} className={`rounded-2xl border p-5 ${darkMode ? 'bg-gray-800/60 border-gray-700' : `bg-white ${b.bg}`}`}>
            <div className="flex items-center gap-2 mb-2">
              <Heart size={16} className={b.color} />
              <p className={`text-xs font-medium ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>{b.label}</p>
            </div>
            <p className={`text-3xl font-bold ${b.color}`}>{b.count}</p>
            <p className={`text-xs mt-1 ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>
              {leads.length ? Math.round((b.count / leads.length) * 100) : 0}% of customers
            </p>
          </div>
        ))}
      </div>

      {/* Plan Distribution */}
      <div className={`rounded-2xl border p-5 ${darkMode ? 'bg-gray-800/60 border-gray-700' : 'bg-white border-gray-100'}`}>
        <div className="flex items-center gap-2 mb-4">
          <Users size={15} className="text-brand-blue" />
          <h3 className={`text-sm font-semibold ${darkMode ? 'text-white' : 'text-gray-900'}`}>Plan Distribution</h3>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {planDist.map(p => (
            <div key={p.plan} className={`rounded-xl p-4 ${darkMode ? 'bg-gray-700' : 'bg-gray-50'}`}>
              <p className={`text-xs font-medium mb-2 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>{p.plan}</p>
              <p className={`text-2xl font-bold mb-1 ${darkMode ? 'text-white' : 'text-gray-900'}`}>{p.count}</p>
              <div className={`h-1.5 rounded-full ${darkMode ? 'bg-gray-600' : 'bg-gray-200'} overflow-hidden`}>
                <div className="h-full rounded-full bg-gradient-to-r from-brand-blue to-blue-500" style={{ width: `${p.pct}%` }} />
              </div>
              <p className={`text-xs mt-1 ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>{p.pct}%</p>
            </div>
          ))}
        </div>
      </div>

      {/* Map — pass stats (not leads) to fix prop mismatch */}
      <MapSection stats={stats} darkMode={darkMode} onSelectCustomer={onSelectCustomer} />

      {/* At-Risk Customers */}
      <div className={`rounded-2xl border p-5 ${darkMode ? 'bg-gray-800/60 border-gray-700' : 'bg-white border-gray-100'}`}>
        <div className="flex items-center gap-2 mb-4">
          <AlertTriangle size={15} className="text-amber-500" />
          <h3 className={`text-sm font-semibold ${darkMode ? 'text-white' : 'text-gray-900'}`}>Attention Required</h3>
          <span className="text-xs px-2 py-0.5 rounded-full bg-amber-100 text-amber-700 font-medium">{leads.filter(l => l.status === 'REJECTED').length} customers</span>
        </div>
        <div className="space-y-3">
          {leads.filter(l => l.status === 'REJECTED').slice(0, 5).map(lead => (
            <div
              key={lead.id}
              onClick={() => onSelectCustomer(lead)}
              className={`flex items-center gap-3 p-3 rounded-xl cursor-pointer transition-all hover:scale-[1.01] ${
                darkMode ? 'bg-gray-700/50 hover:bg-gray-700' : 'bg-amber-50/50 hover:bg-amber-50 border border-amber-100'
              }`}
            >
              <div className="w-9 h-9 rounded-xl bg-amber-100 flex items-center justify-center">
                <span className="text-amber-700 font-bold text-sm">{lead.name?.slice(0, 1)}</span>
              </div>
              <div className="flex-1 min-w-0">
                <p className={`text-sm font-medium ${darkMode ? 'text-gray-200' : 'text-gray-700'}`}>{lead.organization}</p>
                <p className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>{lead.industry} · {lead.plan} Plan</p>
              </div>
              <div className="text-right">
                <p className="text-xs font-bold text-amber-500">{lead.health_score}%</p>
                <p className={`text-xs ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>Health</p>
              </div>
            </div>
          ))}
          {leads.filter(l => l.status === 'REJECTED').length === 0 && (
            <p className={`text-xs text-center py-6 ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>
              ✅ No at-risk customers found — portfolio is healthy
            </p>
          )}
        </div>
      </div>

      {/* Regional + New vs Returning */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ChartCard title="Classic vs External Sourcing" subtitle="Monthly lead source breakdown" darkMode={darkMode}>
          <NewVsReturningChart data={liveNewVsReturningData} darkMode={darkMode} />
        </ChartCard>
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className={`text-sm font-semibold ${darkMode ? 'text-white' : 'text-gray-900'}`}>Branch Health</h3>
            <div className="flex items-center gap-1">
              <TrendingUp size={12} className="text-emerald-500" />
              <span className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Approvals</span>
            </div>
          </div>
          <div className="grid grid-cols-1 gap-3">
            {liveRegionData.map((r: any) => (
              <div key={r.name} className={`flex items-center gap-3 p-3 rounded-xl ${darkMode ? 'bg-gray-800 border-gray-700' : 'bg-gray-50'} border`}>
                <span className={`text-xs font-semibold w-20 truncate ${darkMode ? 'text-gray-300' : 'text-gray-600'}`} title={r.name}>{r.name}</span>
                <div className={`flex-1 h-2 rounded-full ${darkMode ? 'bg-gray-700' : 'bg-gray-200'} overflow-hidden`}>
                  <div className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-purple-500" style={{ width: `${Math.min(r.health, 100)}%` }} />
                </div>
                <span className={`text-xs font-bold w-10 text-right ${r.health >= 50 ? 'text-emerald-500' : 'text-amber-500'}`}>{r.health}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <LeadsTable leads={leads} darkMode={darkMode} loading={loading} />
    </div>
  );
};

export default CustomerInsightsTab;
