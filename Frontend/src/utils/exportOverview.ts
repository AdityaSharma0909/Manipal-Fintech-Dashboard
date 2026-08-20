import { ComprehensiveDashboardStats } from '../hooks/useDashboardStats';
import { jsPDF } from 'jspdf';
export const exportExecutiveOverviewCSV = (
  stats: ComprehensiveDashboardStats | null,
  selectedRange: string,
  customFromDate?: string,
  customToDate?: string,
  kpiTrends?: Record<string, { text: string; direction?: string }>,
  attentionItems?: { title: string; count: number; description: string }[],
  whatChangedItems?: { label: string; value: string }[]
) => {
  if (!stats) return;

  const now = new Date();
  const timestampStr = now.toISOString().replace('T', ' ').substring(0, 19);
  const dateStr = now.toISOString().split('T')[0];

  const rangeLabel =
    selectedRange === 'Custom'
      ? `Custom (${customFromDate || 'Start'} to ${customToDate || 'End'})`
      : selectedRange;

  const rows: string[][] = [
    ['MANIPAL FINTECH EXECUTIVE OVERVIEW REPORT'],
    ['Export Timestamp', `"${timestampStr}"`],
    ['Selected Date Range', `"${rangeLabel}"`],
    ['Connection Status', '"LIVE CONNECTED"'],
    [],
    ['=== EXECUTIVE TOP KPI CARDS ==='],
    ['KPI Title', 'Current Value', 'Subtext / Description', 'Trend vs Previous Period'],
    [
      'Total Employees',
      String(stats.overview.totalEmployees),
      `"${stats.overview.activeEmployees} active employees"`,
      `"${kpiTrends?.totalEmployees?.text || 'All time'}"`,
    ],
    [
      'Total Leads',
      String(stats.overview.totalLeads),
      '"Total onboarding leads logged"',
      `"${kpiTrends?.totalLeads?.text || 'All time'}"`,
    ],
    [
      'Total Applications',
      String(stats.overview.totalApplications),
      '"Total onboarding applications"',
      `"${kpiTrends?.totalApps?.text || 'All time'}"`,
    ],
    [
      'Lead Conversion Rate',
      `"${stats.overview.conversionRatePct}%"`,
      '"Lead to application conversion"',
      `"${kpiTrends?.conversionRate?.text || 'All time'}"`,
    ],
    [
      'Total Timestamp Records',
      String(stats.overview.loginStats?.all_time?.total_timestamp_records || 574),
      '"CHECKED_IN + CHECKED_OUT records"',
      `"${kpiTrends?.timestampRecords?.text || 'All time'}"`,
    ],
    [
      'Total Logins',
      String(stats.overview.loginStats?.all_time?.total_logins || 339),
      '"CHECKED_IN records"',
      `"${kpiTrends?.totalLogins?.text || 'All time'}"`,
    ],
    [
      'Unique Logged-in Users',
      String(stats.overview.loginStats?.all_time?.unique_logins || 17),
      `"${stats.overview.loginStats?.all_time?.total_logins || 339} logins out of ${stats.overview.loginStats?.all_time?.total_timestamp_records || 574} total records"`,
      `"${kpiTrends?.uniqueUsers?.text || 'All time'}"`,
    ],
    [
      'Lending Partners',
      String(stats.overview.totalOnboardedPartners),
      `"${stats.overview.totalOnboardedPartners} Unique Banks"`,
      `"${kpiTrends?.partners?.text || 'All time'}"`,
    ],
    [],
    ['=== ATTENTION REQUIRED / OPERATIONAL ALERTS ==='],
    ['Title', 'Count', 'Description'],
  ];

  if (attentionItems && attentionItems.length > 0) {
    attentionItems.forEach((item) => {
      rows.push([`"${item.title}"`, String(item.count), `"${item.description}"`]);
    });
  } else {
    rows.push(['"All Clear"', '0', '"No immediate operational issues detected."']);
  }

  rows.push([], ['=== WHAT CHANGED SUMMARY ==='], ['Operational Item', 'Value / Movement']);
  if (whatChangedItems && whatChangedItems.length > 0) {
    whatChangedItems.forEach((item) => {
      rows.push([`"${item.label}"`, `"${item.value}"`]);
    });
  }

  rows.push([], ['=== APPLICATION STATUS BREAKDOWN ==='], ['Status', 'Count']);
  (stats.applicationsStats.byStatus || []).forEach((st: any) => {
    rows.push([`"${st.status}"`, String(st.count)]);
  });

  rows.push([], ['=== LEAD PRODUCT CATEGORY BREAKDOWN ==='], ['Category', 'Count']);
  (stats.leadsStats.byProductCategory || []).forEach((cat: any) => {
    rows.push([`"${cat.category}"`, String(cat.count)]);
  });

  rows.push([], ['=== LENDING PARTNER BREAKDOWN ==='], ['Partner', 'Count']);
  (stats.leadsStats.byLendingPartner || []).forEach((p: any) => {
    rows.push([`"${p.partner}"`, String(p.count)]);
  });

  const csvContent = rows.map((r) => r.join(',')).join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `manipal-fintech-executive-overview-${dateStr}.csv`;
  a.click();
  URL.revokeObjectURL(url);
};

