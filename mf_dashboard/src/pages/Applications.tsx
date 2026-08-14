import React from "react";
import { useQuery } from "@tanstack/react-query";
import { useDashboard } from "../context/DashboardContext";
import { getApplications } from "../api/applications";
import { KpiCard, Section, LoadingState, ErrorState, ChartTooltip, formatPct } from "../components/ui";
import { DataTable } from "../components/DataTable";
import type { ColumnDef } from "@tanstack/react-table";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  PieChart,
  Pie,
  Cell,
} from "recharts";

const COLORS = ["#8b5cf6", "#3b82f6", "#10b981", "#f59e0b", "#f43f5e", "#06b6d4"];

export const Applications: React.FC = () => {
  const { filters } = useDashboard();

  const { data, isLoading, isError } = useQuery({
    queryKey: ["applications", filters],
    queryFn: () => getApplications(filters),
  });

  if (isLoading) return <LoadingState />;
  if (isError || !data) return <ErrorState message="Failed to load applications analytics." />;

  const {
    total_applications,
    disbursed_count,
    bureau_approval_rate_pct,
    by_status,
    by_loan_type,
    by_lender,
    tracked_lenders,
    monthly_trend,
  } = data;

  // Render lender table data dynamically from response
  const lenderRows = by_lender.map((l) => {
    const isTracked = ["AXIS", "ICICI", "FEDERAL"].some((k) =>
      l.lender_name.toUpperCase().includes(k)
    );
    return {
      partner: l.lender_name,
      applications: l.count,
      bureauApproved: Math.round(l.count * (bureau_approval_rate_pct / 100)),
      approved: Math.round(l.count * (disbursed_count / (total_applications || 1))),
      rate: isTracked ? bureau_approval_rate_pct : 0,
    };
  });

  const columns: ColumnDef<any, any>[] = [
    {
      id: "Partner",
      header: "Lending Partner",
      accessorKey: "partner",
      cell: (info: any) => <strong style={{ color: "var(--text-primary)" }}>{info.getValue()}</strong>,
    },
    {
      id: "Applications_Count",
      header: "Applications Sourced",
      accessorKey: "applications",
      cell: (info: any) => <span className="font-mono">{info.getValue()?.toLocaleString()}</span>,
    },
    {
      id: "Bureau_Approved",
      header: "Bureau Approved",
      accessorKey: "bureauApproved",
      cell: (info: any) => <span className="font-mono">{info.getValue()?.toLocaleString()}</span>,
    },
    {
      id: "Approved",
      header: "Approved (Disbursed)",
      accessorKey: "approved",
      cell: (info: any) => <span className="font-mono text-emerald">{info.getValue()?.toLocaleString()}</span>,
    },
    {
      id: "Approval_Rate",
      header: "Base Approval Rate",
      accessorKey: "rate",
      cell: (info: any) => (
        <span className="font-bold text-blue">
          {info.getValue() ? `${info.getValue()}%` : "—"}
        </span>
      ),
    },
  ];

  // Map application stages for funnel pipeline
  const pipelineStages = by_status.slice(0, 5).map((item) => ({
    stage: item.status.replace(/_/g, " "),
    count: item.count,
    percentage: total_applications > 0 ? Math.round((item.count / total_applications) * 100) : 0,
  }));

  return (
    <div className="applications-page-wrapper">
      <Section icon="📋" iconColor="violet" title="Applications Pipeline" subtitle="Detailed loan requests status">
        {/* KPIs */}
        <div className="kpi-grid" style={{ marginBottom: 24 }}>
          <KpiCard icon="📁" label="Total Applications Sourced" value={total_applications.toLocaleString()} color="violet" />
          <KpiCard icon="✅" label="Disbursals Recorded" value={disbursed_count.toLocaleString()} color="emerald" />
          <KpiCard icon="🛡️" label="Bureau Approval Rate" value={formatPct(bureau_approval_rate_pct)} color="blue" />
          <KpiCard
            icon="📊"
            label="Disbursal Conversion"
            value={formatPct(total_applications > 0 ? (disbursed_count / total_applications) * 100 : 0)}
            color="amber"
          />
        </div>

        {/* Dynamic Partner Breakdown widgets */}
        <div className="chart-card" style={{ marginBottom: 24 }}>
          <div className="chart-title">🏦 Key Sourcing Partners Overview</div>
          <div className="chart-subtitle">Direct application volumes routed to banking desks</div>
          <div className="lender-grid" style={{ marginTop: 16 }}>
            {Object.entries(tracked_lenders).map(([name, count]) => (
              <div key={name} className="lender-card">
                <div className="lender-name">{name} BANK</div>
                <div className="lender-count">{count.toLocaleString()}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="charts-grid" style={{ marginBottom: 24 }}>
          {/* Trend */}
          <div className="chart-card">
            <div className="chart-title">Applications Monthly Flow</div>
            <div className="chart-subtitle">Monthly application volume trend</div>
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={monthly_trend} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                <XAxis dataKey="month" tick={{ fill: "#475569", fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: "#475569", fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip content={<ChartTooltip />} />
                <Line type="monotone" dataKey="count" stroke="#8b5cf6" strokeWidth={2} dot={{ fill: "#8b5cf6", r: 3 }} name="Applications" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Product Type pie/donut */}
          <div className="chart-card">
            <div className="chart-title">Applications by Lending Category</div>
            <div className="chart-subtitle">Share of product types</div>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={by_loan_type.slice(0, 6)}
                  dataKey="count"
                  nameKey="application_loan_type"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  innerRadius={50}
                  paddingAngle={3}
                >
                  {by_loan_type.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(v: any) => v.toLocaleString()} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Sourcing funnel map */}
          <div className="chart-card" style={{ gridColumn: "1 / -1" }}>
            <div className="chart-title">Application Sourcing Stages</div>
            <div className="chart-subtitle">Current volume metrics at key pipeline milestones</div>
            <div style={{ display: "flex", flexDirection: "column", gap: "14px", marginTop: "16px" }}>
              {pipelineStages.map((stage, idx) => (
                <div key={idx} style={{ display: "flex", alignItems: "center" }}>
                  <div style={{ width: "240px", fontSize: "13px", fontWeight: 600 }}>{stage.stage}</div>
                  <div style={{ flex: 1, background: "rgba(255,255,255,0.04)", height: "10px", borderRadius: "5px", overflow: "hidden", margin: "0 16px" }}>
                    <div style={{ background: "var(--accent-violet)", height: "100%", width: `${stage.percentage}%` }} />
                  </div>
                  <div style={{ width: "100px", textAlign: "right" }}>
                    <span style={{ fontSize: "14px", fontWeight: 700 }}>{stage.count.toLocaleString()}</span>
                    <span style={{ fontSize: "11px", color: "var(--text-muted)", marginLeft: "6px" }}>({stage.percentage}%)</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Sourcing table */}
        <div style={{ marginTop: 24 }}>
          <div className="chart-title" style={{ marginBottom: "16px" }}>Lending Partners Performance Table</div>
          <DataTable
            columns={columns}
            data={lenderRows}
            searchPlaceholder="Search lending partners..."
            exportFileName="lending_partners_applications"
          />
        </div>
      </Section>
    </div>
  );
};
