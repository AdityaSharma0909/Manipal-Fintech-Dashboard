import React from "react";

interface RightPanelProps {
  onQuickAction: (action: string) => void;
  syncTime: string;
  onRefresh: () => void;
}

export const RightPanel: React.FC<RightPanelProps> = ({
  onQuickAction,
  syncTime,
  onRefresh,
}) => {
  return (
    <aside className="right-panel-aside">
      {/* Quick Actions */}
      <div className="panel-card">
        <h3 className="panel-title">Quick Actions</h3>
        <div className="quick-actions-list">
          <button className="btn-quick-action" onClick={() => onQuickAction("create_report")}>
            <span className="action-icon">📝</span>
            <span className="action-label">Create Report</span>
          </button>
          <button className="btn-quick-action" onClick={() => onQuickAction("export_excel")}>
            <span className="action-icon">📤</span>
            <span className="action-label">Export Dashboard</span>
          </button>
          <button className="btn-quick-action" onClick={() => onQuickAction("share_view")}>
            <span className="action-icon">🔗</span>
            <span className="action-label">Share View</span>
          </button>
          <button className="btn-quick-action" onClick={() => onQuickAction("schedule_email")}>
            <span className="action-icon">📅</span>
            <span className="action-label">Schedule Email</span>
          </button>
          <button className="btn-quick-action" onClick={() => onQuickAction("download_pdf")}>
            <span className="action-icon">📄</span>
            <span className="action-label">Download PDF</span>
          </button>
        </div>
      </div>

      {/* Pinned Customers */}
      <div className="panel-card">
        <h3 className="panel-title">Pinned Customers</h3>
        <div className="pinned-customers-list">
          <div className="pinned-customer-item">
            <div className="avatar avatar-blue">EC</div>
            <div className="customer-info">
              <div className="customer-name">EcoFinance</div>
              <div className="customer-status">Starter</div>
            </div>
          </div>
          <div className="pinned-customer-item">
            <div className="avatar avatar-violet">NT</div>
            <div className="customer-info">
              <div className="customer-name">NovaTech Labs</div>
              <div className="customer-status">Starter</div>
            </div>
          </div>
          <div className="pinned-customer-item">
            <div className="avatar avatar-emerald">UA</div>
            <div className="customer-info">
              <div className="customer-name">Urban Analytics</div>
              <div className="customer-status">Starter</div>
            </div>
          </div>
          <div className="pinned-customer-item">
            <div className="avatar avatar-rose">EF</div>
            <div className="customer-info">
              <div className="customer-name">EcoFinance</div>
              <div className="customer-status">Pro</div>
            </div>
          </div>
        </div>
      </div>

      {/* Saved Views */}
      <div className="panel-card">
        <h3 className="panel-title">Saved Views</h3>
        <div className="saved-views-list">
          <div className="saved-view-item">
            <span className="view-icon">👁️</span>
            <span className="view-label">Enterprise Accounts</span>
            <span className="view-count">24</span>
          </div>
          <div className="saved-view-item">
            <span className="view-icon">👁️</span>
            <span className="view-label">At-Risk Customers</span>
            <span className="view-count">8</span>
          </div>
          <div className="saved-view-item">
            <span className="view-icon">👁️</span>
            <span className="view-label">Top AI Users</span>
            <span className="view-count">15</span>
          </div>
          <div className="saved-view-item">
            <span className="view-icon">👁️</span>
            <span className="view-label">Trial Conversions</span>
            <span className="view-count">31</span>
          </div>
        </div>
      </div>

      {/* Data Status */}
      <div className="panel-card status-card">
        <div className="status-header">
          <span className="status-dot"></span>
          <span className="status-text">Live Data Connection</span>
        </div>
        <div className="sync-time-label">Synced {syncTime}</div>
        <button className="btn-refresh" onClick={onRefresh}>
          🔄 Refresh Now
        </button>
      </div>
    </aside>
  );
};
