import React from 'react';
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LabelList
} from 'recharts';
import { Info } from 'lucide-react';

interface ChartCardProps {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  darkMode: boolean;
  action?: React.ReactNode;
  apiEndpoint?: string;
}

export const formatEnumLabel = (raw: string): string => {
  if (!raw) return 'Other';
  const str = String(raw).trim();
  const upper = str.toUpperCase();
  const labelMap: Record<string, string> = {
    GOLD_LOAN: 'Gold Loan',
    PERSONAL_LOAN: 'Personal Loan',
    BUSINESS_LOAN: 'Business Loan',
    HOME_LOAN: 'Home Loan',
    LOAN_AGAINST_PROPERTY: 'Loan Against Property',
    HEALTH_INSURANCE: 'Health Insurance',
    WORKING_CAPITAL: 'Working Capital',
    OVERDRAFT_DOD: 'Overdraft DOD',
    MOTOR_LOAN: 'Motor Loan',
    CREDIT_CARDS: 'Credit Cards',
    MOTOR_INSURANCE: 'Motor Insurance',
    BALANCE_TRANSFER: 'Balance Transfer',
    FRESH: 'Fresh',
    BANK_LEAD: 'Bank Lead',
    CO_LENDING: 'Co-Lending',
    SELF_LENDING: 'Self-Lending',
    LOAN: 'Loan',
    INSURANCE: 'Insurance',
    LOAN_STATUS_UPDATED: 'Status Updated',
    IN_PROGRESS: 'In Progress',
    DRAFT: 'Draft',
    SUBMITTED_TO_UNDERWRITING: 'Underwriting Submitted',
    PUNCHING_PENDING: 'Punching Pending',
    REJECTED: 'Rejected',
    ESIGN_INITIATED: 'eSign Initiated',
    REJECTED_BY_UNDERWRITING: 'Underwriting Rejected',
    APPROVED_BY_RH: 'Approved by RH',
    SENT_FOR_PRE_SCREENING: 'Prescreening',
    ESIGN_COMPLETED: 'eSign Completed',
    READY_FOR_LOAN: 'Ready for Loan',
    RH_APPROVAL_PENDING: 'RH Pending',
    NOT_ELIGIBLE: 'Not Eligible',
  };

  if (labelMap[upper]) return labelMap[upper];

  return upper
    .split('_')
    .map((w) => w.charAt(0) + w.slice(1).toLowerCase())
    .join(' ');
};

const tt = (dark: boolean) => ({
  contentStyle: {
    background: dark ? '#111827' : '#ffffff',
    border: `1px solid ${dark ? '#374151' : '#e5e7eb'}`,
    borderRadius: '12px',
    fontSize: '11px',
    color: dark ? '#f3f4f6' : '#111827',
    boxShadow: '0 10px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.1)',
  },
  labelStyle: { color: dark ? '#9ca3af' : '#4b5563', fontWeight: 700 },
  itemStyle: { color: dark ? '#e5e7eb' : '#1f2937' },
});

