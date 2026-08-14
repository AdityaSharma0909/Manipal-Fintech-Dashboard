import { useState } from "react";
import { QueryClientProvider, useQueryClient } from "@tanstack/react-query";
import { queryClient } from "./api/client";
import { DashboardProvider } from "./context/DashboardContext";
import { Sidebar } from "./components/Sidebar";
import type { ActivePage } from "./components/Sidebar";
import { Header } from "./components/Header";
import { RightPanel } from "./components/RightPanel";
import { Overview } from "./pages/Overview";
import { Leads } from "./pages/Leads";
import { Applications } from "./pages/Applications";
import { Loans } from "./pages/Loans";
import { Team } from "./pages/Team";
import { CustomerFootprint } from "./pages/CustomerFootprint";
import { Reports } from "./pages/Reports";
import { Settings } from "./pages/Settings";

import "./index.css";

function DashboardApp() {
  const [activePage, setActivePage] = useState<ActivePage>("overview");
  const [syncTime, setSyncTime] = useState<string>(new Date().toLocaleTimeString());
  const qc = useQueryClient();

  const handleRefresh = () => {
    qc.invalidateQueries();
    setSyncTime(new Date().toLocaleTimeString());
  };

  const handleQuickAction = (action: string) => {
    switch (action) {
      case "create_report":
        setActivePage("reports");
        break;
      case "export_excel":
        alert("Preparing Excel Export... Sourced data will be compiled and downloaded shortly.");
        break;
      case "share_view":
        const currentUrl = window.location.href;
        navigator.clipboard.writeText(currentUrl);
        alert(`Dashboard share link copied to clipboard: ${currentUrl}`);
        break;
      case "schedule_email":
        setActivePage("reports");
        alert("Directing to Reports Center to configure scheduled email deliveries.");
        break;
      case "download_pdf":
        alert("Branded PDF Report is being generated. Downloading document...");
        break;
      default:
        break;
    }
  };

  const renderActivePage = () => {
    switch (activePage) {
      case "leads":
        return <Leads />;
      case "applications":
        return <Applications />;
      case "loans":
        return <Loans />;
      case "team":
        return <Team />;
      case "footprint":
        return <CustomerFootprint />;
      case "reports":
        return <Reports />;
      case "settings":
        return <Settings />;
      case "overview":
      default:
        return <Overview />;
    }
  };

  const pageTitles: Record<ActivePage, string> = {
    overview: "Executive Overview",
    leads: "Leads Analytics",
    applications: "Applications Pipeline",
    loans: "Loan Portfolio",
    team: "Team Performance",
    footprint: "Customer Footprint — India",
    reports: "Reports Center",
    settings: "Dashboard Settings",
  };

  return (
    <div className="app">
      {/* Global Header */}
      <Header title={pageTitles[activePage]} onQuickAction={handleQuickAction} />

      {/* Horizontal Sub-Navigation Tab Bar */}
      <Sidebar activePage={activePage} setActivePage={setActivePage} />

      {/* Three Column / Main Viewport Grid */}
      <div className="main-viewport-container">
        <main className="main-content-column">
          {renderActivePage()}
        </main>
        
        {/* Right Actions & Insights Panel */}
        <RightPanel 
          onQuickAction={handleQuickAction} 
          syncTime={syncTime} 
          onRefresh={handleRefresh} 
        />
      </div>
    </div>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <DashboardProvider>
        <DashboardApp />
      </DashboardProvider>
    </QueryClientProvider>
  );
}
