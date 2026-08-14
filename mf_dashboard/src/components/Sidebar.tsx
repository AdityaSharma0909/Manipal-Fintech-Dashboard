import React from "react";

export type ActivePage =
  | "overview"
  | "leads"
  | "applications"
  | "loans"
  | "team"
  | "footprint"
  | "reports"
  | "settings";

interface SidebarProps {
  activePage: ActivePage;
  setActivePage: (page: ActivePage) => void;
}

const MENU_ITEMS: Array<{ id: ActivePage; label: string; icon: string }> = [
  { id: "overview",     label: "Overview",            icon: "🏠" },
  { id: "leads",        label: "Leads",               icon: "📈" },
  { id: "applications", label: "Applications",        icon: "📋" },
  { id: "loans",        label: "Loans Portfolio",     icon: "💰" },
  { id: "team",         label: "Team Performance",    icon: "👤" },
  { id: "footprint",    label: "Customer Footprint",  icon: "🇮🇳" },
  { id: "reports",      label: "Reports Center",      icon: "📊" },
  { id: "settings",     label: "Settings",            icon: "⚙️" },
];

export const Sidebar: React.FC<SidebarProps> = ({ activePage, setActivePage }) => {
  return (
    <nav className="horizontal-sub-nav">
      <div className="nav-container">
        {MENU_ITEMS.map((item) => (
          <button
            key={item.id}
            id={`nav-item-${item.id}`}
            onClick={() => setActivePage(item.id)}
            className={`sub-nav-button ${activePage === item.id ? "active" : ""}`}
          >
            <span className="sub-nav-icon">{item.icon}</span>
            <span className="sub-nav-label">{item.label}</span>
          </button>
        ))}
      </div>
    </nav>
  );
};
