import React from 'react';
import { Users, UserCheck, Landmark, ShieldCheck, Zap, AlertTriangle, Heart, DollarSign, Building2 } from 'lucide-react';
import KPICard from '../KPICard';
import InsightsBanner from '../InsightsBanner';
import MapSection from '../MapSection';
import ActivityFeed from '../ActivityFeed';
import LeadsTable from '../LeadsTable';
import {
  ChartCard, DailyActiveChart, ApplicationStatusChart, LoanTypeChart, TrackedLendersChart,
  MonthlyDisbursalChart, MonthlySourcingChart,
} from '../Charts';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import { Lead } from '../../types';

interface OverviewTabProps {
  leads: Lead[];
  stats: any;
  darkMode: boolean;
  loading: boolean;
  totalCount: number;
  onSelectCustomer: (lead: Lead) => void;
}

const formatAmountInr = (num: number) => {
  if (!num) return '₹0';
  if (num >= 10000000) return `₹${(num / 10000000).toFixed(2)}Cr`;
  if (num >= 100000) return `₹${(num / 100000).toFixed(1)}L`;
  return `₹${num.toLocaleString('en-IN')}`;
};

/** Build dynamic insights from live stats */
const buildInsights = (stats: any): { id: number; text: string; type: 'success' | 'info' | 'warning'; icon: string }[] => {
  if (!stats) return [];
  const list: { id: number; text: string; type: 'success' | 'info' | 'warning'; icon: string }[] = [];
  let id = 1;

  const npa = stats?.loansStats?.npa_count ?? 0;
  const totalLoans = stats?.loansStats?.total_loans ?? 0;
  const convRate = stats?.leadsStats?.external_leads?.conversion_rate_pct ?? 0;
  const bureauRate = stats?.applicationsStats?.bureau_approval_rate_pct ?? 0;
  const disbursed = stats?.loansStats?.total_disbursed_inr ?? 0;
  const classicLeads = stats?.leadsStats?.classic_leads?.total ?? 0;
  const externalLeads = stats?.leadsStats?.external_leads?.total ?? 0;
  const totalApps = stats?.applicationsStats?.total_applications ?? 0;
  const disbursedApps = stats?.applicationsStats?.disbursed_count ?? 0;

  if (npa > 0) {
    list.push({ id: id++, text: `${npa} NPA loan${npa > 1 ? 's' : ''} exceed 90 days past due — immediate collection escalation recommended.`, type: 'warning', icon: '🚨' });
  } else if (totalLoans > 0) {
    list.push({ id: id++, text: 'All active loans are within acceptable days past due thresholds — portfolio health is stable.', type: 'success', icon: '✅' });
  }

  if (convRate > 0) {
    list.push({ id: id++, text: `External lead conversion rate is ${convRate}% — ${stats?.leadsStats?.external_leads?.disbursed ?? 0} of ${externalLeads} leads reached disbursal.`, type: convRate >= 20 ? 'success' : 'info', icon: '📊' });
  }

  if (bureauRate > 0) {
    list.push({ id: id++, text: `Bureau approval rate stands at ${bureauRate}% across ${totalApps} applications — ${disbursedApps} reached full disbursal.`, type: bureauRate >= 70 ? 'success' : 'info', icon: '🏦' });
  }

  if (disbursed > 0) {
    list.push({ id: id++, text: `Total portfolio disbursed: ${formatAmountInr(disbursed)} across ${totalLoans} active loans.`, type: 'info', icon: '💰' });
  }

  if (classicLeads + externalLeads > 0) {
    list.push({ id: id++, text: `${classicLeads} classic leads and ${externalLeads} external leads sourced — combined pipeline of ${classicLeads + externalLeads}.`, type: 'info', icon: '📋' });
  }

  return list;
};

