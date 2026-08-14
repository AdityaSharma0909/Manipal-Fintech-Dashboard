import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getScheduledReports, toggleScheduledReport, deleteScheduledReport, createReport, getReports } from "../api/reports";
import { Section, LoadingState, ErrorState } from "../components/ui";

export const Reports: React.FC = () => {
  const queryClient = useQueryClient();

  const [reportName, setReportName] = useState("");
  const [selectedFormat, setSelectedFormat] = useState<"excel" | "csv" | "pdf">("pdf");
  const [selectedPages, setSelectedPages] = useState<string[]>(["overview"]);
  
  // Fetch reports list
  const { data: recentReports, isLoading: isReportsLoading } = useQuery({
    queryKey: ["reportsList"],
    queryFn: getReports,
  });

  // Fetch scheduled reports
  const { data: scheduledList, isLoading: isSchedLoading, isError } = useQuery({
    queryKey: ["scheduledReports"],
    queryFn: getScheduledReports,
  });

  // Mutations
  const createReportMutation = useMutation({
    mutationFn: createReport,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reportsList"] });
      setReportName("");
    },
  });

  const toggleMutation = useMutation({
    mutationFn: toggleScheduledReport,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["scheduledReports"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteScheduledReport,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["scheduledReports"] });
    },
  });

  const handlePageToggle = (page: string) => {
    if (selectedPages.includes(page)) {
      setSelectedPages(selectedPages.filter((p) => p !== page));
    } else {
      setSelectedPages([...selectedPages, page]);
    }
  };

  const handleBuildReport = (e: React.FormEvent) => {
    e.preventDefault();
    if (!reportName.trim()) return;

    createReportMutation.mutate({
      name: reportName,
      pages: selectedPages,
      metrics: ["leads", "applications", "loans", "team"],
      format: selectedFormat,
    });
  };

  if (isReportsLoading || isSchedLoading) return <LoadingState />;
  if (isError || !scheduledList) return <ErrorState message="Failed to load reports configuration." />;

  return (
    <div className="reports-page-wrapper">
      <Section icon="📊" iconColor="blue" title="Reports Center" subtitle="Saved configurations, output exports, scheduled alerts">
        
        {/* Upper layout split: Builder and recent items */}
        <div className="charts-grid" style={{ gridTemplateColumns: "1fr 2fr", marginBottom: 32 }}>
          {/* Builder */}
          <div className="chart-card">
            <div className="chart-title">📄 Report Builder</div>
            <div className="chart-subtitle">Generate exports matching selected configurations</div>
            <form onSubmit={handleBuildReport} style={{ display: "flex", flexDirection: "column", gap: "16px", marginTop: "16px" }}>
              <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                <label style={{ fontSize: "12px", color: "var(--text-secondary)" }}>Report Name</label>
                <input
                  type="text"
                  className="table-search-input"
                  style={{ width: "100%" }}
                  value={reportName}
                  onChange={(e) => setReportName(e.target.value)}
                  placeholder="e.g. Q3 Executive Sourcing"
                  required
                />
              </div>

              {/* Format selection */}
              <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                <label style={{ fontSize: "12px", color: "var(--text-secondary)" }}>Export Format</label>
                <select
                  value={selectedFormat}
                  onChange={(e: any) => setSelectedFormat(e.target.value)}
                  className="filter-select-dropdown"
                  style={{ width: "100%" }}
                >
                  <option value="pdf">PDF Document</option>
                  <option value="excel">Excel Workbook (.xlsx)</option>
                  <option value="csv">Comma-separated Values (.csv)</option>
                </select>
              </div>

              {/* Pages checklists */}
              <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                <label style={{ fontSize: "12px", color: "var(--text-secondary)" }}>Included Pages</label>
                {["overview", "leads", "applications", "loans", "team"].map((p) => (
                  <label key={p} className="column-checkbox-label">
                    <input
                      type="checkbox"
                      checked={selectedPages.includes(p)}
                      onChange={() => handlePageToggle(p)}
                    />
                    <span style={{ textTransform: "capitalize" }}>{p} Page</span>
                  </label>
                ))}
              </div>

              <button type="submit" className="btn-refresh" style={{ width: "100%", justifyContent: "center" }}>
                ⚡ Generate Report
              </button>
            </form>
          </div>

          {/* Recent list */}
          <div className="chart-card table-card" style={{ padding: 0 }}>
            <div className="table-header">
              <div>
                <div className="chart-title">Recent Reports Exports</div>
                <div className="chart-subtitle">Saved exports ready for download</div>
              </div>
            </div>
            <div style={{ overflowX: "auto" }}>
              <table>
                <thead>
                  <tr>
                    <th>Report Details</th>
                    <th>Pages Included</th>
                    <th>Format</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {recentReports?.map((r, idx) => (
                    <tr key={idx}>
                      <td style={{ fontWeight: 600 }}>{r.name}</td>
                      <td className="td-secondary" style={{ fontSize: "12px" }}>
                        {r.pages.join(", ")}
                      </td>
                      <td className="td-mono" style={{ textTransform: "uppercase" }}>{r.format}</td>
                      <td>
                        <span className="kpi-badge up">Ready</span>
                      </td>
                    </tr>
                  ))}
                  {(!recentReports || recentReports.length === 0) && (
                    <tr>
                      <td colSpan={4} style={{ textAlign: "center", padding: "40px", color: "var(--text-muted)" }}>
                        No recent reports generated. Use the builder on the left.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* 2. Scheduled reports section */}
        <div className="chart-card table-card" style={{ padding: 0 }}>
          <div className="table-header">
            <div>
              <div className="chart-title">Scheduled Email Reports</div>
              <div className="chart-subtitle">Automatic daily/weekly/monthly deliveries to stakeholders</div>
            </div>
          </div>
          <div style={{ overflowX: "auto" }}>
            <table>
              <thead>
                <tr>
                  <th>Report Name</th>
                  <th>Frequency</th>
                  <th>Recipients List</th>
                  <th>Last Sent</th>
                  <th>Next Run</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {scheduledList.map((s) => (
                  <tr key={s.id}>
                    <td style={{ fontWeight: 600 }}>{s.name}</td>
                    <td style={{ textTransform: "capitalize" }}>{s.frequency}</td>
                    <td className="td-secondary" style={{ fontSize: "11px" }}>{s.recipients}</td>
                    <td className="td-mono">{s.lastSent || "—"}</td>
                    <td className="td-mono">{s.nextRun}</td>
                    <td>
                      <span className={`kpi-badge ${s.status === "active" ? "up" : "neutral"}`}>
                        {s.status === "active" ? "Active" : "Paused"}
                      </span>
                    </td>
                    <td>
                      <div style={{ display: "flex", gap: "8px" }}>
                        <button
                          className="btn-paginate"
                          style={{ padding: "4px 8px", fontSize: "11px" }}
                          onClick={() => toggleMutation.mutate(s.id)}
                        >
                          {s.status === "active" ? "Pause" : "Resume"}
                        </button>
                        <button
                          className="btn-paginate"
                          style={{ padding: "4px 8px", fontSize: "11px", color: "var(--accent-rose)" }}
                          onClick={() => deleteMutation.mutate(s.id)}
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </Section>
    </div>
  );
};
