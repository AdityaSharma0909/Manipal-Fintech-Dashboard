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
    users: counts[day].users || 1,
    newUsers: counts[day].newUsers,
  }));
};

const AnalyticsTab: React.FC<AnalyticsTabProps> = ({ leads, stats, darkMode }) => {
  const dailyActiveData = buildDailyActiveData(leads);

  // Map branch conversions dynamically to fit RegionCards format
  const branchCardsData = (stats?.teamStats?.conversions_per_branch || []).map((branch: any) => {
    return {
      name: branch.branch_name,
      users: branch.total_applications, // total apps punched
      growth: branch.conversion_rate_pct, // conversion rate
      revenue: branch.disbursed * 150000, // estimated disbursed amount for rendering (e.g. ₹1.5L per loan)
      health: branch.conversion_rate_pct >= 50 ? 92 : 72,
      trend: [12, 18, 30, 48, 55, branch.conversion_rate_pct || 10],
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

  // Repayment Collection Efficiency Trend (Mocked realistically)
  const collectionTrendData = [
    { week: 'W1', rate: 96.4 },
    { week: 'W2', rate: 97.8 },
    { week: 'W3', rate: 95.2 },
    { week: 'W4', rate: 98.1 },
  ];

  // Appraisal peak hours
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
