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
  
  // Specific detailed logging for our key synthetic dataset leads if they exist
  const keyLeads = leads.filter(l => ['Aarav Sharma', 'Priya Iyer', 'Rajesh Patil', 'Kavitha Reddy', 'Vikram Malhotra'].includes(l.name));
  const otherLeads = leads.filter(l => !['Aarav Sharma', 'Priya Iyer', 'Rajesh Patil', 'Kavitha Reddy', 'Vikram Malhotra'].includes(l.name));

  // 1. Aarav Sharma
  const aarav = keyLeads.find(l => l.name === 'Aarav Sharma');
  if (aarav) {
    events.push(
      { id: 'aarav-1', type: 'signin', user: 'Aarav Sharma', action: 'Lead sourced via MG Road Branch (Gold Loan)', time: '2025-01-10', category: 'Leads', avatar: 'AS' },
      { id: 'aarav-2', type: 'workspace', user: 'Aarav Sharma', action: 'Gold collateral appraised (4 Bangles, 47g adjusted weight)', time: '2025-01-10', category: 'Underwriting', avatar: 'AS' },
      { id: 'aarav-3', type: 'upgrade', user: 'Aarav Sharma', action: 'Loan LN-2025-1001 disbursed: ₹1,50,000 via NEFT', time: '2025-01-12', category: 'Disbursement', avatar: 'AS' },
      { id: 'aarav-4', type: 'ai', user: 'Aarav Sharma', action: 'Monthly EMI payment of ₹15,000 received via UPI', time: '2025-02-12', category: 'Repayments', avatar: 'AS' }
    );
  }

  // 2. Priya Iyer
  const priya = keyLeads.find(l => l.name === 'Priya Iyer');
  if (priya) {
    events.push(
      { id: 'priya-1', type: 'signin', user: 'Priya Iyer', action: 'Lead sourced via Digital App (Gold Loan)', time: '2025-01-12', category: 'Leads', avatar: 'PI' },
      { id: 'priya-2', type: 'workspace', user: 'Priya Iyer', action: 'Gold collateral appraised (1 Necklace, 93g adjusted weight)', time: '2025-01-12', category: 'Underwriting', avatar: 'PI' },
      { id: 'priya-3', type: 'upgrade', user: 'Priya Iyer', action: 'Loan LN-2025-1002 disbursed: ₹3,00,000 via RTGS', time: '2025-01-15', category: 'Disbursement', avatar: 'PI' },
      { id: 'priya-4', type: 'ai', user: 'Priya Iyer', action: 'Monthly EMI payment of ₹35,100 received via UPI', time: '2025-02-15', category: 'Repayments', avatar: 'PI' }
    );
  }

  // 3. Rajesh Patil
  const rajesh = keyLeads.find(l => l.name === 'Rajesh Patil');
  if (rajesh) {
    events.push(
      { id: 'rajesh-1', type: 'signin', user: 'Rajesh Patil', action: 'Lead sourced via Agent AGT-55 (Gold Loan)', time: '2025-01-15', category: 'Leads', avatar: 'RP' },
      { id: 'rajesh-2', type: 'workspace', user: 'Rajesh Patil', action: 'Gold collateral appraised (2 Rings, 23.5g adjusted weight)', time: '2025-01-15', category: 'Underwriting', avatar: 'RP' },
      { id: 'rajesh-3', type: 'upgrade', user: 'Rajesh Patil', action: 'Loan LN-2025-1003 disbursed: ₹75,000 via IMPS', time: '2025-01-18', category: 'Disbursement', avatar: 'RP' },
      { id: 'rajesh-4', type: 'ai', user: 'Rajesh Patil', action: 'Full Loan Foreclosure settlement: ₹80,250 received via NEFT', time: '2025-02-28', category: 'Repayments', avatar: 'RP' },
      { id: 'rajesh-5', type: 'report', user: 'Rajesh Patil', action: 'Loan LN-2025-1003 marked as CLOSED (Obligations Met)', time: '2025-02-28', category: 'Disbursement', avatar: 'RP' }
    );
  }

  // 4. Kavitha Reddy
  const kavitha = keyLeads.find(l => l.name === 'Kavitha Reddy');
  if (kavitha) {
    events.push(
      { id: 'kavitha-1', type: 'signin', user: 'Kavitha Reddy', action: 'Lead sourced via Partner CSC (Personal Loan)', time: '2025-01-20', category: 'Leads', avatar: 'KR' },
      { id: 'kavitha-2', type: 'report', user: 'Kavitha Reddy', action: 'Application APP-2025-004 declined: Low bureau score (520)', time: '2025-01-21', category: 'Underwriting', avatar: 'KR' }
    );
  }

  // 5. Vikram Malhotra
  const vikram = keyLeads.find(l => l.name === 'Vikram Malhotra');
  if (vikram) {
    events.push(
      { id: 'vikram-1', type: 'signin', user: 'Vikram Malhotra', action: 'Lead sourced via Web (Gold Loan)', time: '2025-02-01', category: 'Leads', avatar: 'VM' },
      { id: 'vikram-2', type: 'workspace', user: 'Vikram Malhotra', action: 'Gold collateral appraised (2 Chains, 147g adjusted weight)', time: '2025-02-01', category: 'Underwriting', avatar: 'VM' },
      { id: 'vikram-3', type: 'upgrade', user: 'Vikram Malhotra', action: 'Loan LN-2025-1005 disbursed: ₹5,00,000 via NEFT', time: '2025-02-05', category: 'Disbursement', avatar: 'VM' },
      { id: 'vikram-4', type: 'admin', user: 'Vikram Malhotra', action: 'Loan LN-2025-1005 marked as NPA (105 days past due)', time: '2025-03-01', category: 'NPA / Risk', avatar: 'VM' }
    );
  }

  // Process any other database leads dynamically
  otherLeads.forEach((lead) => {
    const initials = lead.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
    const dateStr = lead.created_at ? lead.created_at.split('T')[0] : 'Just now';
    
    events.push({
      id: `dynamic-${lead.id}-source`,
      type: 'signin',
      user: lead.name,
      action: `Lead sourced via ${lead.city || 'Digital'} (${lead.industry || 'Gold'})`,
      time: dateStr,
      category: 'Leads',
      avatar: initials,
    });

    if (lead.status === 'ACTIVE' || lead.status === 'Active') {
      events.push({
        id: `dynamic-${lead.id}-appraise`,
        type: 'workspace',
        user: lead.name,
        action: 'Gold purity and weight verified by Appraiser',
        time: dateStr,
        category: 'Underwriting',
        avatar: initials,
      });
      events.push({
        id: `dynamic-${lead.id}-disb`,
        type: 'upgrade',
        user: lead.name,
        action: `Loan disbursed: ₹${lead.revenue ? lead.revenue.toLocaleString('en-IN') : '1,00,000'} via NEFT`,
        time: dateStr,
        category: 'Disbursement',
        avatar: initials,
      });
    }
  });

  // Sort events by date (newest first)
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
      if (lead.status === 'Trial') counts[dayName].newUsers += 1;
    }
  });

  return ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map(day => ({
    day,
    users: counts[day].users || 1, // Fallback to 1 for visual rendering if empty
    sessions: (counts[day].users || 1) * 2,
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

  // Dummy peak hours data matching loan operations (e.g. branch walk-in peak at 11am-2pm)
  const peakHoursData = [
    { hour: '9am', users: 5 },
    { hour: '10am', users: 18 },
    { hour: '11am', users: 35 },
    { hour: '12pm', users: 48 },
    { hour: '1pm', users: 28 },
    { hour: '2pm', users: 32 },
    { hour: '3pm', users: 44 },
    { hour: '4pm', users: 20 },
    { hour: '5pm', users: 8 },
  ];

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