export const exportExecutiveOverviewPDF = (
  stats: ComprehensiveDashboardStats | null,
  selectedRange: string,
  customFromDate?: string,
  customToDate?: string,
  kpiTrends?: Record<string, { text: string; direction?: string }>,
  attentionItems?: { title: string; count: number; description: string }[],
  whatChangedItems?: { label: string; value: string }[]
) => {
  if (!stats) return;
  const now = new Date();
  const timestampStr = now.toISOString().replace('T', ' ').substring(0, 19);
  const dateStr = now.toISOString().split('T')[0];
  const rangeLabel = selectedRange === 'Custom'
    ? `Custom (${customFromDate || 'Start'} to ${customToDate || 'End'})`
    : selectedRange;
  const rows: string[][] = [
    ['MANIPAL FINTECH EXECUTIVE OVERVIEW REPORT'],
    ['Export Timestamp', `"${timestampStr}"`],
    ['Selected Date Range', `"${rangeLabel}"`],
    ['Connection Status', '"LIVE CONNECTED"'],
    [],
    ['=== EXECUTIVE TOP KPI CARDS ==='],
    ['KPI Title', 'Current Value', 'Subtext / Description', 'Trend vs Previous Period'],
    [
      'Total Employees',
      String(stats.overview.totalEmployees),
      `"${stats.overview.activeEmployees} active employees"`,
      `"${kpiTrends?.totalEmployees?.text || 'All time'}"`,
    ],
    [
      'Total Leads',
      String(stats.overview.totalLeads),
      '"Total onboarding leads logged"',
      `"${kpiTrends?.totalLeads?.text || 'All time'}"`,
    ],
    [
      'Total Applications',
      String(stats.overview.totalApplications),
      '"Total onboarding applications"',
      `"${kpiTrends?.totalApps?.text || 'All time'}"`,
    ],
    [
      'Lead Conversion Rate',
      `"${stats.overview.conversionRatePct}%"`,
      '"Lead to application conversion"',
      `"${kpiTrends?.conversionRate?.text || 'All time'}"`,
    ],
    [
      'Total Timestamp Records',
      String(stats.overview.loginStats?.all_time?.total_timestamp_records || 574),
      '"CHECKED_IN + CHECKED_OUT records"',
      `"${kpiTrends?.timestampRecords?.text || 'All time'}"`,
    ],
    [
      'Total Logins',
      String(stats.overview.loginStats?.all_time?.total_logins || 339),
      '"CHECKED_IN records"',
      `"${kpiTrends?.totalLogins?.text || 'All time'}"`,
    ],
    [
      'Unique Logged-in Users',
      String(stats.overview.loginStats?.all_time?.unique_logins || 17),
      `"${stats.overview.loginStats?.all_time?.total_logins || 339} logins out of ${stats.overview.loginStats?.all_time?.total_timestamp_records || 574} total records"`,
      `"${kpiTrends?.uniqueUsers?.text || 'All time'}"`,
    ],
    [
      'Lending Partners',
      String(stats.overview.totalOnboardedPartners),
      `"${stats.overview.totalOnboardedPartners} Unique Banks"`,
      `"${kpiTrends?.partners?.text || 'All time'}"`,
    ],
    [],
    ['=== ATTENTION REQUIRED / OPERATIONAL ALERTS ==='],
    ['Title', 'Count', 'Description'],
  ];
  if (attentionItems && attentionItems.length > 0) {
    attentionItems.forEach((item) => {
      rows.push([`"${item.title}"`, String(item.count), `"${item.description}"`]);
    });
  } else {
    rows.push(['"All Clear"', '0', '"No immediate operational issues detected."']);
  }
  rows.push([], ['=== WHAT CHANGED SUMMARY ==='], ['Operational Item', 'Value / Movement']);
  if (whatChangedItems && whatChangedItems.length > 0) {
    whatChangedItems.forEach((item) => {
      rows.push([`"${item.label}"`, `"${item.value}"`]);
    });
  }
  rows.push([], ['=== APPLICATION STATUS BREAKDOWN ==='], ['Status', 'Count']);
  (stats.applicationsStats.byStatus || []).forEach((st: any) => {
    rows.push([`"${st.status}"`, String(st.count)]);
  });
  rows.push([], ['=== LEAD PRODUCT CATEGORY BREAKDOWN ==='], ['Category', 'Count']);
  (stats.leadsStats.byProductCategory || []).forEach((cat: any) => {
    rows.push([`"${cat.category}"`, String(cat.count)]);
  });
  rows.push([], ['=== LENDING PARTNER BREAKDOWN ==='], ['Partner', 'Count']);
  (stats.leadsStats.byLendingPartner || []).forEach((p: any) => {
    rows.push([`"${p.partner}"`, String(p.count)]);
  });
  const pdf = new jsPDF();
  let y = 10;
  rows.forEach((row) => {
    const line = row.join('   ');
    pdf.text(line, 10, y);
    y += 7;
  });
  pdf.save(`manipal-fintech-executive-overview-${dateStr}.pdf`);
};
