import React from "react";
import { useQuery } from "@tanstack/react-query";
import { useDashboard } from "../context/DashboardContext";
import { getLoans } from "../api/loans";
import { KpiCard, Section, LoadingState, ErrorState, ChartTooltip, formatInr } from "../components/ui";
import { DataTable } from "../components/DataTable";
import type { ColumnDef } from "@tanstack/react-table";
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
  BarChart,
} from "recharts";

const COLORS = ["#10b981", "#3b82f6", "#8b5cf6", "#f59e0b", "#f43f5e", "#06b6d4"];

export const Loans: React.FC = () => {
  const { filters } = useDashboard();

  const { data, isLoading, isError } = useQuery({
    queryKey: ["loans", filters],
    queryFn: () => getLoans(filters),
  });

  if (isLoading) return <LoadingState />;
  if (isError || !data) return <ErrorState message="Failed to load loan portfolio statistics." />;

  const {
    total_loans,
    active_loans,
    npa_count,
    npa_threshold_days,
    total_disbursed_inr,
    total_principal_remaining_inr,
    avg_loan_amount_inr,
    by_lender,
    by_loan_type,
    monthly_disbursals,
  } = data;

  const npaPct = total_loans > 0 ? (npa_count / total_loans) * 100 : 0;

  // Columns for the TanStack loans lender table
  const columns: ColumnDef<any, any>[] = [
    {
      id: "Rank",
      header: "#",
      accessorKey: "rank",
      cell: (info: any) => <span className="font-bold text-muted">{info.getValue()?.toString()}</span>,
    },
    {
      id: "Lender_Name",
      header: "Lending Institution",
      accessorKey: "lender_name",
      cell: (info: any) => <strong style={{ color: "var(--text-primary)" }}>{info.getValue()}</strong>,
    },
    {
      id: "Loan_Count",
      header: "Active Loans Count",
      accessorKey: "count",
      cell: (info: any) => <span className="font-mono">{info.getValue()?.toLocaleString()}</span>,
    },
    {
      id: "Total_Disbursed",
      header: "Total Sourced Disbursals",
      accessorKey: "total_disbursed",
      cell: (info: any) => (
        <span className="font-mono text-emerald">
          {formatInr(info.getValue() as number)}
        </span>
      ),
    },
  ];

  const tableData = by_lender.map((item, idx) => ({
    rank: idx + 1,
    lender_name: item.lender_name || "Self Lender / General Pool",
    count: item.count,
    total_disbursed: item.total_disbursed || 0,
  }));

  return (
    <div className="loans-page-wrapper">
      <Section icon="💰" iconColor="emerald" title="Loan Portfolio" subtitle="Portfolio metrics, NPA, outstanding balances">
        {/* KPIs */}
        <div className="kpi-grid" style={{ marginBottom: 24 }}>
          <KpiCard icon="💼" label="Total Sourced Loans" value={total_loans.toLocaleString()} color="emerald" />
          <KpiCard icon="🟢" label="Active Portfolio Accounts" value={active_loans.toLocaleString()} color="blue" />
          <KpiCard
            icon="⚠️"
            label={`NPA Overdues (>${npa_threshold_days}d)`}
            value={npa_count.toLocaleString()}
            color="rose"
            badge={`${npaPct.toFixed(1)}%`}
            badgeType={npaPct > 5 ? "down" : "up"}
          />
          <KpiCard icon="💸" label="Total Disbursed (INR)" value={formatInr(total_disbursed_inr)} color="emerald" />
          <KpiCard icon="📥" label="Outstanding Principal" value={formatInr(total_principal_remaining_inr)} color="amber" />
          <KpiCard icon="💹" label="Average Sourced Amount" value={formatInr(avg_loan_amount_inr)} color="violet" />
        </div>

        {/* NPA alerts banner if risk is high */}
        {npa_count > 0 && (
          <div className="error-card" style={{ marginBottom: 24, background: "rgba(244,63,94,0.05)", border: "1px solid rgba(244,63,94,0.15)" }}>
            <span>⚠️</span>
            <span style={{ fontSize: "13px", color: "var(--text-primary)" }}>
              <strong>NPA Overdue Alert:</strong> Portfolio currently contains <strong>{npa_count}</strong> flagged accounts exceeding the {npa_threshold_days}-day threshold. Total outstanding principal is <strong>{formatInr(total_principal_remaining_inr)}</strong>.
            </span>
          </div>
        )}

        <div className="charts-grid" style={{ marginBottom: 24 }}>
          {/* Monthly composed chart */}
          <div className="chart-card">
            <div className="chart-title">Monthly Disbursals Trend</div>
            <div className="chart-subtitle">Disbursed count and total amount in INR</div>
            <ResponsiveContainer width="100%" height={220}>
              <ComposedChart data={monthly_disbursals} margin={{ top: 5, right: 20, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="disbursalsGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                <XAxis dataKey="month" tick={{ fill: "#475569", fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis yAxisId="left" tick={{ fill: "#475569", fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis yAxisId="right" orientation="right" tick={{ fill: "#475569", fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={(v) => formatInr(v)} />
                <Tooltip
                  formatter={(value: any, name: any) =>
                    name === "Amount" ? formatInr(value) : value.toLocaleString()
                  }
                />
                <Area yAxisId="right" type="monotone" dataKey="total_amount_inr" fill="url(#disbursalsGrad)" stroke="#10b981" strokeWidth={2} name="Amount" />
                <Bar yAxisId="left" dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Count" opacity={0.75} barSize={16} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>

          {/* Product Portfolio bar chart */}
          <div className="chart-card">
            <div className="chart-title">Portfolio by Product Category</div>
            <div className="chart-subtitle">Count of sourced active loans</div>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={by_loan_type} margin={{ top: 5, right: 10, left: 0, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                <XAxis dataKey="loan_type" tick={{ fill: "#475569", fontSize: 10 }} angle={-20} textAnchor="end" axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: "#475569", fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip content={<ChartTooltip />} />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {by_loan_type.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Lender Sourcing table */}
        <div style={{ marginTop: 24 }}>
          <div className="chart-title" style={{ marginBottom: "16px" }}>Sourcing Partners Disbursal Summary</div>
          <DataTable
            columns={columns}
            data={tableData}
            searchPlaceholder="Search lending institutions..."
            exportFileName="sourced_loans_disbursals"
          />
        </div>
      </Section>
    </div>
  );
};