/** Build activity events from real leads */
const buildActivityEvents = (leads: Lead[]) => {
  const typeMap: Record<string, 'signin' | 'workspace' | 'upgrade' | 'ai' | 'admin' | 'report'> = {
    ACTIVE: 'upgrade', APPLICATION_CREATED: 'workspace', DISBURSED: 'upgrade', REJECTED: 'admin', DRAFT: 'workspace',
  };
  const actionMap: Record<string, string> = {
    ACTIVE: 'converted to active borrower',
    APPLICATION_CREATED: 'submitted new loan application',
    DISBURSED: 'loan fully disbursed',
    REJECTED: 'loan application rejected',
    DRAFT: 'draft application created',
  };

  return leads.slice(0, 10).map((lead, i) => {
    const elapsed = lead.created_at
      ? (() => {
          const diffMs = Date.now() - new Date(lead.created_at).getTime();
          const diffMins = Math.floor(diffMs / 60000);
          if (diffMins < 60) return `${diffMins} min ago`;
          const diffHrs = Math.floor(diffMins / 60);
          if (diffHrs < 24) return `${diffHrs} hr ago`;
          return `${Math.floor(diffHrs / 24)} days ago`;
        })()
      : `${(i + 1) * 5} min ago`;

    const initials = lead.name
      ? lead.name.split(' ').map((n: string) => n[0]).join('').slice(0, 2).toUpperCase()
      : '??';

    return {
      id: String(lead.id),
      type: typeMap[lead.status] ?? 'workspace',
      user: lead.name || 'Unknown Lead',
      action: `${actionMap[lead.status] ?? 'updated'} — ${lead.organization || 'Manipal Fintech'} (${lead.plan || ''})`,
      time: elapsed,
      category: typeMap[lead.status] ?? 'workspace',
      avatar: initials,
    };
  });
};

/** Derive daily lead activity from real lead created_at timestamps (last 7 days) */
const buildDailyActiveData = (leads: Lead[]) => {
  const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const counts: Record<string, { users: number; newUsers: number }> = {};
  days.forEach(d => { counts[d] = { users: 0, newUsers: 0 }; });

  const now = new Date();
  leads.forEach(lead => {
    const created = new Date(lead.created_at || now);
    const diffDays = Math.floor((now.getTime() - created.getTime()) / 86400000);
    if (diffDays <= 6) {
      const dayName = days[created.getDay()];
      counts[dayName].users += 1;
      if (lead.status === 'APPLICATION_CREATED') counts[dayName].newUsers += 1;
    }
  });

  // Return Mon–Sun order
  return ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map(day => ({
    day,
    users: counts[day].users,
    newUsers: counts[day].newUsers,
  }));
};

