import React from 'react';
import {
  ChartCard, DailyActiveChart, MonthlyChart, RetentionChart,
  PeakHoursChart, NewVsReturningChart, TopFeaturesChart, LoanTypeChart, ApplicationStatusChart,
} from '../Charts';
import LeadsTable from '../LeadsTable';
import TeamPerformanceSection from '../TeamPerformanceSection';
import { Lead } from '../../types';

interface UsersTabProps {
  leads: Lead[];
  stats: any;
  darkMode: boolean;
  loading: boolean;
}

// Helper to get start of day
const getStartOfDay = (date: Date) => new Date(date.getFullYear(), date.getMonth(), date.getDate());

const UsersTab: React.FC<UsersTabProps> = ({ leads, stats, darkMode, loading }) => {
  // Derive real counts from backend stats
  const totalLeads = stats?.leadsStats?.combined_total ?? leads.length;
  const classicLeads = stats?.leadsStats?.classic_leads?.total ?? 0;
  const externalLeads = stats?.leadsStats?.external_leads?.total ?? 0;
  const conversionRate = stats?.leadsStats?.external_leads?.conversion_rate_pct ?? 0;

  const userStats = [
    { label: 'Combined Leads', value: totalLeads.toLocaleString('en-IN'), color: '#0076eb', sub: 'All sourced leads' },
    { label: 'Classic Leads', value: classicLeads.toLocaleString('en-IN'), color: '#e5b83b', sub: 'Internal platform' },
    { label: 'External Leads', value: externalLeads.toLocaleString('en-IN'), color: '#3b82f6', sub: 'Fincome / Manipal' },
    { label: 'Conversion Rate', value: `${conversionRate}%`, color: '#10b981', sub: 'Disbursed / Total' },
  ];

  const byStatus = stats?.leadsStats?.classic_leads?.by_status ?? [];
  const bySource = stats?.leadsStats?.classic_leads?.by_source ?? [];

  // --- Dynamic Chart Data Generation from Live Leads --- //
  
  // 1. Daily Active (by day of week)
  const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const dailyCounts: Record<string, { users: number; newUsers: number }> = {};
  days.forEach(d => { dailyCounts[d] = { users: 0, newUsers: 0 }; });
  leads.forEach(lead => {
    const d = new Date(lead.created_at);
    const dayName = days[d.getDay()];
    dailyCounts[dayName].users += 1;
    if (lead.status === 'APPLICATION_CREATED' || lead.status === 'ACTIVE') dailyCounts[dayName].newUsers += 1;
  });
  const liveDailyActiveData = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map(day => ({
    day,
    users: dailyCounts[day].users || 0,
    sessions: dailyCounts[day].users || 0,
    newUsers: dailyCounts[day].newUsers
  }));

  // 2. Peak Hours
  const hours = ['6am', '8am', '10am', '12pm', '2pm', '4pm', '6pm', '8pm', '10pm'];
  const hourCounts: Record<string, number> = {};
  hours.forEach(h => { hourCounts[h] = 0; });
  leads.forEach(lead => {
    const hour = new Date(lead.created_at).getHours();
    let bucket = '12pm';
    if (hour >= 6 && hour < 8) bucket = '6am';
    else if (hour >= 8 && hour < 10) bucket = '8am';
    else if (hour >= 10 && hour < 12) bucket = '10am';
    else if (hour >= 12 && hour < 14) bucket = '12pm';
    else if (hour >= 14 && hour < 16) bucket = '2pm';
    else if (hour >= 16 && hour < 18) bucket = '4pm';
    else if (hour >= 18 && hour < 20) bucket = '6pm';
    else if (hour >= 20 && hour < 22) bucket = '8pm';
    else bucket = '10pm';
    hourCounts[bucket] += 1;
  });
  const livePeakHoursData = hours.map(hour => ({
    hour,
    users: hourCounts[hour] || 0
  }));

  // 3. Top Features (Mapped to Product Types / Subcategories in DB)
  const features = [
    { name: 'Gold Loan Processing', color: '#6366f1' },
    { name: 'Business / SME Loan', color: '#8b5cf6' },
    { name: 'Home Loan / LAP', color: '#3b82f6' },
    { name: 'Personal Loan', color: '#10b981' },
    { name: 'Digital Sourcing', color: '#f59e0b' },
  ];
  const liveTopFeaturesData = features.map((f) => ({
    feature: f.name,
    usage: leads.filter(l => (l.product_subcategory || '').toLowerCase().includes(f.name.toLowerCase().split(' ')[0])).length,
    color: f.color
  }));

  // 4. Monthly Trend
  const monthlyTrend = stats?.applicationsStats?.monthly_trend || [];
  const liveMonthlyData = monthlyTrend.length > 0
    ? monthlyTrend.map((m: any) => ({
        month: m.month,
        mau: Number(m.count) || 0,
        revenue: 0,
        newOrgs: Number(m.count) || 0
      }))
    : [];

  // 5. New vs Returning (Classic vs External)
  const leadsMonthly = stats?.leadsStats?.monthly_trend || [];
  const liveNewVsReturningData = leadsMonthly.length > 0 
    ? leadsMonthly.map((item: any) => ({
        month: item.month,
        new: externalLeads,
        returning: classicLeads
      }))
    : [{ month: 'Current', new: externalLeads, returning: classicLeads }];

  // 6. Retention Data (Active loan retention rate across portfolio)
  const activePct = totalLeads > 0 ? Math.round((stats?.loansStats?.active_loans || 0) / totalLeads * 100) : 0;
  const liveRetentionData = [
    { week: 'W1', rate: activePct > 0 ? 100 : 0 },
    { week: 'W2', rate: activePct },
    { week: 'W3', rate: activePct },
    { week: 'W4', rate: activePct },
    { week: 'W5', rate: activePct },
    { week: 'W6', rate: activePct },
  ];

  return (
    <div className="space-y-6">
      {/* User Stats — Real Backend Data */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {userStats.map(stat => (
          <div key={stat.label} className={`rounded-2xl border p-5 ${darkMode ? 'bg-gray-800/60 border-gray-700' : 'bg-white border-gray-100'}`}>
            <div className="flex items-center gap-2 mb-1">
              <div className="w-2 h-2 rounded-full" style={{ background: stat.color }} />
              <p className={`text-xs font-medium ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>{stat.label}</p>
            </div>
            <p className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>{stat.value}</p>
            <p className={`text-xs mt-1 ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>{stat.sub}</p>
          </div>
        ))}
      </div>

      {/* Team Performance Section */}
      <TeamPerformanceSection teamStats={stats?.teamStats} darkMode={darkMode} />

      {/* Lead Status & Source Breakdown */}
      {(byStatus.length > 0 || bySource.length > 0) && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {byStatus.length > 0 && (
            <div className={`rounded-2xl border p-5 ${darkMode ? 'bg-gray-800/60 border-gray-700' : 'bg-white border-gray-100'}`}>
              <h4 className={`text-sm font-semibold mb-4 ${darkMode ? 'text-white' : 'text-gray-900'}`}>Lead Status Distribution</h4>
              <div className="space-y-2.5">
                {byStatus.slice(0, 8).map((item: any, i: number) => {
                  const total = byStatus.reduce((s: number, d: any) => s + (d.count || 0), 0);
                  const pct = total > 0 ? Math.round((item.count / total) * 100) : 0;
                  const colors = ['#0076eb','#e5b83b','#3b82f6','#06b6d4','#10b981','#f59e0b','#ef4444','#ec4899'];
                  return (
                    <div key={i}>
                      <div className="flex items-center justify-between mb-1">
                        <span className={`text-xs font-medium truncate max-w-[60%] ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                          {item.status?.replace(/_/g, ' ') || 'Unknown'}
                        </span>
                        <span className={`text-xs font-bold ${darkMode ? 'text-gray-200' : 'text-gray-800'}`}>{item.count} ({pct}%)</span>
                      </div>
                      <div className={`h-2 rounded-full ${darkMode ? 'bg-gray-700' : 'bg-gray-100'} overflow-hidden`}>
                        <div
                          className="h-full rounded-full transition-all duration-700"
                          style={{ width: `${pct}%`, background: colors[i % colors.length] }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {bySource.length > 0 && (
            <div className={`rounded-2xl border p-5 ${darkMode ? 'bg-gray-800/60 border-gray-700' : 'bg-white border-gray-100'}`}>
              <h4 className={`text-sm font-semibold mb-4 ${darkMode ? 'text-white' : 'text-gray-900'}`}>Lead Source Breakdown</h4>
              <div className="space-y-2.5">
                {bySource.slice(0, 8).map((item: any, i: number) => {
                  const total = bySource.reduce((s: number, d: any) => s + (d.count || 0), 0);
                  const pct = total > 0 ? Math.round((item.count / total) * 100) : 0;
                  const colors = ['#10b981','#0076eb','#e5b83b','#3b82f6','#8b5cf6','#ef4444','#06b6d4','#ec4899'];
                  return (
                    <div key={i}>
                      <div className="flex items-center justify-between mb-1">
                        <span className={`text-xs font-medium truncate max-w-[60%] ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                          {item.source || 'Unknown'}
                        </span>
                        <span className={`text-xs font-bold ${darkMode ? 'text-gray-200' : 'text-gray-800'}`}>{item.count} ({pct}%)</span>
                      </div>
                      <div className={`h-2 rounded-full ${darkMode ? 'bg-gray-700' : 'bg-gray-100'} overflow-hidden`}>
                        <div
                          className="h-full rounded-full transition-all duration-700"
                          style={{ width: `${pct}%`, background: colors[i % colors.length] }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Application Status + Loan Type from Backend */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ChartCard title="Application Pipeline Status" subtitle="By processing stage" darkMode={darkMode}>
          <ApplicationStatusChart data={stats?.applicationsStats?.by_status || []} darkMode={darkMode} />
        </ChartCard>
        <ChartCard title="External Lead Loan Types" subtitle="From Fincome & Manipal sourcing" darkMode={darkMode}>
          <div className="pt-2">
            <LoanTypeChart data={stats?.leadsStats?.external_leads?.by_loan_type || []} darkMode={darkMode} />
          </div>
        </ChartCard>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ChartCard title="Daily Active Users" subtitle="Current week breakdown" darkMode={darkMode}>
          <DailyActiveChart data={liveDailyActiveData} darkMode={darkMode} />
        </ChartCard>
        <ChartCard title="Monthly Active Users" subtitle="Historical engagement trend" darkMode={darkMode}>
          <MonthlyChart data={liveMonthlyData} darkMode={darkMode} />
        </ChartCard>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <ChartCard title="Retention Cohort" subtitle="User survival curve" darkMode={darkMode}>
          <RetentionChart data={liveRetentionData} darkMode={darkMode} />
        </ChartCard>
        <ChartCard title="Peak Usage Hours" subtitle="Active users by time of day" darkMode={darkMode}>
          <PeakHoursChart data={livePeakHoursData} darkMode={darkMode} />
        </ChartCard>
        <ChartCard title="New vs Returning" subtitle="User acquisition vs engagement" darkMode={darkMode}>
          <NewVsReturningChart data={liveNewVsReturningData} darkMode={darkMode} />
        </ChartCard>
      </div>

      <ChartCard title="Top Features Used" subtitle="By user interaction count" darkMode={darkMode}>
        <div className="pt-2">
          <TopFeaturesChart data={liveTopFeaturesData} darkMode={darkMode} />
        </div>
      </ChartCard>

      <LeadsTable leads={leads} darkMode={darkMode} loading={loading} />
    </div>
  );
};

export default UsersTab;
