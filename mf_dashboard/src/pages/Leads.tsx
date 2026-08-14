import React from "react";
import { useQuery } from "@tanstack/react-query";
import { useDashboard } from "../context/DashboardContext";
import { getLeads } from "../api/leads";
import { KpiCard, Section, LoadingState, ErrorState, ChartTooltip } from "../components/ui";
import { DataTable } from "../components/DataTable";
import type { ColumnDef } from "@tanstack/react-table";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

const COLORS = ["#3b82f6", "#8b5cf6", "#10b981", "#f59e0b", "#f43f5e", "#06b6d4"];

export const Leads: React.FC = () => {
  const { filters } = useDashboard();

  const { data, isLoading, isError } = useQuery({
    queryKey: ["leads", filters],
    queryFn: () => getLeads(filters),
  });

  if (isLoading) return <LoadingState />;
  if (isError || !data) return <ErrorState message="Failed to load lead analytics." />;

  const { classic_leads, external_leads, combined_total, monthly_trend } = data;

  // Columns for the TanStack Leads table
  const columns: ColumnDef<any, any>[] = [
    {
      id: "Lead_Channel",
      header: "Lead Channel",
      accessorKey: "source",
      cell: (info: any) => (
        <span className="badge-lending-partner">
          {info.getValue()?.toString().replace(/_/g, " ") || "Classic Source"}
        </span>
      ),
    },
    {
      id: "Status",
      header: "Status",
      accessorKey: "status",
      cell: (info: any) => (
        <span className="badge-status-stage">
          {info.getValue()?.toString().replace(/_/g, " ") || "New Lead"}
        </span>
      ),
    },
    {
      id: "Product_Scope",
      header: "Lending Scope",
      accessorKey: "lending_type",
      cell: (info: any) => <span style={{ fontWeight: 500 }}>{info.getValue()}</span>,
    },
    {
      id: "Attributed_Count",
      header: "Total Count",
      accessorKey: "count",
      cell: (info: any) => <span className="font-mono">{info.getValue()?.toLocaleString() || "1"}</span>,
    },
  ];

  // Map API responses to rows for the Data Table
  const tableData = [
    ...classic_leads.by_status.map((item) => ({
      source: "Classic Leads Pipeline",
      status: item.status,
      lending_type: "Individual Product",
      count: item.count,
    })),
    ...external_leads.by_status.map((item) => ({
      source: "External Lead Imports",
      status: item.status,
      lending_type: "Bulk Sourced Pool",
      count: item.count,
    })),
  ];

  // Derived Conversion funnel counts
  const funnelSteps = [
    { stage: "1. Lead Sourced", count: combined_total, rate: 100 },
    { stage: "2. Application Initiated", count: classic_leads.total, rate: combined_total > 0 ? Math.round((classic_leads.total / combined_total) * 100) : 0 },
    { stage: "3. Disbursed (External)", count: external_leads.disbursed, rate: external_leads.total > 0 ? Math.round((external_leads.disbursed / external_leads.total) * 100) : 0 },
  ];

  return (
    <div className="leads-page-wrapper">
      <Section icon="📈" iconColor="blue" title="Leads Analytics" subtitle="Attributions and conversion stages">
        {/* KPIs */}
        <div className="kpi-grid" style={{ marginBottom: 24 }}>
          <KpiCard icon="🎯" label="Combined Leads" value={combined_total.toLocaleString()} color="blue" />
          <KpiCard icon="📁" label="Classic Leads Sourced" value={classic_leads.total.toLocaleString()} color="violet" />
          <KpiCard icon="🌐" label="External Leads Sourced" value={external_leads.total.toLocaleString()} color="emerald" />
          <KpiCard icon="✅" label="External Disbursed" value={external_leads.disbursed.toLocaleString()} color="emerald" />
          <KpiCard icon="💹" label="Conversion Rate" value={`${external_leads.conversion_rate_pct}%`} color="amber" />
        </div>

        {/* Charts */}
        <div className="charts-grid" style={{ marginBottom: 24 }}>
          {/* Monthly trend area chart */}
          <div className="chart-card">
            <div className="chart-title">Lead Acquisition Trend</div>
            <div className="chart-subtitle">Acquired volume over last 6 months</div>
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={monthly_trend} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="leadsGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                <XAxis dataKey="month" tick={{ fill: "#475569", fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: "#475569", fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip content={<ChartTooltip />} />
                <Area type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={2} fill="url(#leadsGrad)" name="Leads" />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Product Type pie/donut */}
          <div className="chart-card">
            <div className="chart-title">Leads by Lending Channel</div>
            <div className="chart-subtitle">Direct app attributions</div>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={classic_leads.by_lending_type.slice(0, 6)}
                  dataKey="count"
                  nameKey="lending_type"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  innerRadius={50}
                  paddingAngle={3}
                >
                  {classic_leads.by_lending_type.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(v: any) => v.toLocaleString()} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Status Bar */}
          <div className="chart-card">
            <div className="chart-title">Lead Pipeline Status</div>
            <div className="chart-subtitle">Volume distribution by state</div>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={classic_leads.by_status.slice(0, 6)} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                <XAxis dataKey="status" tick={{ fill: "#475569", fontSize: 10 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: "#475569", fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip content={<ChartTooltip />} />
                <Bar dataKey="count" fill="#8b5cf6" radius={[4, 4, 0, 0]} name="Leads" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Funnel chart */}
          <div className="chart-card">
            <div className="chart-title">Operational Sourcing Funnel</div>
            <div className="chart-subtitle">Stages calculated from total entries</div>
            <div style={{ display: "flex", flexDirection: "column", gap: "12px", marginTop: "16px" }}>
              {funnelSteps.map((step, idx) => (
                <div key={idx} style={{ display: "flex", alignItems: "center", justifyItems: "space-between" }}>
                  <div style={{ flex: 1, minWidth: "160px" }}>
                    <div style={{ fontSize: "13px", fontWeight: 600 }}>{step.stage}</div>
                    <div style={{ fontSize: "11px", color: "var(--text-muted)" }}>{step.count.toLocaleString()} cases</div>
                  </div>
                  <div style={{ width: "120px", background: "rgba(255,255,255,0.04)", height: "8px", borderRadius: "4px", overflow: "hidden", margin: "0 12px" }}>
                    <div style={{ background: "var(--accent-emerald)", height: "100%", width: `${step.rate}%` }} />
                  </div>
                  <div style={{ fontSize: "13px", fontWeight: 700, color: "var(--accent-emerald)", width: "36px", textAlign: "right" }}>
                    {step.rate}%
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* TanStack Table */}
        <div style={{ marginTop: 24 }}>
          <div className="chart-title" style={{ marginBottom: "16px" }}>Pipeline Aggregations Table</div>
          <DataTable
            columns={columns}
            data={tableData}
            searchPlaceholder="Search pipeline status..."
            exportFileName="leads_pipeline"
          />
        </div>
      </Section>
    </div>
  );
};
