import React from 'react';
import {
  AreaChart, Area, BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend
} from 'recharts';

interface ChartCardProps {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  darkMode: boolean;
  action?: React.ReactNode;
}

const tt = (dark: boolean) => ({
  contentStyle: {
    background: dark ? '#1f2937' : '#fff',
    border: `1px solid ${dark ? '#374151' : '#e5e7eb'}`,
    borderRadius: '12px',
    fontSize: '11px',
    color: dark ? '#d1d5db' : '#374151',
    boxShadow: '0 4px 24px rgba(0,0,0,0.08)',
  },
  labelStyle: { color: dark ? '#9ca3af' : '#6b7280', fontWeight: 600 },
  itemStyle: { color: dark ? '#d1d5db' : '#374151' },
});

export const ChartCard: React.FC<ChartCardProps> = ({ title, subtitle, children, darkMode, action }) => (
  <div className={`rounded-2xl border p-5 transition-all hover:shadow-lg ${
    darkMode ? 'bg-gray-800/60 border-gray-700 hover:border-gray-600' : 'bg-white border-gray-100 hover:border-gray-200'
  }`}>
    <div className="flex items-start justify-between mb-4">
      <div>
        <h3 className={`text-sm font-semibold ${darkMode ? 'text-white' : 'text-gray-900'}`}>{title}</h3>
        {subtitle && <p className={`text-xs mt-0.5 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>{subtitle}</p>}
      </div>
      {action && <div>{action}</div>}
    </div>
    {children}
  </div>
);

// Daily Active Users - Area Chart
export const DailyActiveChart: React.FC<{ data: any[]; darkMode: boolean }> = ({ data, darkMode }) => {
  const { contentStyle, labelStyle, itemStyle } = tt(darkMode);
  const grid = darkMode ? '#374151' : '#f3f4f6';
  return (
    <ResponsiveContainer width="100%" height={220}>
      <AreaChart data={data} margin={{ top: 5, right: 10, bottom: 0, left: -10 }}>
        <defs>
          <linearGradient id="dau1" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#0076eb" stopOpacity={0.15} />
            <stop offset="95%" stopColor="#0076eb" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="dau2" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#10b981" stopOpacity={0.15} />
            <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke={grid} />
        <XAxis dataKey="day" tick={{ fontSize: 11, fill: darkMode ? '#9ca3af' : '#6b7280' }} axisLine={false} tickLine={false} />
        <YAxis tick={{ fontSize: 11, fill: darkMode ? '#9ca3af' : '#6b7280' }} axisLine={false} tickLine={false} />
        <Tooltip contentStyle={contentStyle} labelStyle={labelStyle} itemStyle={itemStyle} />
        <Area type="monotone" dataKey="users" name="Active Users" stroke="#0076eb" strokeWidth={2} fill="url(#dau1)" dot={false} activeDot={{ r: 4, fill: '#0076eb' }} />
        <Area type="monotone" dataKey="newUsers" name="New Users" stroke="#10b981" strokeWidth={2} fill="url(#dau2)" dot={false} activeDot={{ r: 4, fill: '#10b981' }} />
        <Legend wrapperStyle={{ fontSize: '11px' }} />
      </AreaChart>
    </ResponsiveContainer>
  );
};

// Monthly MAU - Area Chart
export const MonthlyChart: React.FC<{ data: any[]; darkMode: boolean }> = ({ data, darkMode }) => {
  const { contentStyle, labelStyle, itemStyle } = tt(darkMode);
  const grid = darkMode ? '#374151' : '#f3f4f6';
  return (
    <ResponsiveContainer width="100%" height={220}>
      <AreaChart data={data} margin={{ top: 5, right: 10, bottom: 0, left: -10 }}>
        <defs>
          <linearGradient id="mauGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#0076eb" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#0076eb" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke={grid} vertical={false} />
        <XAxis dataKey="month" tick={{ fontSize: 11, fill: darkMode ? '#9ca3af' : '#6b7280' }} axisLine={false} tickLine={false} />
        <YAxis tick={{ fontSize: 11, fill: darkMode ? '#9ca3af' : '#6b7280' }} axisLine={false} tickLine={false} />
        <Tooltip contentStyle={contentStyle} labelStyle={labelStyle} itemStyle={itemStyle} formatter={(v: any) => [v.toLocaleString(), 'Active Users']} />
        <Area type="monotone" dataKey="mau" name="MAU" stroke="#0076eb" strokeWidth={3} fill="url(#mauGrad)" dot={{ fill: '#0076eb', r: 4, strokeWidth: 2, stroke: darkMode ? '#1f2937' : '#fff' }} activeDot={{ r: 6, strokeWidth: 0 }} />
      </AreaChart>
    </ResponsiveContainer>
  );
};

// New vs Returning - Stacked Bar
export const NewVsReturningChart: React.FC<{ data: any[]; darkMode: boolean }> = ({ data, darkMode }) => {
  const { contentStyle, labelStyle, itemStyle } = tt(darkMode);
  const grid = darkMode ? '#374151' : '#f3f4f6';
  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} margin={{ top: 5, right: 10, bottom: 0, left: -10 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={grid} />
        <XAxis dataKey="month" tick={{ fontSize: 11, fill: darkMode ? '#9ca3af' : '#6b7280' }} axisLine={false} tickLine={false} />
        <YAxis tick={{ fontSize: 11, fill: darkMode ? '#9ca3af' : '#6b7280' }} axisLine={false} tickLine={false} />
        <Tooltip contentStyle={contentStyle} labelStyle={labelStyle} itemStyle={itemStyle} />
        <Bar dataKey="returning" name="Returning" fill="#0076eb" radius={[0, 0, 4, 4]} stackId="a" />
        <Bar dataKey="new" name="New" fill="#10b981" radius={[4, 4, 0, 0]} stackId="a" />
        <Legend wrapperStyle={{ fontSize: '11px' }} />
      </BarChart>
    </ResponsiveContainer>
  );
};

// Peak Hours - Bar
export const PeakHoursChart: React.FC<{ data: any[]; darkMode: boolean }> = ({ data, darkMode }) => {
  const { contentStyle, labelStyle, itemStyle } = tt(darkMode);
  return (
    <ResponsiveContainer width="100%" height={180}>
      <BarChart data={data} margin={{ top: 5, right: 10, bottom: 0, left: -20 }}>
        <XAxis dataKey="hour" tick={{ fontSize: 10, fill: darkMode ? '#9ca3af' : '#6b7280' }} axisLine={false} tickLine={false} />
        <YAxis tick={{ fontSize: 10, fill: darkMode ? '#9ca3af' : '#6b7280' }} axisLine={false} tickLine={false} />
        <Tooltip contentStyle={contentStyle} labelStyle={labelStyle} itemStyle={itemStyle} />
        <Bar dataKey="users" name="Active Users" radius={[4, 4, 0, 0]}>
          {data.map((_, i) => (
            <Cell key={i} fill={i === 4 ? '#0076eb' : darkMode ? '#374151' : '#e0e7ff'} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
};

// Top Features - Horizontal Bar
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
            <div
              className="h-full rounded-full transition-all duration-700"
              style={{ width: `${(item.usage / data[0].usage) * 100}%`, background: item.color }}
            />
          </div>
        </div>
      ))}
    </div>
  );
};

// Retention - Area Chart
export const RetentionChart: React.FC<{ data: any[]; darkMode: boolean }> = ({ data, darkMode }) => {
  const { contentStyle, labelStyle, itemStyle } = tt(darkMode);
  const grid = darkMode ? '#374151' : '#f3f4f6';
  return (
    <ResponsiveContainer width="100%" height={180}>
      <AreaChart data={data} margin={{ top: 5, right: 10, bottom: 0, left: -20 }}>
        <defs>
          <linearGradient id="ret" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#e5b83b" stopOpacity={0.2} />
            <stop offset="95%" stopColor="#e5b83b" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke={grid} />
        <XAxis dataKey="week" tick={{ fontSize: 10, fill: darkMode ? '#9ca3af' : '#6b7280' }} axisLine={false} tickLine={false} />
        <YAxis tick={{ fontSize: 10, fill: darkMode ? '#9ca3af' : '#6b7280' }} axisLine={false} tickLine={false} domain={[60, 100]} />
        <Tooltip contentStyle={contentStyle} labelStyle={labelStyle} itemStyle={itemStyle} formatter={(v: any) => [`${v}%`, 'Retention']} />
        <Area type="monotone" dataKey="rate" stroke="#e5b83b" strokeWidth={2} fill="url(#ret)" dot={{ fill: '#e5b83b', r: 3 }} />
      </AreaChart>
    </ResponsiveContainer>
  );
};

// AI Usage Stacked Area
export const AIUsageChart: React.FC<{ data: any[]; darkMode: boolean }> = ({ data, darkMode }) => {
  const { contentStyle, labelStyle, itemStyle } = tt(darkMode);
  const grid = darkMode ? '#374151' : '#f3f4f6';
  return (
    <ResponsiveContainer width="100%" height={220}>
      <AreaChart data={data} margin={{ top: 5, right: 10, bottom: 0, left: -10 }}>
        <defs>
          <linearGradient id="ait" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#0076eb" stopOpacity={0.2} />
            <stop offset="95%" stopColor="#0076eb" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="aic" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#10b981" stopOpacity={0.2} />
            <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke={grid} />
        <XAxis dataKey="month" tick={{ fontSize: 11, fill: darkMode ? '#9ca3af' : '#6b7280' }} axisLine={false} tickLine={false} />
        <YAxis yAxisId="left" tick={{ fontSize: 11, fill: darkMode ? '#9ca3af' : '#6b7280' }} axisLine={false} tickLine={false} />
        <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 11, fill: darkMode ? '#9ca3af' : '#6b7280' }} axisLine={false} tickLine={false} />
        <Tooltip contentStyle={contentStyle} labelStyle={labelStyle} itemStyle={itemStyle} />
        <Area yAxisId="left" type="monotone" dataKey="tokens" name="Tokens" stroke="#0076eb" strokeWidth={2} fill="url(#ait)" dot={false} />
        <Area yAxisId="right" type="monotone" dataKey="conversations" name="Conversations" stroke="#10b981" strokeWidth={2} fill="url(#aic)" dot={false} />
        <Legend wrapperStyle={{ fontSize: '11px' }} />
      </AreaChart>
    </ResponsiveContainer>
  );
};

// AI Models Donut
export const AIModelsDonut: React.FC<{ data: any[]; darkMode: boolean }> = ({ data, darkMode }) => {
  const { contentStyle, labelStyle, itemStyle } = tt(darkMode);
  return (
    <div className="flex items-center gap-4">
      <ResponsiveContainer width={140} height={140}>
        <PieChart>
          <Pie data={data} cx="50%" cy="50%" innerRadius={42} outerRadius={60} paddingAngle={3} dataKey="value" startAngle={90} endAngle={450}>
            {data.map((entry, i) => (
              <Cell key={i} fill={entry.color} stroke="none" />
            ))}
          </Pie>
          <Tooltip contentStyle={contentStyle} labelStyle={labelStyle} itemStyle={itemStyle} />
        </PieChart>
      </ResponsiveContainer>
      <div className="flex-1 space-y-2">
        {data.map((item, i) => (
          <div key={i} className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-2.5 h-2.5 rounded-sm" style={{ background: item.color }} />
              <span className={`text-xs ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>{item.name}</span>
            </div>
            <span className={`text-xs font-bold ${darkMode ? 'text-gray-200' : 'text-gray-800'}`}>{item.value}%</span>
          </div>
        ))}
      </div>
    </div>
  );
};

