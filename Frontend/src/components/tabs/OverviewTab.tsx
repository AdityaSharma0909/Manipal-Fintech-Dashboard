import React, { useState } from 'react';
import KPICard from '../KPICard';
import InsightsBanner from '../InsightsBanner';
import MapSection from '../MapSection';
import LeadsTable from '../LeadsTable';
import {
  ChartCard,
  ConversionFunnelChart,
  TimeBasedTrendChart,
  SalesOfficerLeaderboardChart,
  ApplicationStatusColumnChart,
  ProductSubcategoryRankedList,
  LeadTypeDonutChart,
  ProductCategoryDonutGauge,
} from '../Charts';
import { Lead, ComprehensiveDashboardStats } from '../../types';
import { DateRangeOption } from '../../App';
import { exportExecutiveOverviewCSV } from '../../utils/exportOverview';
import { AlertTriangle, Activity, ArrowRight, Download, Check } from 'lucide-react';


interface OverviewTabProps {
  leads: Lead[];
  stats: ComprehensiveDashboardStats | any;
  darkMode: boolean;
  loading: boolean;
  totalCount: number;
  onSelectCustomer: (lead: Lead) => void;
  selectedRange?: DateRangeOption;
  customFromDate?: string;
  customToDate?: string;
}

const OverviewTab: React.FC<OverviewTabProps> = ({
  leads,
  stats,
  darkMode,
  loading,
  totalCount,
  onSelectCustomer,
  selectedRange = 'All Time',
  customFromDate,
  customToDate,
}) => {
  const [exportToast, setExportToast] = useState(false);

  const handleExportCSV = () => {
    exportExecutiveOverviewCSV(
      stats,
      selectedRange,
      customFromDate,
      customToDate,
      stats?.kpiTrends,
      stats?.attentionItems,
      stats?.whatChangedItems
    );
    setExportToast(true);
    setTimeout(() => setExportToast(false), 4000);
  };

  const ov = stats?.overview || {

    totalEmployees: stats?.employeesStats?.total || 0,
    activeEmployees: stats?.employeesStats?.active || 0,
    totalLeads: stats?.leadsStats?.total || leads.length || 0,
    totalApplications: stats?.applicationsStats?.total || 0,
    loginStats: null,
    conversionRatePct: stats?.overview?.conversionRatePct || 0,
    totalOnboardedPartners: stats?.overview?.totalOnboardedPartners || 0,
    approvedApplications: stats?.applicationsStats?.approvedCount || 0,
    disbursedApplications: stats?.applicationsStats?.disbursedCount || 0,
    totalApplicationAmount: 0,
    totalDisbursedAmount: 0,
  };

  const leadsMonthlyTrend = stats?.leadsStats?.monthlyTrend || [];
  const officerPerformance = stats?.employeesStats?.employeePerformance || [];

  // Verified Data Sets from Live API
  const appStatusDistribution = (stats?.applicationsStats?.byStatus || []).map((s: any) => ({
    name: s.status,
    count: s.count,
  }));

  const productCatDistribution = (stats?.leadsStats?.byProductCategory || []).map((c: any) => ({
    name: c.category,
    count: c.count,
  }));

  const productSubcatDistribution = (stats?.leadsStats?.byProductSubcategory || []).map((c: any) => ({
    name: c.subcategory,
    count: c.count,
  }));

  // 100% Real Live lead_type data from API
  const leadTypeDistribution = (stats?.leadsStats?.byLeadType || []).map((lt: any) => ({
    name: lt.leadType || lt.name,
    count: lt.count,
  }));

  // ── TimeStamp Login Stats (from /user/login-stats/ or live backend calculation) ──
  const loginStats = ov.loginStats || null;

  // Helper to safely extract login metrics for a time bucket
  const getLoginBucket = (bucket: string) => ({
    totalTimestampRecords: loginStats?.[bucket]?.total_timestamp_records ?? 0,
    totalLogins: loginStats?.[bucket]?.total_logins ?? 0,
    uniqueLogins: loginStats?.[bucket]?.unique_logins ?? 0,
  });

  // Dynamic calculations based on global date filter selection
  let displayTimestampRecords = 0;
  let timestampRecordsSubtext = '';
  let displayTotalLogins = 0;
  let totalLoginsSubtext = '';
  let displayUniqueUsers = 0;
  let uniqueUsersSubtext = '';
  let attendanceInsightText = '';

  if (selectedRange === 'Today') {
    const b = getLoginBucket('today');
    displayTimestampRecords = b.totalTimestampRecords;
    timestampRecordsSubtext = 'CHECKED_IN + CHECKED_OUT Today';
    displayTotalLogins = b.totalLogins;
    totalLoginsSubtext = 'CHECKED_IN records Today';
    displayUniqueUsers = b.uniqueLogins;
    uniqueUsersSubtext = `${b.totalLogins} logins out of ${b.totalTimestampRecords} total records`;
    attendanceInsightText = `Attendance Today: ${b.uniqueLogins} unique users logged in (${b.totalLogins} logins out of ${b.totalTimestampRecords} total records).`;
  } else if (selectedRange === 'This Week') {
    const b = getLoginBucket('this_week');
    displayTimestampRecords = b.totalTimestampRecords;
    timestampRecordsSubtext = 'CHECKED_IN + CHECKED_OUT This Week';
    displayTotalLogins = b.totalLogins;
    totalLoginsSubtext = 'CHECKED_IN records This Week';
    displayUniqueUsers = b.uniqueLogins;
    uniqueUsersSubtext = `${b.totalLogins} logins out of ${b.totalTimestampRecords} total records`;
    attendanceInsightText = `Attendance This Week: ${b.uniqueLogins} unique users logged in (${b.totalLogins} logins out of ${b.totalTimestampRecords} total records).`;
  } else if (selectedRange === 'This Month') {
    const b = getLoginBucket('this_month');
    const bToday = getLoginBucket('today');
    displayTimestampRecords = b.totalTimestampRecords;
    timestampRecordsSubtext = 'CHECKED_IN + CHECKED_OUT This Month';
    displayTotalLogins = b.totalLogins;
    totalLoginsSubtext = 'CHECKED_IN records This Month';
    displayUniqueUsers = b.uniqueLogins;
    uniqueUsersSubtext = `${b.totalLogins} logins out of ${b.totalTimestampRecords} total records`;
    attendanceInsightText = `Attendance This Month: ${b.uniqueLogins} unique users logged in (${b.totalLogins} logins out of ${b.totalTimestampRecords} total records, ${bToday.uniqueLogins} today).`;
  } else if (selectedRange === 'All Time') {
    const b = getLoginBucket('all_time');
    displayTimestampRecords = b.totalTimestampRecords;
    timestampRecordsSubtext = 'CHECKED_IN + CHECKED_OUT All Time';
    displayTotalLogins = b.totalLogins;
    totalLoginsSubtext = 'CHECKED_IN records All Time';
    displayUniqueUsers = b.uniqueLogins;
    uniqueUsersSubtext = `${b.totalLogins} logins out of ${b.totalTimestampRecords} total records`;
    attendanceInsightText = `Attendance All Time: ${b.uniqueLogins} unique users logged in (${b.totalLogins} logins out of ${b.totalTimestampRecords} total records).`;
  } else if (selectedRange === 'Custom') {
    const b = loginStats?.custom ?? getLoginBucket('all_time');
    displayTimestampRecords = b.totalTimestampRecords;
    timestampRecordsSubtext = 'CHECKED_IN + CHECKED_OUT (Custom Range)';
    displayTotalLogins = b.totalLogins;
    totalLoginsSubtext = 'CHECKED_IN records (Custom Range)';
    displayUniqueUsers = b.uniqueLogins;
    uniqueUsersSubtext = `${b.totalLogins} logins out of ${b.totalTimestampRecords} total records`;
    attendanceInsightText = `Attendance Custom Range: ${b.uniqueLogins} unique users logged in (${b.totalLogins} logins out of ${b.totalTimestampRecords} total records).`;
  }


  const insightsList = [
    {
      id: 1,
      title: 'Executive Overview',
      text: `Total leads logged: ${ov.totalLeads} across ${ov.totalOnboardedPartners} onboarded lending partners.`,
      type: 'success' as const,
      icon: '📊',
    },
    {
      id: 2,
      title: 'Conversion Funnel',
      text: `Applications originated: ${ov.totalApplications} with a ${ov.conversionRatePct}% conversion rate.`,
      type: 'info' as const,
      icon: '📈',
    },
    {
      id: 3,
      title: 'Attendance Metrics',
      text: attendanceInsightText || 'Live attendance metrics synced from database timestamp logs.',
      type: 'info' as const,
      icon: '👤',
    },
  ];

  return (
    <div className="space-y-6">
      {exportToast && (
        <div className="fixed bottom-6 right-6 z-50 flex items-center gap-2 bg-emerald-600 text-white px-4 py-2.5 rounded-xl shadow-2xl text-xs font-semibold animate-bounce">
          <Check size={14} />
          <span>✓ Executive Overview exported successfully.</span>
        </div>
      )}

      <InsightsBanner insights={insightsList} darkMode={darkMode} />

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Total Employees"
          value={ov.totalEmployees}
          description={`${ov.activeEmployees || ov.totalEmployees} active employees`}
          icon="Users"
          color="blue"
          apiEndpoint="/user/employee"
          darkMode={darkMode}
          delayMs={0}
          trend={stats?.kpiTrends?.totalEmployees}
        />

        <KPICard
          title="Total Leads"
          value={ov.totalLeads}
          description="Total onboarding leads logged"
          icon="FileText"
          color="indigo"
          apiEndpoint="/api/v2/onboarding/leads/list/"
          darkMode={darkMode}
          delayMs={100}
          trend={stats?.kpiTrends?.totalLeads}
        />

        <KPICard
          title="Total Applications"
          value={ov.totalApplications}
          description="Total onboarding applications"
          icon="FileText"
          color="cyan"
          apiEndpoint="/api/v2/onboarding/applications/list/"
          darkMode={darkMode}
          delayMs={200}
          trend={stats?.kpiTrends?.totalApps}
        />

        <KPICard
          title="Lead Conversion Rate"
          value={`${ov.conversionRatePct}%`}
          description="Lead to application conversion"
          icon="TrendingUp"
          color="purple"
          apiEndpoint="/api/v2/onboarding/leads/list/ & /applications/list/"
          darkMode={darkMode}
          delayMs={300}
          trend={stats?.kpiTrends?.conversionRate}
        />

        <KPICard
          title="Total Timestamp Records"
          value={displayTimestampRecords}
          description={timestampRecordsSubtext}
          icon="Clock"
          color="blue"
          apiEndpoint="TimeStamp / users_timestamp (CHECKED_IN + CHECKED_OUT)"
          darkMode={darkMode}
          delayMs={400}
          trend={stats?.kpiTrends?.timestampRecords}
        />

        <KPICard
          title="Total Logins"
          value={displayTotalLogins}
          description={totalLoginsSubtext}
          icon="LogIn"
          color="emerald"
          apiEndpoint="TimeStamp / users_timestamp (status = CHECKED_IN)"
          darkMode={darkMode}
          delayMs={500}
          trend={stats?.kpiTrends?.totalLogins}
        />

        <KPICard
          title="Unique Logged-in Users"
          value={displayUniqueUsers}
          description={uniqueUsersSubtext}
          icon="UserCheck"
          color="rose"
          apiEndpoint="TimeStamp / users_timestamp (status = CHECKED_IN user distinct)"
          darkMode={darkMode}
          delayMs={600}
          trend={stats?.kpiTrends?.uniqueUsers}
        />

        <KPICard
          title="Lending Partners"
          value={ov.totalOnboardedPartners}
          description={
            ov.totalOnboardedPartners > 0
              ? `${ov.totalOnboardedPartners} Unique Banks (${ov.partnerCategories?.goldLoan || 0} Gold Loan · ${ov.partnerCategories?.otherLoans || 0} Other Loans)`
              : 'Onboarded lending partners'
          }
          icon="Building2"
          color="amber"
          apiEndpoint="/api/v2/onboarding/lending-partners/ (bank_name)"
          darkMode={darkMode}
          delayMs={700}
          trend={stats?.kpiTrends?.partners}
        />
      </div>

      {/* ── Operational Features Row: What Changed? ── */}
      <div className="w-full">
        {/* Feature 5: What Changed? (Operational Movement) */}
        <div className={`rounded-2xl border p-5 ${darkMode ? 'bg-gray-900/70 border-gray-800' : 'bg-white border-gray-100 shadow-xs'}`}>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Activity size={16} className="text-brand-blue" />
              <h3 className={`text-xs font-bold uppercase tracking-wider ${darkMode ? 'text-gray-200' : 'text-gray-900'}`}>
                What Changed? (Operational Movement)
              </h3>
            </div>
            <span className={`text-[10px] font-mono opacity-60 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
              Live Period Metrics
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
            {(stats?.whatChangedItems || []).map((item: any, idx: number) => (
              <div
                key={idx}
                className={`flex flex-col justify-between p-3 rounded-xl border text-xs ${
                  darkMode ? 'bg-gray-800/50 border-gray-750' : 'bg-gray-50/80 border-gray-100'
                }`}
              >
                <span className={`font-medium mb-1 ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>{item.label}</span>
                <span className="font-extrabold text-sm text-brand-blue font-mono">{item.value}</span>
              </div>
            ))}
          </div>

          <p className={`text-[10px] mt-3 opacity-60 ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>
            Calculated strictly from live API record creation timestamps in selected date window.
          </p>
        </div>
      </div>


      {/* ── MIDDLE SECTION: Conversion Funnel & Top Sales Officers ─────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 1. Conversion Funnel (Leads -> Applications -> Approved -> Disbursed) */}

        <ChartCard
          title="Conversion Funnel Pipeline"
          subtitle="Leads → Applications → Approved → Disbursed"
          apiEndpoint="/api/v2/onboarding/leads/list/ & /applications/list/"
          darkMode={darkMode}
        >
          <ConversionFunnelChart
            totalLeads={ov.totalLeads}
            totalApps={ov.totalApplications}
            approvedApps={ov.approvedApplications}
            disbursedApps={ov.disbursedApplications}
            darkMode={darkMode}
          />
        </ChartCard>

        {/* 2. Monthly Lead Sourcing Trend Line Chart */}
        <ChartCard
          title="Lead Sourcing Volume Trend"
          subtitle="Time-based incoming lead trend"
          apiEndpoint="/api/v2/onboarding/leads/list/"
          darkMode={darkMode}
        >
          <TimeBasedTrendChart data={leadsMonthlyTrend} darkMode={darkMode} metricName="Leads" color="#0076eb" />
        </ChartCard>

        {/* 3. Top Sales Officers Leaderboard */}
        <ChartCard
          title="Top Sales Officers Leaderboard"
          subtitle="Highest lead & app originators (by user_id)"
          apiEndpoint="/user/employee & /user/employee/applications"
          darkMode={darkMode}
        >
          <SalesOfficerLeaderboardChart data={officerPerformance} darkMode={darkMode} />
        </ChartCard>
      </div>

      {/* ── VISUALIZATION SECTION: 4 Completely Distinct Chart Types ───── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 1. Application Status Breakdown (Vertical Column Chart) */}
        <ChartCard
          title="Application Status Breakdown"
          subtitle="Vertical Column Chart sorted descending by volume"
          apiEndpoint="/api/v2/onboarding/applications/list/"
          darkMode={darkMode}
        >
          <ApplicationStatusColumnChart data={appStatusDistribution} darkMode={darkMode} />
        </ChartCard>

        {/* 2. Product Subcategory Share (Ranked Horizontal Progress Bar List) */}
        <ChartCard
          title="Product Subcategory Share"
          subtitle="Ranked horizontal volume share (sorted by count)"
          apiEndpoint="/api/v2/onboarding/leads/list/"
          darkMode={darkMode}
        >
          <ProductSubcategoryRankedList data={productSubcatDistribution} darkMode={darkMode} />
        </ChartCard>

        {/* 3. Lead Type Distribution (Donut Chart) */}
        <ChartCard
          title="Lead Type Distribution"
          subtitle="Donut Chart with count & percentage badges"
          apiEndpoint="/api/v2/onboarding/leads/list/ (lead_type)"
          darkMode={darkMode}
        >
          <LeadTypeDonutChart data={leadTypeDistribution} darkMode={darkMode} />
        </ChartCard>

        {/* 4. Product Category Share (Donut Ring Gauge) */}
        <ChartCard
          title="Product Category Share"
          subtitle="Donut Ring Gauge (Loan vs Insurance)"
          apiEndpoint="/api/v2/onboarding/leads/list/"
          darkMode={darkMode}
        >
          <ProductCategoryDonutGauge data={productCatDistribution} darkMode={darkMode} />
        </ChartCard>
      </div>

      {/* ── GEOGRAPHIC SECTION: India State-Level Map ─────────────────── */}
      <MapSection stats={stats} darkMode={darkMode} />

      {/* Main Onboarding Leads Register Table */}
      <LeadsTable
        leads={leads}
        applications={stats?.applicationsList || []}
        darkMode={darkMode}
        totalCount={totalCount}
        onSelectCustomer={onSelectCustomer}
      />

    </div>
  );
};

export default OverviewTab;