export const ChartCard: React.FC<ChartCardProps> = ({ title, subtitle, children, darkMode, action, apiEndpoint }) => (
  <div
    className={`group rounded-2xl border p-5 transition-all duration-300 hover:shadow-xl flex flex-col justify-between ${
      darkMode
        ? 'bg-gray-900/80 border-gray-800 hover:border-gray-700 backdrop-blur-xl'
        : 'bg-white border-gray-200/80 hover:border-gray-300 shadow-sm'
    }`}
  >
    <div>
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className={`text-sm font-bold tracking-tight ${darkMode ? 'text-white' : 'text-gray-900'}`}>{title}</h3>
          {subtitle && <p className={`text-xs mt-0.5 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>{subtitle}</p>}
        </div>
        <div className="flex items-center gap-2">
          {action}
          {apiEndpoint && (
            <div className="relative group/tooltip">
              <Info size={14} className={`${darkMode ? 'text-gray-500 group-hover/tooltip:text-gray-300' : 'text-gray-400 group-hover/tooltip:text-gray-600'} transition-colors cursor-pointer`} />
              <div className={`absolute right-0 top-full mt-1.5 hidden group-hover/tooltip:flex flex-col whitespace-nowrap z-50 px-2.5 py-1 rounded-lg text-[10px] font-mono shadow-xl border pointer-events-none ${
                darkMode ? 'bg-gray-800 border-gray-700 text-gray-200' : 'bg-gray-900 border-gray-800 text-white'
              }`}>
                <span className="text-[9px] text-gray-400 font-sans uppercase font-bold tracking-wider">Data Source</span>
                <span>{apiEndpoint}</span>
              </div>
            </div>
          )}
        </div>
      </div>
      {children}
    </div>
  </div>
);

// ── 1. Funnel Visualization (Conversion Pipeline) ─────────────────
export const ConversionFunnelChart: React.FC<{
  totalLeads: number;
  totalApps: number;
  approvedApps: number;
  disbursedApps?: number;
  darkMode: boolean;
}> = ({ totalLeads, totalApps, approvedApps, disbursedApps = 0, darkMode }) => {
  const steps = [
    {
      label: '1. Sourced Leads',
      count: totalLeads,
      pct: 100,
      color: '#0076eb',
      bg: darkMode ? 'bg-blue-900/20 border-blue-500/30' : 'bg-blue-50 border-blue-200',
    },
    {
      label: '2. Applications Created',
      count: totalApps,
      pct: totalLeads > 0 ? Math.round((totalApps / totalLeads) * 100) : 0,
      color: '#8b5cf6',
      bg: darkMode ? 'bg-purple-900/20 border-purple-500/30' : 'bg-purple-50 border-purple-200',
    },
    {
      label: '3. Approved Applications',
      count: approvedApps,
      pct: totalLeads > 0 ? Math.round((approvedApps / totalLeads) * 100) : 0,
      color: '#10b981',
      bg: darkMode ? 'bg-emerald-900/20 border-emerald-500/30' : 'bg-emerald-50 border-emerald-200',
    },
    {
      label: '4. Disbursed Loans',
      count: disbursedApps,
      pct: totalLeads > 0 ? Math.round((disbursedApps / totalLeads) * 100) : 0,
      color: '#f59e0b',
      bg: darkMode ? 'bg-amber-900/20 border-amber-500/30' : 'bg-amber-50 border-amber-200',
    },
  ];

  return (
    <div className="space-y-3 py-1">
      {steps.map((step, idx) => (
        <div key={idx} className="relative">
          <div className={`p-3.5 rounded-xl border transition-all ${step.bg}`}>
            <div className="flex items-center justify-between mb-1.5">
              <span className={`text-xs font-bold ${darkMode ? 'text-gray-200' : 'text-gray-800'}`}>{step.label}</span>
              <div className="flex items-center gap-2">
                <span className={`text-sm font-extrabold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                  {step.count.toLocaleString()}
                </span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-white/40 dark:bg-black/40">
                  {step.pct}%
                </span>
              </div>
            </div>
            <div className={`h-2 rounded-full overflow-hidden ${darkMode ? 'bg-gray-800' : 'bg-white/80'}`}>
              <div
                className="h-full rounded-full transition-all duration-700 ease-out"
                style={{ width: `${Math.max(3, step.pct)}%`, backgroundColor: step.color }}
              />
            </div>
          </div>
          {idx < steps.length - 1 && (
            <div className="flex justify-center my-0.5 text-gray-400 text-[10px] font-bold">↓</div>
          )}
        </div>
      ))}
    </div>
  );
};

