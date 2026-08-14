import React, { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { useDashboard } from "../context/DashboardContext";
import { getTeam } from "../api/team";
import { KpiCard, Section, LoadingState, ErrorState, formatPct } from "../components/ui";
import { DataTable } from "../components/DataTable";
import type { ColumnDef } from "@tanstack/react-table";

export const Team: React.FC = () => {
  const { filters } = useDashboard();

  const { data, isLoading, isError } = useQuery({
    queryKey: ["team", filters],
    queryFn: () => getTeam(filters),
  });

  const branchSummary = useMemo(() => {
    if (!data || !data.conversions_per_branch.length) return null;

    const list = [...data.conversions_per_branch].sort((a, b) => b.conversion_rate_pct - a.conversion_rate_pct);
    const sumRate = list.reduce((acc, curr) => acc + curr.conversion_rate_pct, 0);

    return {
      topBranch: list[0],
      lowestBranch: list[list.length - 1],
      averageRate: sumRate / list.length,
    };
  }, [data]);

  if (isLoading) return <LoadingState />;
  if (isError || !data) return <ErrorState message="Failed to load team performance analytics." />;

  // 1. Officer Performance Columns
  const officerColumns: ColumnDef<any, any>[] = [
    {
      id: "Officer_Name",
      header: "Officer Name",
      accessorFn: (row: any) => `${row.first_name} ${row.last_name}`,
      cell: (info: any) => <strong style={{ color: "var(--text-primary)" }}>{info.getValue() as string}</strong>,
    },
    {
      id: "Role",
      header: "Designated Role",
      accessorKey: "role",
      cell: (info: any) => (
        <span className="badge-lending-partner">
          {info.getValue()?.toString().replace(/_/g, " ") || "Loan Officer"}
        </span>
      ),
    },
    {
      id: "Leads_Count",
      header: "Leads Sourced",
      accessorKey: "lead_count",
      cell: (info: any) => <span className="font-mono">{info.getValue()?.toLocaleString()}</span>,
    },
  ];

  // 2. Branch Performance Columns
  const branchColumns: ColumnDef<any, any>[] = [
    {
      id: "Branch_Name",
      header: "Branch",
      accessorKey: "branch_name",
      cell: (info: any) => <strong style={{ color: "var(--text-primary)" }}>{info.getValue() as string}</strong>,
    },
    {
      id: "Branch_Code",
      header: "Code",
      accessorKey: "branch_code",
      cell: (info: any) => <span className="font-mono">{info.getValue() as string}</span>,
    },
    {
      id: "Total_Applications",
      header: "Applications",
      accessorKey: "total_applications",
      cell: (info: any) => <span className="font-mono">{info.getValue()?.toLocaleString()}</span>,
    },
    {
      id: "Disbursed",
      header: "Disbursed Count",
      accessorKey: "disbursed",
      cell: (info: any) => <span className="font-mono text-emerald">{info.getValue()?.toLocaleString()}</span>,
    },
    {
      id: "Conversion_Rate",
      header: "Conversion Rate",
      accessorKey: "conversion_rate_pct",
      cell: (info: any) => (
        <strong className="text-blue">
          {info.getValue()}%
        </strong>
      ),
    },
  ];

  // 3. BM Performance Columns
  const bmColumns: ColumnDef<any, any>[] = [
    {
      id: "Manager_Name",
      header: "Branch Manager",
      accessorFn: (row: any) => `${row.first_name} ${row.last_name}`,
      cell: (info: any) => <strong style={{ color: "var(--text-primary)" }}>{info.getValue() as string}</strong>,
    },
    {
      id: "Approvals",
      header: "Approved Applications",
      accessorKey: "approved_count",
      cell: (info: any) => <span className="font-mono text-emerald">{info.getValue()?.toLocaleString()}</span>,
    },
  ];

  return (
    <div className="team-page-wrapper">
      <Section icon="👤" iconColor="amber" title="Team Performance" subtitle="Staff and Branch performance leaderboard">
        
        {/* Network performance indicators */}
        {branchSummary && (
          <div className="kpi-grid" style={{ marginBottom: 24 }}>
            <KpiCard
              icon="🥇"
              label="Top Performing Branch"
              value={branchSummary.topBranch.branch_name}
              color="emerald"
              badge={`${branchSummary.topBranch.conversion_rate_pct}% conversion`}
              badgeType="up"
            />
            <KpiCard
              icon="📉"
              label="Lowest Sourcing Branch"
              value={branchSummary.lowestBranch.branch_name}
              color="rose"
              badge={`${branchSummary.lowestBranch.conversion_rate_pct}% conversion`}
              badgeType="down"
            />
            <KpiCard
              icon="💹"
              label="Network Average Rate"
              value={formatPct(branchSummary.averageRate)}
              color="blue"
            />
          </div>
        )}

        {/* 1. Branch conversions table */}
        <div style={{ marginBottom: 32 }}>
          <div className="chart-title" style={{ marginBottom: "12px" }}>🏢 Branch Conversion Leaderboard</div>
          <div className="chart-subtitle" style={{ marginBottom: "16px" }}>Complete branch conversion rates based on loan requests</div>
          <DataTable
            columns={branchColumns}
            data={data.conversions_per_branch}
            searchPlaceholder="Search branch..."
            exportFileName="branch_performance_summary"
          />
        </div>

        {/* 2. Officers and BMs tables split row */}
        <div className="charts-grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(400px, 1fr))" }}>
          <div>
            <div className="chart-title" style={{ marginBottom: "12px" }}>📁 Officer Lead Acquisition</div>
            <div className="chart-subtitle" style={{ marginBottom: "16px" }}>Top active loan officers ranked by sourcing volume</div>
            <DataTable
              columns={officerColumns}
              data={data.leads_per_officer}
              searchPlaceholder="Search officer..."
              exportFileName="officer_leads_summary"
            />
          </div>

          <div>
            <div className="chart-title" style={{ marginBottom: "12px" }}>🏆 Branch Manager Approvals</div>
            <div className="chart-subtitle" style={{ marginBottom: "16px" }}>BM authorizations recorded at credit checkpoints</div>
            <DataTable
              columns={bmColumns}
              data={data.approvals_per_bm}
              searchPlaceholder="Search manager..."
              exportFileName="bm_approvals_summary"
            />
          </div>
        </div>
      </Section>
    </div>
  );
};
