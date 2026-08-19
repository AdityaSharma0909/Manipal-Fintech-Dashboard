import React from 'react';
import { 
  ChartCard, DailyActiveChart, RetentionChart, PeakHoursChart,
  MonthlyDisbursalChart, ApplicationStatusChart, LoanTypeChart, 
  TrackedLendersChart, TopFeaturesChart 
} from '../Charts';
import RegionCards from '../RegionCards';
import { Lead } from '../../types';

interface AnalyticsTabProps {
  leads: Lead[];
  stats: any;
  darkMode: boolean;
  loading: boolean;
}

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

  return ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map(day => ({
    day,
    users: counts[day].users || 0,
    newUsers: counts[day].newUsers,
  }));
};

const AnalyticsTab: React.FC<AnalyticsTabProps> = ({ leads, stats, darkMode }) => {
  const dailyActiveData = buildDailyActiveData(leads);

  // Map branch conversions dynamically to fit RegionCards format
  const branchCardsData = (stats?.teamStats?.conversions_per_branch || []).map((branch: any) => {
    const rate = branch.conversion_rate_pct || 0;
    return {
      name: branch.branch_name,
      users: branch.total_applications || 0, // total apps punched
      growth: rate, // conversion rate
      revenue: (branch.disbursed || 0) * 100000, // estimated disbursed amount
      health: rate >= 50 ? 92 : (rate > 0 ? 70 : 0),
      trend: [0, 0, 0, 0, 0, rate],
    };
  });

  // Map loan type distribution dynamically to features bar chart
  const loanProductAdoption = (stats?.loansStats?.by_loan_type || []).map((lt: any, idx: number) => {
    const colors = ['#6366f1', '#e5b83b', '#10b981', '#ef4444', '#8b5cf6', '#3b82f6'];
    return {
      feature: lt.loan_type?.replace(/_/g, ' ') || 'Unknown',
      usage: lt.count || 0,
      color: colors[idx % colors.length],
    };
  });

  // Repayment Collection Efficiency Rate derived from active loans vs NPA count
  const totalLoansCount = stats?.loansStats?.total_loans || 0;
  const npaCount = stats?.loansStats?.npa_count || 0;
  const performingRate = totalLoansCount > 0 ? Math.round(((totalLoansCount - npaCount) / totalLoansCount) * 1000) / 10 : 0;

  const collectionTrendData = [
    { week: 'W1', rate: performingRate },
    { week: 'W2', rate: performingRate },
    { week: 'W3', rate: performingRate },
    { week: 'W4', rate: performingRate },
  ];

  // Appraisal peak hours calculated from lead creation timestamps
  const hourList = ['9am', '10am', '11am', '12pm', '1pm', '2pm', '3pm', '4pm', '5pm'];
  const hrCounts: Record<string, number> = {};
  hourList.forEach(h => { hrCounts[h] = 0; });
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
    hrCounts[b] += 1;
  });
  const peakHoursData = hourList.map(hour => ({ hour, users: hrCounts[hour] || 0 }));

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ChartCard title="Monthly Portfolio Disbursals" subtitle="Month-on-month volume in INR (Lakhs) & loan count" darkMode={darkMode}>
          <MonthlyDisbursalChart data={stats?.loansStats?.monthly_disbursals || []} darkMode={darkMode} />
        </ChartCard>
        <ChartCard title="Underwriting Pipeline Status" subtitle="Applications breakdown by stage" darkMode={darkMode}>
          <ApplicationStatusChart data={stats?.applicationsStats?.by_status || []} darkMode={darkMode} />
        </ChartCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ChartCard title="Daily Sourced Leads" subtitle="Weekly sourcing pattern" darkMode={darkMode}>
          <DailyActiveChart data={dailyActiveData} darkMode={darkMode} />
        </ChartCard>
        <ChartCard title="Lender Appraisals Distribution" subtitle="Punch counts across active co-lending banks" darkMode={darkMode}>
          <TrackedLendersChart tracked={stats?.applicationsStats?.tracked_lenders || {}} darkMode={darkMode} />
        </ChartCard>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <ChartCard title="Loan Portfolio Mix" subtitle="Accounts share" darkMode={darkMode}>
          <LoanTypeChart data={stats?.loansStats?.by_loan_type || []} darkMode={darkMode} />
        </ChartCard>
        <ChartCard title="Collection Efficiency" subtitle="Weekly repayment collection rate" darkMode={darkMode}>
          <RetentionChart data={collectionTrendData} darkMode={darkMode} />
        </ChartCard>
        <ChartCard title="Peak Gold Valuations" subtitle="Hourly appraisal activity" darkMode={darkMode}>
          <PeakHoursChart data={peakHoursData} darkMode={darkMode} />
        </ChartCard>
      </div>

      {loanProductAdoption.length > 0 && (
        <ChartCard title="Loan Product Adoption" subtitle="Total accounts opened per product" darkMode={darkMode}>
          <div className="pt-2">
            <TopFeaturesChart data={loanProductAdoption} darkMode={darkMode} />
          </div>
        </ChartCard>
      )}

      {branchCardsData.length > 0 && (
        <div>
          <h3 className={`text-sm font-semibold mb-3 ${darkMode ? 'text-white' : 'text-gray-900'}`}>Branch Performance Analytics</h3>
          <RegionCards regions={branchCardsData} darkMode={darkMode} />
        </div>
      )}
    </div>
  );
};

export default AnalyticsTab;
