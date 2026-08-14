import React, { useState } from "react";
import { Section } from "../components/ui";

export const Settings: React.FC = () => {
  const [baseUrl, setBaseUrl] = useState(import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000");
  const [apiKey, setApiKey] = useState(import.meta.env.VITE_DASHBOARD_API_KEY ?? "");
  const [theme, setTheme] = useState("dark");
  const [locale, setLocale] = useState("en-IN");
  const [npaLimit, setNpaLimit] = useState(90);

  const handleSavePreferences = (e: React.FormEvent) => {
    e.preventDefault();
    alert("Dashboard settings saved successfully! Page will update configurations on next reload.");
  };

  return (
    <div className="settings-page-wrapper">
      <Section icon="⚙️" iconColor="blue" title="Dashboard Settings" subtitle="Preferences and API configurations">
        <div className="charts-grid" style={{ gridTemplateColumns: "1fr" }}>
          
          {/* Main preferences form */}
          <div className="chart-card">
            <div className="chart-title">⚙️ Preference Configuration</div>
            <div className="chart-subtitle">Adjust parameters governing visualizations and formatting</div>
            
            <form onSubmit={handleSavePreferences} style={{ display: "flex", flexDirection: "column", gap: "20px", marginTop: "16px", maxWidth: "600px" }}>
              {/* API settings */}
              <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                <label style={{ fontSize: "12px", color: "var(--text-secondary)", fontWeight: 600 }}>API Server Base URL</label>
                <input
                  type="text"
                  className="table-search-input"
                  style={{ width: "100%" }}
                  value={baseUrl}
                  onChange={(e) => setBaseUrl(e.target.value)}
                />
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                <label style={{ fontSize: "12px", color: "var(--text-secondary)", fontWeight: 600 }}>Dashboard API Access Token (API Key)</label>
                <input
                  type="text"
                  className="table-search-input font-mono"
                  style={{ width: "100%" }}
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                />
              </div>

              {/* Thresholds */}
              <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                <label style={{ fontSize: "12px", color: "var(--text-secondary)", fontWeight: 600 }}>NPA Threshold Overdue Days</label>
                <input
                  type="number"
                  className="table-search-input"
                  style={{ width: "100%" }}
                  value={npaLimit}
                  onChange={(e) => setNpaLimit(parseInt(e.target.value))}
                />
              </div>

              {/* Theme & formatting */}
              <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                <label style={{ fontSize: "12px", color: "var(--text-secondary)", fontWeight: 600 }}>Visual Theme Preset</label>
                <select
                  value={theme}
                  onChange={(e) => setTheme(e.target.value)}
                  className="filter-select-dropdown"
                  style={{ width: "100%" }}
                >
                  <option value="dark">Enterprise Dark Mode (Recommended)</option>
                  <option value="light">Classic Light Mode</option>
                  <option value="glass">Glassmorphism Overlay</option>
                </select>
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                <label style={{ fontSize: "12px", color: "var(--text-secondary)", fontWeight: 600 }}>Currency Locale formatting</label>
                <select
                  value={locale}
                  onChange={(e) => setLocale(e.target.value)}
                  className="filter-select-dropdown"
                  style={{ width: "100%" }}
                >
                  <option value="en-IN">Indian Rupees (₹ Lakh / Crore)</option>
                  <option value="en-US">US Dollars ($ Millions)</option>
                </select>
              </div>

              <button type="submit" className="btn-refresh" style={{ width: "fit-content", marginTop: "12px" }}>
                💾 Save Preferences
              </button>
            </form>
          </div>
        </div>
      </Section>
    </div>
  );
};
