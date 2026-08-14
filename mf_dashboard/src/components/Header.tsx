import React, { useState } from "react";
import { useDashboard } from "../context/DashboardContext";
import type { DatePreset } from "../context/DashboardContext";
import { useQuery } from "@tanstack/react-query";
import { getTeam } from "../api/team";

interface HeaderProps {
  title: string;
  onQuickAction?: (action: string) => void;
}

export const Header: React.FC<HeaderProps> = ({ title, onQuickAction }) => {
  const {
    preset,
    setPreset,
    fromDate,
    setFromDate,
    toDate,
    setToDate,
    branchId,
    setBranchId,
    searchQuery,
    setSearchQuery,
    resetAllFilters,
  } = useDashboard();

  const [tempFromDate, setTempFromDate] = useState(fromDate);
  const [tempToDate, setTempToDate] = useState(toDate);
  const [showQuickMenu, setShowQuickMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);

  // Fetch branches dynamically from Team Conversions endpoint to populate the branch filter
  const { data: teamData } = useQuery({
    queryKey: ["team", fromDate, toDate],
    queryFn: () => getTeam({ fromDate, toDate }),
  });

  const handlePresetChange = (p: DatePreset) => {
    setPreset(p);
  };

  const handleApplyCustomDates = (e: React.FormEvent) => {
    e.preventDefault();
    setPreset("custom");
    setFromDate(tempFromDate);
    setToDate(tempToDate);
  };

  const activeFiltersCount =
    (branchId ? 1 : 0) + (preset === "custom" ? 1 : 0) + (searchQuery ? 1 : 0);

  return (
    <header className="global-header">
      {/* Upper row: branding and profile actions */}
      <div className="header-top-row">
        <div className="header-branding">
          <img src="/Manipal-Fintech_New-Logo.png" alt="Manipal Fintech Logo" className="brand-logo-img" />
          <div className="vertical-divider" />
          <div>
            <h1 className="header-page-title">{title}</h1>
            <span className="org-badge">🏢 Manipal Fintech Ltd</span>
          </div>
        </div>

        {/* Global actions */}
        <div className="header-global-actions">
          {/* Global search */}
          <div className="global-search-container">
            <span className="search-icon">🔍</span>
            <input
              type="text"
              placeholder="Search dashboards..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="global-search-input"
            />
          </div>

          {/* Notification Center */}
          <div className="action-menu-container">
            <button
              className="btn-header-action"
              onClick={() => setShowNotifications(!showNotifications)}
              title="Notifications"
            >
              🔔 <span className="notification-dot" />
            </button>
            {showNotifications && (
              <div className="action-dropdown notification-dropdown">
                <div className="dropdown-header">System Notifications</div>
                <div className="notification-item unread">
                  <div className="notification-title">NPA Overdue Alert</div>
                  <div className="notification-desc">Branch Pune reports day-past-dues exceeds 90 days.</div>
                </div>
                <div className="notification-item">
                  <div className="notification-title">Weekly Report Prepared</div>
                  <div className="notification-desc">Your scheduled executive summary is ready.</div>
                </div>
              </div>
            )}
          </div>

          {/* User profile */}
          <div className="user-profile-badge">
            <div className="user-avatar">AD</div>
            <div className="user-info-text">
              <span className="user-name">Aditya Dwivedi</span>
              <span className="user-role">Chief Business Officer</span>
            </div>
          </div>

          {/* Quick Actions Dropdown */}
          <div className="action-menu-container">
            <button
              className="btn-quick-actions"
              onClick={() => setShowQuickMenu(!showQuickMenu)}
            >
              ⚡ Quick Actions 🔽
            </button>
            {showQuickMenu && (
              <div className="action-dropdown quick-dropdown">
                <button
                  onClick={() => {
                    onQuickAction?.("create_report");
                    setShowQuickMenu(false);
                  }}
                >
                  📄 Create Report
                </button>
                <button
                  onClick={() => {
                    onQuickAction?.("export_excel");
                    setShowQuickMenu(false);
                  }}
                >
                  📈 Export Excel
                </button>
                <button
                  onClick={() => {
                    onQuickAction?.("share_view");
                    setShowQuickMenu(false);
                  }}
                >
                  🔗 Share Dashboard View
                </button>
                <button
                  onClick={() => {
                    onQuickAction?.("schedule_email");
                    setShowQuickMenu(false);
                  }}
                >
                  📅 Schedule Email Report
                </button>
                <button
                  onClick={() => {
                    onQuickAction?.("download_pdf");
                    setShowQuickMenu(false);
                  }}
                >
                  💾 Download PDF Report
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Lower row: filters and date presets */}
      <div className="header-filters-row">
        {/* Preset selectors */}
        <div className="date-presets-wrapper">
          <button
            className={`preset-tab ${preset === "today" ? "active" : ""}`}
            onClick={() => handlePresetChange("today")}
          >
            Today
          </button>
          <button
            className={`preset-tab ${preset === "week" ? "active" : ""}`}
            onClick={() => handlePresetChange("week")}
          >
            This Week
          </button>
          <button
            className={`preset-tab ${preset === "month" ? "active" : ""}`}
            onClick={() => handlePresetChange("month")}
          >
            This Month
          </button>
        </div>

        {/* Custom date range selection */}
        <form onSubmit={handleApplyCustomDates} className="custom-date-form">
          <input
            type="date"
            className="date-filter-input"
            value={tempFromDate}
            onChange={(e) => setTempFromDate(e.target.value)}
            title="Start date"
          />
          <span className="date-separator">to</span>
          <input
            type="date"
            className="date-filter-input"
            value={tempToDate}
            onChange={(e) => setTempToDate(e.target.value)}
            title="End date"
          />
          <button type="submit" className="btn-date-apply">
            Apply
          </button>
        </form>

        <div className="header-separator" />

        {/* Reusable Branch filter list */}
        <div className="filter-select-wrapper">
          <span className="filter-select-label">Branch:</span>
          <select
            value={branchId}
            onChange={(e) => setBranchId(e.target.value)}
            className="filter-select-dropdown"
          >
            <option value="">All Branches</option>
            {teamData?.conversions_per_branch.map((b) => (
              <option key={b.branch_id} value={b.branch_id}>
                {b.branch_name} ({b.branch_code})
              </option>
            ))}
          </select>
        </div>

        {/* Active Filter Chips */}
        {activeFiltersCount > 0 && (
          <div className="filter-chips-container">
            {branchId && (
              <span className="filter-chip">
                Branch:{" "}
                {teamData?.conversions_per_branch.find((b) => b.branch_id === branchId)
                  ?.branch_name || branchId}
              </span>
            )}
            {preset === "custom" && <span className="filter-chip">Custom Dates</span>}
            {searchQuery && <span className="filter-chip">Query: {searchQuery}</span>}
            <button className="btn-reset-filters" onClick={resetAllFilters}>
              Reset All Filters
            </button>
          </div>
        )}
      </div>
    </header>
  );
};