// AI Radar
export const AIRadarChart: React.FC<{ data: any[]; darkMode: boolean }> = ({ data, darkMode }) => {
  const { contentStyle, labelStyle, itemStyle } = tt(darkMode);
  return (
    <ResponsiveContainer width="100%" height={200}>
      <RadarChart data={data}>
        <PolarGrid stroke={darkMode ? '#374151' : '#e5e7eb'} />
        <PolarAngleAxis dataKey="subject" tick={{ fontSize: 10, fill: darkMode ? '#9ca3af' : '#6b7280' }} />
        <Radar name="Score" dataKey="score" stroke="#0076eb" fill="#0076eb" fillOpacity={0.15} strokeWidth={2} />
        <Tooltip contentStyle={contentStyle} labelStyle={labelStyle} itemStyle={itemStyle} />
      </RadarChart>
    </ResponsiveContainer>
  );
};

// Revenue Bar Chart
export const RevenueChart: React.FC<{ data: any[]; darkMode: boolean }> = ({ data, darkMode }) => {
  const { contentStyle, labelStyle, itemStyle } = tt(darkMode);
  const grid = darkMode ? '#374151' : '#f3f4f6';
  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} margin={{ top: 5, right: 10, bottom: 0, left: -10 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={grid} />
        <XAxis dataKey="month" tick={{ fontSize: 11, fill: darkMode ? '#9ca3af' : '#6b7280' }} axisLine={false} tickLine={false} />
        <YAxis tick={{ fontSize: 11, fill: darkMode ? '#9ca3af' : '#6b7280' }} axisLine={false} tickLine={false} tickFormatter={(v) => `₹${(v/1000).toFixed(0)}K`} />
        <Tooltip contentStyle={contentStyle} labelStyle={labelStyle} itemStyle={itemStyle} formatter={(v: any) => [`₹${(v/1000).toFixed(0)}K`, 'Revenue']} />
        <Bar dataKey="revenue" name="Revenue" radius={[6, 6, 0, 0]}>
          {data.map((_, i) => (
            <Cell key={i} fill={`hsl(${245 + i * 5}, 70%, ${60 - i * 2}%)`} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
};

// ─── Backend-Integrated Charts ───────────────────────────────────────────────

// Application Status Donut — consumes applicationsStats.by_status
const APP_STATUS_COLORS: Record<string, string> = {
  NEW_APPLICATION:           '#0076eb',
  ASSET_ADDED:               '#8b5cf6',
  BUREAU_INITIATED:          '#3b82f6',
  BUREAU_COMPLETED:          '#06b6d4',
  OFFER_GENERATED:           '#10b981',
  OFFER_ACCEPTED:            '#22c55e',
  LOAN_AGREEMENT_GENERATED:  '#84cc16',
  PAYMENT_DETAILS_RECORDED:  '#f59e0b',
  REJECTED:                  '#ef4444',
  UNDERWRITING_APPROVED:     '#10b981',
  CREDIT_STATUS_CHECKED:     '#0076eb',
  GOLD_COLLECTED:            '#e5b83b',
  GOLD_DEPOSITED:            '#b45309',
  APPLICATION_REJECTED_BY_CPC: '#ef4444',
  APPLICATION_REJECTED_BY_CM:  '#dc2626',
};

export const ApplicationStatusChart: React.FC<{ data: any[]; darkMode: boolean }> = ({ data, darkMode }) => {
  const { contentStyle, labelStyle, itemStyle } = tt(darkMode);
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-40">
        <p className={`text-xs ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>No application data</p>
      </div>
    );
  }

  const total = data.reduce((s: number, d: any) => s + (d.count || 0), 0);
  const pieData = data.map((d: any, i: number) => ({
    name: d.status?.replace(/_/g, ' ') || 'Unknown',
    value: d.count || 0,
    color: APP_STATUS_COLORS[d.status] || `hsl(${i * 40}, 65%, 55%)`,
  }));

  return (
    <div className="flex items-center gap-4">
      <ResponsiveContainer width={140} height={140}>
        <PieChart>
          <Pie data={pieData} cx="50%" cy="50%" innerRadius={38} outerRadius={58} paddingAngle={2} dataKey="value" startAngle={90} endAngle={450}>
            {pieData.map((entry, i) => (
              <Cell key={i} fill={entry.color} stroke="none" />
            ))}
          </Pie>
          <Tooltip contentStyle={contentStyle} labelStyle={labelStyle} itemStyle={itemStyle} formatter={(v: any) => [v, '']} />
        </PieChart>
      </ResponsiveContainer>
      <div className="flex-1 space-y-1.5 overflow-hidden">
        {pieData.slice(0, 6).map((item, i) => (
          <div key={i} className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-1.5 min-w-0">
              <div className="w-2 h-2 rounded-sm flex-shrink-0" style={{ background: item.color }} />
              <span className={`text-xs truncate ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>{item.name}</span>
            </div>
            <div className="flex items-center gap-1 flex-shrink-0">
              <span className={`text-xs font-bold ${darkMode ? 'text-gray-200' : 'text-gray-700'}`}>{item.value}</span>
              <span className={`text-xs ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>({total > 0 ? Math.round((item.value / total) * 100) : 0}%)</span>
            </div>
          </div>
        ))}
        {pieData.length > 6 && (
          <p className={`text-xs ${darkMode ? 'text-gray-600' : 'text-gray-400'}`}>+{pieData.length - 6} more statuses</p>
        )}
      </div>
    </div>
  );
};

// Loan Type Donut Chart — consumes loansStats.by_loan_type
export const LoanTypeChart: React.FC<{ data: any[]; darkMode: boolean }> = ({ data, darkMode }) => {
  const { contentStyle, labelStyle, itemStyle } = tt(darkMode);
  
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-40">
        <p className={`text-xs ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>No loan type data</p>
      </div>
    );
  }

  const colors = ['#0076eb', '#e5b83b', '#3b82f6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444'];
  const total = data.reduce((sum, item) => sum + (item.count || 0), 0);
  
  const chartData = data.slice(0, 6).map((item, i) => ({
    name: item.loan_type?.replace(/_/g, ' ') || 'Unknown',
    value: item.count || 0,
    color: colors[i % colors.length]
  }));

  return (
    <div className="flex items-center gap-4">
      <ResponsiveContainer width={140} height={140}>
        <PieChart>
          <Pie 
            data={chartData} 
            cx="50%" cy="50%" 
            innerRadius={42} 
            outerRadius={62} 
            paddingAngle={3} 
            dataKey="value" 
            startAngle={90} 
            endAngle={450}
            stroke="none"
          >
            {chartData.map((entry, i) => (
              <Cell key={i} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip contentStyle={contentStyle} labelStyle={labelStyle} itemStyle={itemStyle} formatter={(v: any) => [v, 'Loans']} />
        </PieChart>
      </ResponsiveContainer>
      <div className="flex-1 space-y-2">
        {chartData.map((item, i) => (
          <div key={i} className="flex items-center justify-between">
            <div className="flex items-center gap-2 min-w-0">
              <div className="w-2.5 h-2.5 rounded-sm flex-shrink-0" style={{ background: item.color }} />
              <span className={`text-xs truncate ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>{item.name}</span>
            </div>
            <div className="flex items-center gap-1.5 flex-shrink-0">
              <span className={`text-xs font-bold ${darkMode ? 'text-gray-200' : 'text-gray-800'}`}>{item.value}</span>
              <span className={`text-[10px] ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>
                ({total > 0 ? Math.round((item.value / total) * 100) : 0}%)
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Tracked Lenders Chart — consumes applicationsStats.tracked_lenders (AXIS, ICICI, FEDERAL)
export const TrackedLendersChart: React.FC<{ tracked: Record<string, number>; darkMode: boolean }> = ({ tracked, darkMode }) => {
  const { contentStyle, labelStyle, itemStyle } = tt(darkMode);
  if (!tracked || Object.keys(tracked).length === 0) {
    return (
      <div className="flex items-center justify-center h-40">
        <p className={`text-xs ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>No lender data</p>
      </div>
    );
  }

  const lenderColors: Record<string, string> = {
    AXIS:    '#ef4444',
    ICICI:   '#f59e0b',
    FEDERAL: '#10b981',
  };

  const chartData = Object.entries(tracked).map(([name, count]) => ({ name, count, fill: lenderColors[name] || '#0076eb' }));

  return (
    <ResponsiveContainer width="100%" height={160}>
      <BarChart data={chartData} margin={{ top: 5, right: 10, bottom: 0, left: -20 }}>
        <XAxis dataKey="name" tick={{ fontSize: 11, fill: darkMode ? '#9ca3af' : '#6b7280' }} axisLine={false} tickLine={false} />
        <YAxis tick={{ fontSize: 11, fill: darkMode ? '#9ca3af' : '#6b7280' }} axisLine={false} tickLine={false} />
        <Tooltip contentStyle={contentStyle} labelStyle={labelStyle} itemStyle={itemStyle} formatter={(v: any) => [v, 'Applications']} />
        <Bar dataKey="count" name="Applications" radius={[6, 6, 0, 0]}>
          {chartData.map((entry, i) => (
            <Cell key={i} fill={entry.fill} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
};

// Monthly Loan Disbursals — consumes loansStats.monthly_disbursals
export const MonthlyDisbursalChart: React.FC<{ data: any[]; darkMode: boolean }> = ({ data, darkMode }) => {
  const { contentStyle, labelStyle, itemStyle } = tt(darkMode);
  const grid = darkMode ? '#374151' : '#f3f4f6';

  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-48">
        <p className={`text-xs ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>No disbursal data available</p>
      </div>
    );
  }

  const formatted = data.map((d: any) => ({
    month: d.month?.slice(0, 7) || d.month,
    count: d.count || 0,
    amount: Math.round((d.total_amount_inr || 0) / 100000), // convert to Lakhs
  }));

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={formatted} margin={{ top: 5, right: 10, bottom: 0, left: -10 }}>
        <defs>
          <linearGradient id="disbGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#10b981" stopOpacity={0.9} />
            <stop offset="95%" stopColor="#059669" stopOpacity={0.7} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke={grid} />
        <XAxis dataKey="month" tick={{ fontSize: 10, fill: darkMode ? '#9ca3af' : '#6b7280' }} axisLine={false} tickLine={false} />
        <YAxis yAxisId="left" tick={{ fontSize: 10, fill: darkMode ? '#9ca3af' : '#6b7280' }} axisLine={false} tickLine={false} />
        <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 10, fill: darkMode ? '#9ca3af' : '#6b7280' }} axisLine={false} tickLine={false} tickFormatter={(v) => `₹${v}L`} />
        <Tooltip
          contentStyle={contentStyle} labelStyle={labelStyle} itemStyle={itemStyle}
          formatter={(v: any, name: string) => name === 'amount' ? [`₹${v}L`, 'Disbursed (₹L)'] : [v, 'Loan Count']}
        />
        <Bar yAxisId="left" dataKey="count" name="Loan Count" fill="#0076eb" radius={[4, 4, 0, 0]} opacity={0.8} />
        <Bar yAxisId="right" dataKey="amount" name="amount" fill="url(#disbGrad)" radius={[4, 4, 0, 0]} />
        <Legend wrapperStyle={{ fontSize: '11px' }} />
      </BarChart>
    </ResponsiveContainer>
  );
};

// Monthly Leads and Applications Sourcing Area Chart
export const MonthlySourcingChart: React.FC<{ data: any[]; darkMode: boolean }> = ({ data, darkMode }) => {
  const { contentStyle, labelStyle, itemStyle } = tt(darkMode);
  const grid = darkMode ? '#374151' : '#f3f4f6';
  return (
    <ResponsiveContainer width="100%" height={220}>
      <AreaChart data={data} margin={{ top: 5, right: 10, bottom: 0, left: -10 }}>
        <defs>
          <linearGradient id="leadsGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#0076eb" stopOpacity={0.15} />
            <stop offset="95%" stopColor="#0076eb" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="appsGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#e5b83b" stopOpacity={0.15} />
            <stop offset="95%" stopColor="#e5b83b" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke={grid} />
        <XAxis dataKey="month" tick={{ fontSize: 10, fill: darkMode ? '#9ca3af' : '#6b7280' }} axisLine={false} tickLine={false} />
        <YAxis tick={{ fontSize: 10, fill: darkMode ? '#9ca3af' : '#6b7280' }} axisLine={false} tickLine={false} />
        <Tooltip contentStyle={contentStyle} labelStyle={labelStyle} itemStyle={itemStyle} />
        <Area type="monotone" dataKey="leads" name="Leads" stroke="#0076eb" strokeWidth={2} fill="url(#leadsGrad)" dot={false} />
        <Area type="monotone" dataKey="applications" name="Applications" stroke="#e5b83b" strokeWidth={2} fill="url(#appsGrad)" dot={false} />
        <Legend wrapperStyle={{ fontSize: '11px' }} />
      </AreaChart>
    </ResponsiveContainer>
  );
};
