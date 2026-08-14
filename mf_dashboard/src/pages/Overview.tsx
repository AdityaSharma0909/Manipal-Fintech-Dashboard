import React, { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { useDashboard } from "../context/DashboardContext";
import { getLeads } from "../api/leads";
import { getApplications } from "../api/applications";
import { getLoans } from "../api/loans";
import { getTeam } from "../api/team";
import {
  KpiCard,
  Section,
  LoadingState,
  ErrorState,
  formatInr,
  formatPct,
} from "../components/ui";
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

export const Overview: React.FC = () => {
  const { filters } = useDashboard();

  // Parallel React Query fetchers
  const leadsQuery = useQuery({
    queryKey: ["leads", filters],
    queryFn: () => getLeads(filters),
  });

  const appsQuery = useQuery({
    queryKey: ["applications", filters],
    queryFn: () => getApplications(filters),
  });

  const loansQuery = useQuery({
    queryKey: ["loans", filters],
    queryFn: () => getLoans(filters),
  });

  const teamQuery = useQuery({
    queryKey: ["team", filters],
    queryFn: () => getTeam(filters),
  });

  const isLoading =
    leadsQuery.isLoading ||
    appsQuery.isLoading ||
    loansQuery.isLoading ||
    teamQuery.isLoading;

  const isError =
    leadsQuery.isError ||
    appsQuery.isError ||
    loansQuery.isError ||
    teamQuery.isError;

  // ── Executive Insights engine (derived entirely from API responses) ──
  const insights = useMemo(() => {
    const list: string[] = [];
    if (!leadsQuery.data || !appsQuery.data || !loansQuery.data || !teamQuery.data) return list;

    const leads = leadsQuery.data;
    const apps = appsQuery.data;
    const loans = loansQuery.data;
    const team = teamQuery.data;

    // Insight 1: Unique leads ratio
    const totalLeads = leads.combined_total;
    const uniqueLeads = leads.classic_leads.total;
    if (totalLeads > 0) {
      const uniquePct = (uniqueLeads / totalLeads) * 100;
      list.push(
        `Unique leads represent ${uniquePct.toFixed(0)}% of total registered records (attribution via classic source channels).`
      );
    }

    // Insight 2: Lending partner approval rate comparison
    const AxisCount = apps.tracked_lenders["AXIS"] || 0;
    const FederalCount = apps.tracked_lenders["FEDERAL"] || 0;
    const IciciCount = apps.tracked_lenders["ICICI"] || 0;
    
    const partnerCounts = [
      { name: "Axis Bank", count: AxisCount },
      { name: "Federal Bank", count: FederalCount },
      { name: "ICICI Bank", count: IciciCount }
    ].sort((a, b) => b.count - a.count);

    if (partnerCounts[0] && partnerCounts[0].count > 0) {
      list.push(
        `${partnerCounts[0].name} is currently our most active lending partner with ${partnerCounts[0].count.toLocaleString()} registered application cases.`
      );
    }

    // Insight 3: Top conversion branch
    const topBranch = team.conversions_per_branch[0];
    if (topBranch && topBranch.total_applications > 0) {
      list.push(
        `Branch ${topBranch.branch_name} (${topBranch.branch_code}) leads operational network with a ${topBranch.conversion_rate_pct}% pipeline conversion rate.`
      );
    }

    // Insight 4: NPA concentration risk
    const npaCount = loans.npa_count;
    if (npaCount > 0) {
      const npaRate = (npaCount / (loans.total_loans || 1)) * 100;
      list.push(
        `Overdue risk flag: Portfolio reports ${npaCount} NPA accounts, representing a concentration rate of ${npaRate.toFixed(1)}%.`
      );
    } else {
      list.push("Portfolio health is optimal: No active accounts flagged under default / NPA status.");
    }

    return list;
  }, [leadsQuery.data, appsQuery.data, loansQuery.data, teamQuery.data]);

  if (isLoading) return <LoadingState />;
  if (isError) return <ErrorState message="Failed to load executive analytics." />;

  const leads = leadsQuery.data!;
  const apps = appsQuery.data!;
  const loans = loansQuery.data!;

  // Merge trends to show combined lead/app volume chart
  const combinedTrend = leads.monthly_trend.map((l) => {
    const matchingApp = apps.monthly_trend.find((a) => a.month === l.month);
    return {
      month: l.month,
      leads: l.count,
      applications: matchingApp ? matchingApp.count : 0,
    };
  });

  return (
    <div className="overview-page-wrapper">
      {/* ── KPI Grid ── */}
      <Section icon="🏠" iconColor="blue" title="Overview Statistics" subtitle="Real-time KPI metrics">
        <div className="kpi-grid" style={{ marginBottom: 24 }}>
          {/* Leads */}
          <KpiCard icon="📈" label="Total Lead Records" value={leads.combined_total.toLocaleString()} color="blue" />
          <KpiCard icon="🎯" label="Classic Source Leads" value={leads.classic_leads.total.toLocaleString()} color="violet" />
          <KpiCard icon="⚡" label="External Source Conversion" value={`${leads.external_leads.conversion_rate_pct}%`} color="amber" />
          
          {/* Applications */}
          <KpiCard icon="📋" label="Applications Registered" value={apps.total_applications.toLocaleString()} color="violet" />
          <KpiCard icon="🛡️" label="Bureau Approval Rate" value={formatPct(apps.bureau_approval_rate_pct)} color="blue" />
          
          {/* Loans */}
          <KpiCard icon="💰" label="Total Disbursed" value={formatInr(loans.total_disbursed_inr)} color="emerald" />
          <KpiCard icon="💼" label="Active Loans" value={loans.active_loans.toLocaleString()} color="emerald" />
          <KpiCard icon="⚠️" label="NPA Overdues (90d+)" value={loans.npa_count.toLocaleString()} color="rose" />
          <KpiCard icon="📥" label="Principal Remaining" value={formatInr(loans.total_principal_remaining_inr)} color="amber" />
        </div>
      </Section>

      {/* ── Executive Insights & Trends Row ── */}
      <div className="charts-grid" style={{ marginBottom: 24 }}>
        {/* Insights */}
        <div className="chart-card">
          <div className="chart-title">💡 Executive Insights</div>
          <div className="chart-subtitle">Calculated dynamically from real-time API telemetry</div>
          <div className="insights-list-box">
            {insights.map((insight, index) => (
              <div key={index} className="insight-bullet">
                <span className="bullet-point">🔸</span>
                <span className="insight-text">{insight}</span>
              </div>
            ))}
          </div>
        </div>

        {/* High-level trend */}
        <div className="chart-card">
          <div className="chart-title">Monthly Conversion Pipeline</div>
          <div className="chart-subtitle">Monthly volume comparison: Leads vs. Applications</div>
          <ResponsiveContainer width="100%" height={220}>
            <ComposedChart data={combinedTrend}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
              <XAxis dataKey="month" tick={{ fill: "#475569", fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "#475569", fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip formatter={(v: any) => v.toLocaleString()} />
              <Area type="monotone" dataKey="leads" fill="rgba(59, 130, 246, 0.12)" stroke="#3b82f6" strokeWidth={2} name="Leads" />
              <Bar dataKey="applications" fill="#8b5cf6" radius={[4, 4, 0, 0]} name="Applications" barSize={16} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
