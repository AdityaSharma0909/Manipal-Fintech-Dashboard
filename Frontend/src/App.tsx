import React, { useState, useCallback } from 'react';
import Header from './components/Header';
import NavTabs from './components/NavTabs';
import RightSidebar from './components/RightSidebar';
import Footer from './components/Footer';
import CustomerPanel from './components/CustomerPanel';
import OverviewTab from './components/tabs/OverviewTab';
import LeadsTab from './components/tabs/LeadsTab';
import ApplicationsTab from './components/tabs/ApplicationsTab';
import UsersTab from './components/tabs/UsersTab';
import AnalyticsTab from './components/tabs/AnalyticsTab';
import SettingsTab from './components/tabs/SettingsTab';
import { useLeadsData } from './hooks/useLeadsData';
import { useEmployeesData } from './hooks/useEmployeesData';
import { useDashboardStats } from './hooks/useDashboardStats';
import { exportExecutiveOverviewCSV, exportExecutiveOverviewPDF } from './utils/exportOverview';
import { TabId, Lead } from './types';


export type DateRangeOption = 'Today' | 'This Week' | 'This Month' | 'All Time' | 'Custom';

const App: React.FC = () => {
  const [darkMode, setDarkMode] = useState(false);
  const [activeTab, setActiveTab] = useState<TabId>('overview');
  const [selectedCustomer, setSelectedCustomer] = useState<Lead | null>(null);
  const [selectedRange, setSelectedRange] = useState<DateRangeOption>('All Time');
  const [customFromDate, setCustomFromDate] = useState<string>(() => {
    const d = new Date();
    d.setDate(d.getDate() - 30);
    return d.toISOString().split('T')[0];
  });
  const [customToDate, setCustomToDate] = useState<string>(() => new Date().toISOString().split('T')[0]);

  // Date range calculations
  const getTodayStr = () => new Date().toISOString().split('T')[0];
  const getStartOfWeekStr = () => {
    const d = new Date();
    const day = d.getDay();
    const diff = d.getDate() - day + (day === 0 ? -6 : 1);
    return new Date(d.setDate(diff)).toISOString().split('T')[0];
  };
  const getStartOfMonthStr = () => {
    const d = new Date();
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-01`;
  };

  let fromDate: string | undefined;
  let toDate: string | undefined = getTodayStr();

  if (selectedRange === 'Today') {
    fromDate = getTodayStr();
  } else if (selectedRange === 'This Week') {
    fromDate = getStartOfWeekStr();
  } else if (selectedRange === 'This Month') {
    fromDate = getStartOfMonthStr();
  } else if (selectedRange === 'All Time') {
    fromDate = undefined;
    toDate = undefined;
  } else if (selectedRange === 'Custom') {
    fromDate = customFromDate;
    toDate = customToDate;
  }

  const { leads, loading: leadsLoading, isPolling: leadsPolling, error: leadsError, totalCount: leadsCount, refetch: refetchLeads, lastSync: leadsSync } = useLeadsData();
  const { employees, loading: empLoading, isPolling: empPolling, error: empError, refetch: refetchEmps } = useEmployeesData();
  const { stats, loading: statsLoading, isPolling: statsPolling, refetch: refetchStats, apiLatencyMs, error: statsError } = useDashboardStats(
    fromDate,
    toDate
  );

  const error = leadsError || empError || statsError;
  const isPolling = leadsPolling || empPolling || statsPolling;
  const toggleDark = () => setDarkMode((d) => !d);

  const pinnedCustomers = leads.slice(0, 4);

  const handleRefreshAll = useCallback(() => {
    refetchLeads();
    refetchEmps();
    refetchStats();
  }, [refetchLeads, refetchEmps, refetchStats]);

  const renderTab = () => {
    switch (activeTab) {
      case 'leads':
        return (
          <LeadsTab
            leads={leads}
            stats={stats}
            darkMode={darkMode}
            loading={leadsLoading || statsLoading}
          />
        );
      case 'applications':
        return (
          <ApplicationsTab
            applications={stats?.applicationsList || []}
            stats={stats}
            darkMode={darkMode}
            loading={statsLoading}
          />
        );
      case 'employees':
        return (
          <UsersTab
            employees={employees}
            stats={stats}
            darkMode={darkMode}
            loading={empLoading || statsLoading}
          />
        );
      case 'analytics':
        return (
          <AnalyticsTab
            leads={leads}
            stats={stats}
            darkMode={darkMode}
            loading={leadsLoading || statsLoading}
          />
        );
      case 'settings':
        return <SettingsTab darkMode={darkMode} toggleDark={toggleDark} />;
      default:
        return (
          <OverviewTab
            leads={leads}
            stats={stats}
            darkMode={darkMode}
            loading={leadsLoading || statsLoading}
            totalCount={leadsCount}
            onSelectCustomer={setSelectedCustomer}
            selectedRange={selectedRange}
            customFromDate={customFromDate}
            customToDate={customToDate}
          />
        );
    }
  };


  return (
    <div
      className={`min-h-screen flex flex-col font-sans ${darkMode ? 'bg-gray-950 text-gray-100' : 'bg-[#F8FAFC] text-gray-900'}`}
      style={{ fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif" }}
    >
      {/* Header */}
      <Header
        darkMode={darkMode}
        toggleDark={toggleDark}
        notifications={3}
        selectedRange={selectedRange}
        setSelectedRange={setSelectedRange}
        customFromDate={customFromDate}
        setCustomFromDate={setCustomFromDate}
        customToDate={customToDate}
        setCustomToDate={setCustomToDate}
        isPolling={isPolling}
        lastSync={leadsSync}
        error={error}
        onRefresh={handleRefreshAll}
        onExport={() =>
          exportExecutiveOverviewCSV(
            stats,
            selectedRange,
            customFromDate,
            customToDate,
            stats?.kpiTrends,
            stats?.attentionItems,
            stats?.whatChangedItems
          )
        }
        onExportPDF={() =>
          exportExecutiveOverviewPDF(
            stats,
            selectedRange,
            customFromDate,
            customToDate,
            stats?.kpiTrends,
            stats?.attentionItems,
            stats?.whatChangedItems
          )
        }
      />


      {/* Nav Tabs */}
      <NavTabs activeTab={activeTab} setActiveTab={setActiveTab} darkMode={darkMode} />

      {/* Body */}
      <div className="flex flex-1 overflow-hidden">
        {/* Main Content */}
        <main className="flex-1 overflow-y-auto">
          {/* API Error Banner */}
          {error && (
            <div
              className={`mx-6 mt-4 px-4 py-3 rounded-xl border text-xs flex items-center gap-2 ${darkMode ? 'bg-rose-900/20 border-rose-500/30 text-rose-300' : 'bg-rose-50 border-rose-200 text-rose-700'
                }`}
            >
              <span>⚠️</span>
              <span>
                <strong>API Notice:</strong> {error}
              </span>
            </div>
          )}

          {/* Page Content */}
          <div className="p-6">
            {/* Page Title */}
            <div className="mb-5">
              <div className="flex items-center justify-between flex-wrap gap-3">
                <div>
                  <h1 className={`text-xl font-bold tracking-tight ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                    {activeTab === 'overview' && 'Executive Overview'}
                    {activeTab === 'leads' && 'Leads Dashboard'}
                    {activeTab === 'applications' && 'Applications Pipeline'}
                    {activeTab === 'employees' && 'Employees & Workforce'}
                    {activeTab === 'analytics' && 'Analytics Center'}
                    {activeTab === 'settings' && 'Dashboard Settings'}
                  </h1>
                  <p className={`text-xs mt-0.5 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                    Manipal Fintech Live API Dashboard ·{' '}
                    {new Date().toLocaleDateString('en-IN', {
                      weekday: 'long',
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                    })}
                    {(leadsLoading || statsLoading || empLoading) && (
                      <span className="ml-2 text-brand-blue animate-pulse">· Syncing live endpoints...</span>
                    )}
                  </p>
                </div>
                <div className="flex items-center gap-2 flex-wrap">
                  <div
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium border ${darkMode ? 'bg-gray-800 border-gray-700 text-gray-300' : 'bg-white border-gray-250 text-gray-600'
                      }`}
                  >
                    <div className={`w-1.5 h-1.5 rounded-full ${error ? 'bg-rose-500' : 'bg-emerald-500'} animate-pulse`} />
                    {error ? 'API Offline' : `Live Connected · ${stats?.overview.totalLeads || leadsCount} Leads`}
                  </div>
                </div>
              </div>
            </div>

            {/* Tab Content */}
            {renderTab()}
          </div>
        </main>

        {/* Right Sidebar - Temporarily disabled to give Executive Overview 100% full screen width */}
        {/*
        <div className="hidden xl:block">
          <RightSidebar
            darkMode={darkMode}
            lastSync={leadsSync}
            pinnedCustomers={pinnedCustomers}
            onSelectCustomer={setSelectedCustomer}
            onRefresh={handleRefreshAll}
          />
        </div>
        */}
      </div>

      {/* Footer */}
      <Footer darkMode={darkMode} lastSync={leadsSync} />

      {/* Customer Panel Drawer */}
      {selectedCustomer && (
        <CustomerPanel customer={selectedCustomer} onClose={() => setSelectedCustomer(null)} darkMode={darkMode} />
      )}
    </div>
  );
};

export default App;