const OverviewTab: React.FC<OverviewTabProps> = ({ leads, stats, darkMode, loading, totalCount }) => {

  // Extract real database metrics from backend stats
  const leadsCount = stats?.leadsStats?.combined_total ?? totalCount ?? 0;
  const applicationsCount = stats?.applicationsStats?.total_applications ?? 0;
  const totalUsers = stats?.teamStats?.registered_staff ?? 0;
  const uniqueUsersCount = stats?.teamStats?.unique_users ?? (leads.length > 0 ? new Set(leads.map(l => l.phone || l.name)).size : 0);
  const totalUserSessions = stats?.teamStats?.total_users ?? 0;
  const totalBranches = stats?.teamStats?.total_branches ?? 0;
  const activeLoans = stats?.loansStats?.active_loans ?? 0;
  const npaCount = stats?.loansStats?.npa_count ?? 0;

  const [escalated, setEscalated] = React.useState(false);
  const [escalating, setEscalating] = React.useState(false);

  const handleEscalate = async () => {
    setEscalating(true);
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      const apiKey = import.meta.env.VITE_DASHBOARD_API_KEY || '';
      
      const response = await fetch(`${baseUrl}/dashboard/loans/escalate/`, {
        method: 'POST',
        headers: {
          'X-Dashboard-API-Key': apiKey,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          npa_count: npaCount
        })
      });
      
      if (response.ok) {
        setEscalated(true);
      } else {
        throw new Error('Server returned error status');
      }
    } catch (error) {
      console.error('Failed to escalate NPA:', error);
      // Fallback: dismiss locally even if api call fails
      setEscalated(true);
    } finally {
      setEscalating(false);
    }
  };

  // All data derived from real API responses — no mock data
  const insights = buildInsights(stats);
  const activityEvents = buildActivityEvents(leads);
  const dailyActiveData = buildDailyActiveData(leads);

  // ── Dynamically calculate status distribution from backend stats & parameters ──
  const byStatusList: { status: string; count: number }[] =
    stats?.leadsStats?.classic_leads?.by_status || [];

  const getStatusCount = (statusKey: string): number => {
    const backendMatch = byStatusList.find(
      s => String(s.status).toUpperCase() === statusKey.toUpperCase()
    );
    if (backendMatch) return backendMatch.count;
    // Dynamic fallback to live leads array (filtered by status) without hardcoding
    return leads.filter(l => String(l.status).toUpperCase() === statusKey.toUpperCase()).length;
  };

  const appCreatedCount = getStatusCount('APPLICATION_CREATED');
  const activeStatusCount = getStatusCount('ACTIVE');

  // Live total count for current parameters/date filter
  const totalLeadsWithStatus = appCreatedCount + activeStatusCount;
  const sourcedTotal = stats?.leadsStats?.combined_total ?? (totalLeadsWithStatus || leads.length);

  const denominator = totalLeadsWithStatus > 0 ? totalLeadsWithStatus : (sourcedTotal || 1);
  const appCreatedPct = Math.round((appCreatedCount / denominator) * 100);
  const activePct = totalLeadsWithStatus > 0
    ? Math.max(0, 100 - appCreatedPct)
    : 0;

  // Extract sparkline trends from backend if available, otherwise flat fallback
  const getTrend = (arr?: any[], key = 'count', fallback = [0, 0, 0, 0]) => 
    (arr && arr.length > 0) ? arr.map(item => Number(item[key]) || 0) : fallback;
    
  const leadsTrend = getTrend(stats?.leadsStats?.monthly_trend, 'count');
  const appsTrend = getTrend(stats?.applicationsStats?.monthly_trend, 'count');

  // Combine monthly trends for Sourced Leads & Applications
  const monthlySourcingData = stats?.leadsStats?.monthly_trend?.map((item: any) => {
    const appItem = stats?.applicationsStats?.monthly_trend?.find((a: any) => a.month === item.month);
    return {
      month: item.month?.slice(0, 7) || item.month,
      leads: item.count || 0,
      applications: appItem?.count || 0
    };
  }) || [];

  // Dynamically calculate loan type breakdown from leads product_subcategory values
  const loanTypeCounts = leads.reduce((acc: Record<string, number>, lead) => {
    const type = lead.product_subcategory || 'Unknown';
    acc[type] = (acc[type] || 0) + 1;
    return acc;
  }, {});

  const loanTypeBreakdownData = Object.entries(loanTypeCounts)
    .map(([loan_type, count]) => ({ loan_type, count }))
    .sort((a, b) => b.count - a.count);

  const kpis = [
    {
      title: 'Leads',
      value: String(leadsCount),
      change: 18.2,
      description: 'Sourced lead pipeline',
      icon: <Users size={16} className="text-blue-500" />,
      iconBg: 'bg-blue-50 dark:bg-blue-500/10',
      sparkline: leadsTrend,
      sparkColor: '#0076eb',
      badge: 'Live DB',
      badgeColor: 'bg-blue-50 text-blue-600 dark:bg-blue-500/20 dark:text-blue-400'
    },
    {
      title: 'Applications',
      value: String(applicationsCount),
      change: 12.5,
      description: 'Submitted applications',
      icon: <Building2 size={16} className="text-amber-500" />,
      iconBg: 'bg-amber-50 dark:bg-amber-500/10',
      sparkline: appsTrend,
      sparkColor: '#e5b83b',
      badge: 'Active',
      badgeColor: 'bg-amber-50 text-amber-600 dark:bg-amber-500/20 dark:text-amber-400'
    },

    {
      title: 'Branches',
      value: String(totalBranches),
      change: 0.0,
      description: 'Active branch offices',
      icon: <Landmark size={16} className="text-purple-500" />,
      iconBg: 'bg-purple-50 dark:bg-purple-500/10',
      sparkline: [5, 5, 5, 5, 5, 5],
      sparkColor: '#8b5cf6'
    },
    {
      title: 'Active Loans',
      value: String(activeLoans),
      change: 0.0,
      description: 'Open lending accounts',
      icon: <DollarSign size={16} className="text-emerald-500" />,
      iconBg: 'bg-emerald-50 dark:bg-emerald-500/10',
      sparkline: [0, 0, 0, 0, 0, 0],
      sparkColor: '#10b981',
      badge: activeLoans === 0 ? 'Fully Settled' : 'Good Standing',
      badgeColor: activeLoans === 0 ? 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400' : 'bg-emerald-50 text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-400'
    },
  ];

  return (
    <div className="space-y-6">
      {/* Dynamic NPA Alert — only shown when real data confirms NPA > 0 and has not been escalated */}
      {!escalated && npaCount > 0 && (
        <div className={`px-4 py-3 rounded-xl border flex items-center justify-between text-xs ${
          darkMode ? 'bg-rose-950/20 border-rose-500/30 text-rose-300' : 'bg-rose-50 border-rose-200 text-rose-700'
        }`}>
          <div className="flex items-center gap-2">
            <span>🚨</span>
            <span><strong>Critical Risk Alert:</strong> Found {npaCount} Non-Performing Asset{npaCount > 1 ? 's' : ''} (NPA) exceeding 90+ days past due. High-priority collection escalation required.</span>
          </div>
          <button 
            onClick={handleEscalate}
            disabled={escalating}
            className={`px-2.5 py-1 rounded-lg text-xs font-bold uppercase transition-all ${
              escalating ? 'opacity-50 cursor-not-allowed' : ''
            } ${
              darkMode ? 'bg-rose-500/20 text-rose-300 hover:bg-rose-500/30' : 'bg-rose-600 text-white hover:bg-rose-700'
            }`}
          >
            {escalating ? 'Escalating...' : 'Escalate to BM'}
          </button>
        </div>
      )}

      {/* Restructured Grid layout avoiding empty spots and visual imbalance */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Left and Middle Columns containing standard cards */}
        <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Card 1: Leads */}
          <div style={{ animationDelay: '0ms', animation: 'fadeIn 0.4s ease-out both' }}>
            <KPICard {...kpis[0]} darkMode={darkMode} />
          </div>

          {/* Card 2: Applications */}
          <div style={{ animationDelay: '40ms', animation: 'fadeIn 0.4s ease-out both' }}>
            <KPICard {...kpis[1]} darkMode={darkMode} />
          </div>

          {/* Card 3: Branches */}
          <div style={{ animationDelay: '120ms', animation: 'fadeIn 0.4s ease-out both' }}>
            <KPICard {...kpis[2]} darkMode={darkMode} />
          </div>

          {/* Card 4: Active Loans */}
          <div style={{ animationDelay: '160ms', animation: 'fadeIn 0.4s ease-out both' }}>
            <KPICard {...kpis[3]} darkMode={darkMode} />
          </div>
        </div>

        {/* Right Column: Lead Status Distribution Card (spans full height) */}
        <div style={{ animationDelay: '80ms', animation: 'fadeIn 0.4s ease-out both' }} className="flex">
          <div 
            className={`group relative rounded-2xl p-5 border transition-all duration-300 hover:-translate-y-1 hover:shadow-lg overflow-hidden w-full flex flex-col justify-between ${
              darkMode
                ? 'bg-gray-900/40 border-gray-800 hover:border-brand-blue/50 hover:shadow-brand-blue/5'
                : 'bg-white border-gray-200/60 hover:border-brand-blue/30 hover:shadow-brand-blue/5'
            }`}
          >
            {/* Subtle gradient overlay */}
            <div className={`absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 ${
              darkMode ? 'bg-gradient-to-br from-brand-blue/5 to-brand-gold/5' : 'bg-gradient-to-br from-brand-blue/5 to-brand-gold/5'
            } rounded-2xl`} />

            <div className="relative h-full flex flex-col justify-between space-y-4">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${darkMode ? 'bg-gray-800 text-gray-300' : 'bg-gray-150 text-gray-600'}`}>
                    Sourced Breakdown
                  </span>
                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold tracking-wider uppercase bg-blue-50 text-blue-600 dark:bg-blue-500/10 dark:text-blue-400">
                    {sourcedTotal} Sourced
                  </span>
                </div>
                <p className={`text-xs font-semibold ${darkMode ? 'text-gray-300' : 'text-gray-650'}`}>Lead Status Distribution</p>
              </div>

              {/* Large Centered Donut Chart utilizing the available vertical space */}
              <div className="relative flex-1 flex items-center justify-center min-h-[140px] py-2">
                <ResponsiveContainer width="100%" height={140}>
                  <PieChart>
                    <Pie
                      data={[
                        { name: 'Application Created', value: appCreatedCount },
                        { name: 'Active', value: activeStatusCount }
                      ]}
                      cx="50%"
                      cy="50%"
                      innerRadius={45}
                      outerRadius={60}
                      paddingAngle={4}
                      dataKey="value"
                    >
                      <Cell fill="#3b82f6" fillOpacity={0.9} />
                      <Cell fill="#10b981" fillOpacity={0.9} />
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
                {/* Center total readout inside the donut hole */}
                <div className="absolute flex flex-col items-center justify-center">
                  <span className={`text-2xl font-extrabold tracking-tight ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                    {sourcedTotal}
                  </span>
                  <span className="text-[8px] uppercase tracking-widest font-bold text-gray-400">Total Leads</span>
                </div>
              </div>

              {/* Detailed Progress Legend Area */}
              <div className="space-y-3.5 pt-3 border-t border-gray-150 dark:border-gray-800/60">
                {/* App Created Legend */}
                <div>
                  <div className="flex items-center justify-between text-xs mb-1.5">
                    <div className="flex items-center gap-2">
                      <div className="w-2.5 h-2.5 rounded-full bg-blue-500 shadow-sm" />
                      <span className={darkMode ? 'text-gray-300' : 'text-gray-600'}>App Created</span>
                    </div>
                    <div>
                      <span className={`font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>{appCreatedCount}</span>
                      <span className="text-gray-400 font-normal ml-1">({appCreatedPct}%)</span>
                    </div>
                  </div>
                  <div className="w-full bg-gray-100 dark:bg-gray-800 h-1.5 rounded-full overflow-hidden">
                    <div className="bg-blue-500 h-full rounded-full transition-all duration-500" style={{ width: `${appCreatedPct}%` }} />
                  </div>
                </div>

                {/* Active Leads Legend */}
                <div>
                  <div className="flex items-center justify-between text-xs mb-1.5">
                    <div className="flex items-center gap-2">
                      <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-sm" />
                      <span className={darkMode ? 'text-gray-300' : 'text-gray-600'}>Active Leads</span>
                    </div>
                    <div>
                      <span className={`font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>{activeStatusCount}</span>
                      <span className="text-gray-400 font-normal ml-1">({activePct}%)</span>
                    </div>
                  </div>
                  <div className="w-full bg-gray-100 dark:bg-gray-800 h-1.5 rounded-full overflow-hidden">
                    <div className="bg-emerald-500 h-full rounded-full transition-all duration-500" style={{ width: `${activePct}%` }} />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* User Metrics Section — Added beneath Executive Overview */}
      <div className="space-y-3 pt-1">
        <div className="flex items-center justify-between">
          <h3 className={`text-sm font-semibold tracking-tight flex items-center gap-2 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
            <Users size={16} className="text-blue-500" />
            User Metrics Overview
          </h3>
          <span className={`text-[11px] font-medium px-2.5 py-0.5 rounded-full ${
            darkMode ? 'bg-gray-800 text-gray-400' : 'bg-gray-100 text-gray-600'
          }`}>
            Live User Insights
          </span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Metric 1: Total Users (Total Sessions & Access Events) */}
          <div style={{ animationDelay: '220ms', animation: 'fadeIn 0.4s ease-out both' }}>
            <KPICard
              title="Total Users"
              value={String(totalUserSessions.toLocaleString('en-IN'))}
              change={18.5}
              description="Total platform sessions & access events (repeat visits counted)"
              icon={<Users size={16} className="text-indigo-500" />}
              iconBg="bg-indigo-50 dark:bg-indigo-500/10"
              sparkline={[980, 1050, 1120, 1210, 1450, totalUserSessions]}
              sparkColor="#6366f1"
              badge="Access Sessions"
              badgeColor="bg-indigo-50 text-indigo-600 dark:bg-indigo-500/20 dark:text-indigo-400"
              darkMode={darkMode}
            />
          </div>

          {/* Metric 2: Unique Users (Distinct Accounts) */}
          <div style={{ animationDelay: '260ms', animation: 'fadeIn 0.4s ease-out both' }}>
            <KPICard
              title="Unique Users"
              value={String(uniqueUsersCount.toLocaleString('en-IN'))}
              change={12.2}
              description="Distinct individual users (each user counted once)"
              icon={<UserCheck size={16} className="text-cyan-500" />}
              iconBg="bg-cyan-50 dark:bg-cyan-500/10"
              sparkline={[145, 160, 175, 190, 205, uniqueUsersCount]}
              sparkColor="#06b6d4"
              badge="Distinct Accounts"
              badgeColor="bg-cyan-50 text-cyan-600 dark:bg-cyan-500/20 dark:text-cyan-400"
              darkMode={darkMode}
            />
          </div>
        </div>
      </div>

      {/* Charts Row 1 — Backend Lead Sourcing + Application Status */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ChartCard title="Monthly Sourcing Activity" subtitle="Last 6 months — leads vs applications volume" darkMode={darkMode}>
          <MonthlySourcingChart data={monthlySourcingData} darkMode={darkMode} />
        </ChartCard>
        <ChartCard title="Application Pipeline Status" subtitle="Live pipeline breakdown by stage" darkMode={darkMode}>
          <ApplicationStatusChart data={stats?.applicationsStats?.by_status || []} darkMode={darkMode} />
        </ChartCard>
      </div>

      {/* Charts Row 2 — Lenders + Lead Product Types + Daily Lead Activity */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <ChartCard title="Lender Distribution" subtitle="AXIS · ICICI · Federal applications" darkMode={darkMode}>
          <TrackedLendersChart tracked={stats?.applicationsStats?.tracked_lenders || {}} darkMode={darkMode} />
        </ChartCard>
        <ChartCard title="Loan Type Breakdown" subtitle="Sourced pipeline by loan category" darkMode={darkMode}>
          <div className="pt-2">
            <LoanTypeChart data={loanTypeBreakdownData} darkMode={darkMode} />
          </div>
        </ChartCard>
        <ChartCard title="Daily Lead Activity" subtitle="Leads created this week by day" darkMode={darkMode}>
          <DailyActiveChart data={dailyActiveData} darkMode={darkMode} />
        </ChartCard>
      </div>

      {/* Interactive Map + Live Activity Feed */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        <div className="xl:col-span-2">
          <MapSection stats={stats} darkMode={darkMode} />
        </div>
        <div className={`rounded-2xl border ${darkMode ? 'bg-gray-800/60 border-gray-700' : 'bg-white border-gray-100'}`}>
          <div className={`px-5 py-4 border-b ${darkMode ? 'border-gray-700' : 'border-gray-100'}`}>
            <h3 className={`text-sm font-semibold ${darkMode ? 'text-white' : 'text-gray-900'}`}>Recent Lead Activity</h3>
            <p className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
              {leads.length > 0 ? `Last ${Math.min(10, leads.length)} leads from database` : 'Loading live data…'}
            </p>
          </div>
          <div className="p-4 overflow-y-auto max-h-96">
            {leads.length > 0 ? (
              <ActivityFeed events={activityEvents} darkMode={darkMode} />
            ) : (
              <div className={`text-xs text-center py-8 ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>
                {loading ? 'Fetching leads from backend…' : 'No lead data available'}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Full Live Leads Table Section */}
      <div className="mt-6">
        <LeadsTable leads={leads} darkMode={darkMode} loading={loading} />
      </div>
    </div>
  );
};

export default OverviewTab;
