import React, { useState } from 'react';
import { Activity } from 'lucide-react';
import ActivityFeed from '../ActivityFeed';
import { ChartCard, DailyActiveChart, PeakHoursChart } from '../Charts';
import { Lead } from '../../types';

interface ActivityTabProps {
  leads: Lead[];
  stats: any;
  darkMode: boolean;
  loading: boolean;
}

const buildActivityTimeline = (leads: Lead[]) => {
  const events: any[] = [];

  leads.forEach((lead) => {
    const initials = lead.name ? lead.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2) : 'LD';
    const dateStr = lead.created_at ? lead.created_at.split('T')[0] : 'Just now';

    events.push({
      id: `lead-${lead.id}-source`,
      type: 'signin',
      user: lead.name || 'Lead',
      action: `Lead sourced via ${lead.city || 'Branch'} (${lead.product_subcategory || lead.industry || 'Gold Loan'})`,
      time: dateStr,
      category: 'Leads',
      avatar: initials,
    });

    if (lead.status === 'ACTIVE' || lead.status === 'CONVERTED' || lead.status === 'DISBURSED') {
      events.push({
        id: `lead-${lead.id}-disbursed`,
        type: 'upgrade',
        user: lead.name || 'Lead',
        action: `Loan disbursed: ₹${lead.revenue ? lead.revenue.toLocaleString('en-IN') : '0'} via NEFT`,
        time: dateStr,
        category: 'Disbursement',
        avatar: initials,
      });
    } else if (lead.status === 'REJECTED' || lead.status === 'CLOSED_LOST') {
      events.push({
        id: `lead-${lead.id}-declined`,
        type: 'admin',
        user: lead.name || 'Lead',
        action: `Application closed / declined`,
        time: dateStr,
        category: 'NPA / Risk',
        avatar: initials,
      });
    }
  });

  return events.sort((a, b) => new Date(b.time).getTime() - new Date(a.time).getTime()).slice(0, 15);
};

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
      if (lead.status === 'APPLICATION_CREATED' || lead.status === 'NEW') counts[dayName].newUsers += 1;
    }
  });

  return ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map(day => ({
    day,
    users: counts[day].users,
    sessions: counts[day].users,
    newUsers: counts[day].newUsers,
  }));
};

const ActivityTab: React.FC<ActivityTabProps> = ({ leads, stats, darkMode }) => {
  const [filterCategory, setFilterCategory] = useState('All');

  const categories = ['All', 'Leads', 'Underwriting', 'Disbursement', 'Repayments', 'NPA / Risk'];

  const timelineEvents = buildActivityTimeline(leads);
  const dailyActiveData = buildDailyActiveData(leads);

  const filtered = filterCategory === 'All'
    ? timelineEvents
    : timelineEvents.filter(e => e.category.toLowerCase() === filterCategory.toLowerCase());

  // Dynamic portfolio stats from real database metrics
  const leadsCount = stats?.leadsStats?.combined_total ?? leads.length ?? 0;
  const activeLoans = stats?.loansStats?.active_loans ?? 0;
  const avgLoanVal = stats?.loansStats?.avg_loan_amount_inr 
    ? `₹${(stats.loansStats.avg_loan_amount_inr / 100000).toFixed(1)}L` 
    : '₹0';
  const npaCount = stats?.loansStats?.npa_count ?? 0;

  const cardStats = [
    { label: 'Total Leads Sourced', value: String(leadsCount), color: 'text-indigo-500' },
    { label: 'Active Outstanding Loans', value: String(activeLoans), color: 'text-emerald-500' },
    { label: 'Avg Sourced Loan Amount', value: avgLoanVal, color: 'text-amber-500' },
    { label: 'NPA Accounts (90+ DPD)', value: String(npaCount), color: npaCount > 0 ? 'text-rose-500 font-extrabold animate-pulse' : 'text-gray-500' },
  ];

  // Peak appraisal hours derived from database lead creation hours
  const hourBuckets = ['9am', '10am', '11am', '12pm', '1pm', '2pm', '3pm', '4pm', '5pm'];
  const hourCountsMap: Record<string, number> = {};
  hourBuckets.forEach(h => { hourCountsMap[h] = 0; });
  leads.forEach(l => {
    const hr = new Date(l.created_at).getHours();
    let b = '12pm';
    if (hr >= 9 && hr < 10) b = '9am';
    else if (hr >= 10 && hr < 11) b = '10am';
    else if (hr >= 11 && hr < 12) b = '11am';
    else if (hr >= 12 && hr < 13) b = '12pm';
    else if (hr >= 13 && hr < 14) b = '1pm';
    else if (hr >= 14 && hr < 15) b = '2pm';
    else if (hr >= 15 && hr < 16) b = '3pm';
    else if (hr >= 16 && hr < 17) b = '4pm';
    else if (hr >= 17) b = '5pm';
    hourCountsMap[b] += 1;
  });
  const peakHoursData = hourBuckets.map(hour => ({ hour, users: hourCountsMap[hour] || 0 }));

  return (
    <div className="space-y-6">
      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {cardStats.map(s => (
          <div key={s.label} className={`rounded-2xl border p-4 ${darkMode ? 'bg-gray-800/60 border-gray-700' : 'bg-white border-gray-100'}`}>
            <p className={`text-2xl font-bold mb-1 ${s.color}`}>{s.value}</p>
            <p className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>{s.label}</p>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ChartCard title="Leads Ingress" subtitle="Leads sourced this week" darkMode={darkMode}>
          <DailyActiveChart data={dailyActiveData} darkMode={darkMode} />
        </ChartCard>
        <ChartCard title="Peak Appraisal Hours" subtitle="Appraiser valuations by hour of day" darkMode={darkMode}>
          <PeakHoursChart data={peakHoursData} darkMode={darkMode} />
        </ChartCard>
      </div>

      {/* Activity Feed */}
      <div className={`rounded-2xl border ${darkMode ? 'bg-gray-800/60 border-gray-700' : 'bg-white border-gray-100'}`}>
        <div className={`flex items-center justify-between px-5 py-4 border-b ${darkMode ? 'border-gray-700' : 'border-gray-100'} flex-wrap gap-4`}>
          <div className="flex items-center gap-2">
            <Activity size={15} className="text-indigo-500" />
            <h3 className={`text-sm font-semibold ${darkMode ? 'text-white' : 'text-gray-900'}`}>Gold Loan Portfolio Timeline</h3>
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            <div className="flex items-center gap-1 flex-wrap">
              {categories.map(cat => (
                <button
                  key={cat}
                  onClick={() => setFilterCategory(cat)}
                  className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-all ${
                    filterCategory === cat
                      ? 'bg-indigo-600 text-white'
                      : darkMode ? 'bg-gray-700 text-gray-300 hover:bg-gray-600' : 'bg-gray-100 text-gray-600 hover:bg-gray-250'
                  }`}
                >{cat}</button>
              ))}
            </div>
          </div>
        </div>
        <div className="p-4">
          <ActivityFeed events={filtered} darkMode={darkMode} />
        </div>
      </div>
    </div>
  );
};

export default ActivityTab;