// ── 2. Time-Based Trend Line Chart ────────────────────────────────
export const TimeBasedTrendChart: React.FC<{
  data: { month: string; count: number }[];
  darkMode: boolean;
  metricName?: string;
  color?: string;
}> = ({ data, darkMode, metricName = 'Count', color = '#0076eb' }) => {
  const { contentStyle, labelStyle, itemStyle } = tt(darkMode);
  const grid = darkMode ? '#374151' : '#f3f4f6';

  return (
    <ResponsiveContainer width="100%" height={230}>
      <AreaChart data={data} margin={{ top: 10, right: 10, bottom: 0, left: -20 }}>
        <defs>
          <linearGradient id="trendGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={color} stopOpacity={0.3} />
            <stop offset="95%" stopColor={color} stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke={grid} vertical={false} />
        <XAxis dataKey="month" tick={{ fontSize: 11, fill: darkMode ? '#9ca3af' : '#6b7280' }} axisLine={false} tickLine={false} />
        <YAxis tick={{ fontSize: 11, fill: darkMode ? '#9ca3af' : '#6b7280' }} axisLine={false} tickLine={false} />
        <Tooltip contentStyle={contentStyle} labelStyle={labelStyle} itemStyle={itemStyle} />
        <Area
          type="monotone"
          dataKey="count"
          name={metricName}
          stroke={color}
          strokeWidth={3}
          fill="url(#trendGrad)"
          dot={{ fill: color, r: 4, strokeWidth: 2, stroke: darkMode ? '#111827' : '#fff' }}
          activeDot={{ r: 6 }}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
};

export const MonthlyDisbursalChart = TimeBasedTrendChart;

// ── 3. Ranked Sales Officer Leaderboard ───────────────────────────
export const SalesOfficerLeaderboardChart: React.FC<{
  data: { user_id: string; name: string; leadsHandled: number; appsHandled: number; conversionRate: number }[];
  darkMode: boolean;
}> = ({ data, darkMode }) => {
  const topOfficers = data.slice(0, 5);

  return (
    <div className="space-y-3">
      {topOfficers.length === 0 ? (
        <div className="text-center py-6 text-xs text-gray-500">No officer activity recorded yet.</div>
      ) : (
        topOfficers.map((officer, i) => (
          <div key={officer.user_id || i} className={`p-3 rounded-xl border ${darkMode ? 'bg-gray-800/40 border-gray-700' : 'bg-gray-50 border-gray-200'}`}>
            <div className="flex items-center justify-between mb-1.5">
              <span className={`text-xs font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                #{i + 1} {officer.name}
              </span>
              <div className="flex items-center gap-2.5 text-xs font-semibold">
                <span className="text-brand-blue">{officer.leadsHandled} Leads</span>
                <span className="text-purple-500">{officer.appsHandled} Apps</span>
                <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-600 font-bold">
                  {officer.conversionRate}% Conv
                </span>
              </div>
            </div>
            <div className={`h-2 rounded-full overflow-hidden ${darkMode ? 'bg-gray-700' : 'bg-gray-200'}`}>
              <div
                className="h-full bg-gradient-to-r from-brand-blue to-emerald-500 rounded-full transition-all duration-500"
                style={{ width: `${Math.min(100, Math.max(10, officer.conversionRate))}%` }}
              />
            </div>
          </div>
        ))
      )}
    </div>
  );
};

// ── 4. Application Status Column Chart ─────────────────────────────
export const ApplicationStatusColumnChart: React.FC<{
  data: { name: string; count: number }[];
  darkMode: boolean;
}> = ({ data, darkMode }) => {
  const sorted = [...data]
    .map((item) => ({ name: formatEnumLabel(item.name), count: item.count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 8);

  const { contentStyle, labelStyle, itemStyle } = tt(darkMode);
  const grid = darkMode ? '#374151' : '#f3f4f6';

  return (
    <ResponsiveContainer width="100%" height={230}>
      <BarChart data={sorted} margin={{ top: 25, right: 10, bottom: 35, left: -20 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={grid} vertical={false} />
        <XAxis
          dataKey="name"
          tick={{ fontSize: 9, fill: darkMode ? '#9ca3af' : '#6b7280' }}
          interval={0}
          angle={-25}
          textAnchor="end"
          axisLine={false}
          tickLine={false}
        />
        <YAxis tick={{ fontSize: 10, fill: darkMode ? '#9ca3af' : '#6b7280' }} axisLine={false} tickLine={false} />
        <Tooltip contentStyle={contentStyle} labelStyle={labelStyle} itemStyle={itemStyle} />
        <Bar dataKey="count" name="Applications" radius={[6, 6, 0, 0]}>
          <LabelList dataKey="count" position="top" fill={darkMode ? '#f3f4f6' : '#111827'} fontSize={10} fontWeight={800} />
          {sorted.map((_, i) => (
            <Cell key={i} fill={['#8b5cf6', '#0076eb', '#10b981', '#f59e0b', '#ec4899', '#6366f1'][i % 6]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
};

// ── 5. Product Subcategory Ranked Horizontal Bar List (Ultra Clean) ──
export const ProductSubcategoryRankedList: React.FC<{
  data: { name: string; count: number }[];
  darkMode: boolean;
}> = ({ data, darkMode }) => {
  const sorted = [...data]
    .map((d) => ({ name: formatEnumLabel(d.name), count: d.count }))
    .sort((a, b) => b.count - a.count);

  const maxCount = Math.max(1, ...sorted.map((s) => s.count));
  const total = sorted.reduce((sum, s) => sum + s.count, 0);

  const BAR_COLORS = [
    'from-blue-600 to-indigo-600',
    'from-purple-600 to-violet-600',
    'from-emerald-500 to-teal-600',
    'from-amber-500 to-orange-500',
    'from-pink-500 to-rose-600',
    'from-cyan-500 to-blue-500',
    'from-indigo-500 to-blue-700',
  ];

  return (
    <div className="space-y-3 max-h-[230px] overflow-y-auto pr-1">
      {sorted.length === 0 ? (
        <div className="text-center py-6 text-xs text-gray-500">No subcategory data found.</div>
      ) : (
        sorted.map((item, idx) => {
          const pct = total > 0 ? ((item.count / total) * 100).toFixed(1) : '0';
          const barPct = Math.round((item.count / maxCount) * 100);
          const barColor = BAR_COLORS[idx % BAR_COLORS.length];

          return (
            <div key={idx} className="space-y-1">
              <div className="flex items-center justify-between text-xs font-semibold">
                <div className="flex items-center gap-2">
                  <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${darkMode ? 'bg-gray-800 text-gray-400' : 'bg-gray-100 text-gray-600'}`}>
                    #{idx + 1}
                  </span>
                  <span className={`truncate max-w-[190px] font-bold ${darkMode ? 'text-gray-200' : 'text-gray-800'}`}>
                    {item.name}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`font-extrabold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                    {item.count.toLocaleString()}
                  </span>
                  <span className="text-[10px] text-brand-blue font-bold font-mono">({pct}%)</span>
                </div>
              </div>
              <div className={`h-2.5 rounded-full overflow-hidden ${darkMode ? 'bg-gray-800' : 'bg-gray-100'}`}>
                <div
                  className={`h-full bg-gradient-to-r ${barColor} rounded-full transition-all duration-500`}
                  style={{ width: `${Math.max(4, barPct)}%` }}
                />
              </div>
            </div>
          );
        })
      )}
    </div>
  );
};

export const ProductSubcategoryTreemap = ProductSubcategoryRankedList;

// ── 6. Product Category Donut Ring Gauge (Loan vs Insurance) ──────
export const ProductCategoryDonutGauge: React.FC<{
  data: { name: string; count: number }[];
  darkMode: boolean;
}> = ({ data, darkMode }) => {
  const formatted = data.map((d) => ({ name: formatEnumLabel(d.name), count: d.count }));
  const total = formatted.reduce((sum, item) => sum + item.count, 0);
  const COLORS = ['#0076eb', '#10b981', '#8b5cf6'];
  const { contentStyle, labelStyle, itemStyle } = tt(darkMode);

  return (
    <div className="flex items-center justify-between py-2">
      <ResponsiveContainer width="48%" height={190}>
        <PieChart>
          <Pie
            data={formatted}
            dataKey="count"
            nameKey="name"
            cx="50%"
            cy="50%"
            innerRadius={50}
            outerRadius={75}
            paddingAngle={4}
          >
            {formatted.map((_, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip contentStyle={contentStyle} labelStyle={labelStyle} itemStyle={itemStyle} />
        </PieChart>
      </ResponsiveContainer>

      <div className="w-[48%] space-y-3">
        {formatted.map((item, i) => {
          const pct = total > 0 ? ((item.count / total) * 100).toFixed(1) : '0';
          return (
            <div key={item.name} className={`p-3 rounded-xl border ${darkMode ? 'bg-gray-800/40 border-gray-700' : 'bg-gray-50 border-gray-200'}`}>
              <div className="flex items-center justify-between text-xs font-bold mb-1">
                <div className="flex items-center gap-1.5">
                  <div className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: COLORS[i % COLORS.length] }} />
                  <span className={darkMode ? 'text-white' : 'text-gray-900'}>{item.name}</span>
                </div>
                <span className="text-brand-blue font-extrabold">{pct}%</span>
              </div>
              <div className="text-xs text-gray-500 font-bold">{item.count.toLocaleString()} leads</div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export const ProductCategorySplitBarChart = ProductCategoryDonutGauge;

// ── 7. Lead Type Donut Chart ──────────────────────────────────────
export const LeadTypeDonutChart: React.FC<{
  data: { name: string; count: number }[];
  darkMode: boolean;
}> = ({ data, darkMode }) => {
  const normalizedMap = new Map<string, number>();

  data.forEach((item) => {
    const label = formatEnumLabel(item.name);
    normalizedMap.set(label, (normalizedMap.get(label) || 0) + item.count);
  });

  const formatted = Array.from(normalizedMap.entries())
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count);

  const total = formatted.reduce((sum, item) => sum + item.count, 0);
  const COLORS = ['#f59e0b', '#0076eb', '#8b5cf6', '#10b981', '#ec4899'];
  const { contentStyle, labelStyle, itemStyle } = tt(darkMode);

  return (
    <div className="flex items-center justify-between py-2">
      <ResponsiveContainer width="48%" height={190}>
        <PieChart>
          <Pie
            data={formatted}
            dataKey="count"
            nameKey="name"
            cx="50%"
            cy="50%"
            innerRadius={45}
            outerRadius={75}
            paddingAngle={4}
          >
            {formatted.map((_, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip contentStyle={contentStyle} labelStyle={labelStyle} itemStyle={itemStyle} />
        </PieChart>
      </ResponsiveContainer>

      <div className="w-[48%] space-y-2 max-h-[190px] overflow-y-auto pr-1">
        {formatted.map((item, i) => {
          const pct = total > 0 ? ((item.count / total) * 100).toFixed(1) : '0';
          return (
            <div key={item.name} className={`p-2.5 rounded-xl border ${darkMode ? 'bg-gray-800/40 border-gray-700' : 'bg-gray-50 border-gray-200'}`}>
              <div className="flex items-center justify-between text-xs font-bold mb-0.5">
                <div className="flex items-center gap-1.5">
                  <div className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: COLORS[i % COLORS.length] }} />
                  <span className={`truncate max-w-[90px] ${darkMode ? 'text-white' : 'text-gray-900'}`}>{item.name}</span>
                </div>
                <span className="text-amber-500 font-bold">{pct}%</span>
              </div>
              <div className="text-[10px] text-gray-500 font-semibold">{item.count.toLocaleString()} leads</div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// ── Backwards Compatible Export Aliases ───────────────────────────
export const ApplicationStatusRankedChart = ApplicationStatusColumnChart;
export const ProductCategoryDonutChart = ProductCategoryDonutGauge;
export const RankedHorizontalBarChart = ProductSubcategoryRankedList;
export const LeadTypeHorizontalChart = LeadTypeDonutChart;
export const CategoricalBarChart = ApplicationStatusColumnChart;
export const ProductDistributionChart = ProductCategoryDonutGauge;
export const LendingPartnerPerformanceChart = ApplicationStatusColumnChart;
export const TrackedLendersChart = ApplicationStatusColumnChart;
export const ApplicationStatusChart = ApplicationStatusColumnChart;
export const LoanTypeChart = ProductSubcategoryRankedList;

export const DailyActiveChart: React.FC<{ data: any[]; darkMode: boolean }> = ({ data, darkMode }) => {
  const { contentStyle, labelStyle, itemStyle } = tt(darkMode);
  const grid = darkMode ? '#374151' : '#f3f4f6';
  return (
    <ResponsiveContainer width="100%" height={220}>
      <AreaChart data={data} margin={{ top: 5, right: 10, bottom: 0, left: -10 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={grid} />
        <XAxis dataKey="day" tick={{ fontSize: 11, fill: darkMode ? '#9ca3af' : '#6b7280' }} axisLine={false} tickLine={false} />
        <YAxis tick={{ fontSize: 11, fill: darkMode ? '#9ca3af' : '#6b7280' }} axisLine={false} tickLine={false} />
        <Tooltip contentStyle={contentStyle} labelStyle={labelStyle} itemStyle={itemStyle} />
        <Area type="monotone" dataKey="users" name="Active Users" stroke="#0076eb" strokeWidth={2} fill="#0076eb" fillOpacity={0.15} />
      </AreaChart>
    </ResponsiveContainer>
  );
};

export const RetentionChart: React.FC<{ data: any[]; darkMode: boolean }> = ({ data, darkMode }) => {
  const { contentStyle, labelStyle, itemStyle } = tt(darkMode);
  return (
    <ResponsiveContainer width="100%" height={180}>
      <AreaChart data={data} margin={{ top: 5, right: 10, bottom: 0, left: -20 }}>
        <XAxis dataKey="week" tick={{ fontSize: 10, fill: darkMode ? '#9ca3af' : '#6b7280' }} axisLine={false} tickLine={false} />
        <YAxis tick={{ fontSize: 10, fill: darkMode ? '#9ca3af' : '#6b7280' }} axisLine={false} tickLine={false} />
        <Tooltip contentStyle={contentStyle} labelStyle={labelStyle} itemStyle={itemStyle} />
        <Area type="monotone" dataKey="rate" stroke="#e5b83b" strokeWidth={2} fill="#e5b83b" fillOpacity={0.15} />
      </AreaChart>
    </ResponsiveContainer>
  );
};

export const PeakHoursChart: React.FC<{ data: any[]; darkMode: boolean }> = ({ data, darkMode }) => {
  const { contentStyle, labelStyle, itemStyle } = tt(darkMode);
  return (
    <ResponsiveContainer width="100%" height={180}>
      <BarChart data={data} margin={{ top: 5, right: 10, bottom: 0, left: -20 }}>
        <XAxis dataKey="hour" tick={{ fontSize: 10, fill: darkMode ? '#9ca3af' : '#6b7280' }} axisLine={false} tickLine={false} />
        <YAxis tick={{ fontSize: 10, fill: darkMode ? '#9ca3af' : '#6b7280' }} axisLine={false} tickLine={false} />
        <Tooltip contentStyle={contentStyle} labelStyle={labelStyle} itemStyle={itemStyle} />
        <Bar dataKey="users" name="Active Users" fill="#0076eb" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
};

export const TopFeaturesChart: React.FC<{ data: any[]; darkMode: boolean }> = ({ data, darkMode }) => {
  return (
    <div className="space-y-3">
      {data.map((item, i) => (
        <div key={i}>
          <div className="flex items-center justify-between mb-1">
            <span className={`text-xs font-medium ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>{item.feature}</span>
            <span className={`text-xs font-bold ${darkMode ? 'text-gray-200' : 'text-gray-800'}`}>{item.usage.toLocaleString()}</span>
          </div>
          <div className={`h-2 rounded-full ${darkMode ? 'bg-gray-700' : 'bg-gray-100'} overflow-hidden`}>
            <div className="h-full rounded-full" style={{ width: `${(item.usage / data[0].usage) * 100}%`, background: item.color }} />
          </div>
        </div>
      ))}
    </div>
  );
};
