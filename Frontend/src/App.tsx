import React, { useState, useCallback } from 'react';
import Header from './components/Header';
import NavTabs from './components/NavTabs';
import RightSidebar from './components/RightSidebar';
import Footer from './components/Footer';
import CustomerPanel from './components/CustomerPanel';
import OverviewTab from './components/tabs/OverviewTab';
import UsersTab from './components/tabs/UsersTab';
import ActivityTab from './components/tabs/ActivityTab';
import CustomerInsightsTab from './components/tabs/CustomerInsightsTab';

import PerformanceTab from './components/tabs/PerformanceTab';
import AnalyticsTab from './components/tabs/AnalyticsTab';
import ReportsTab from './components/tabs/ReportsTab';
import SettingsTab from './components/tabs/SettingsTab';
import { useLeadsData } from './hooks/useLeadsData';
import { useDashboardStats } from './hooks/useDashboardStats';
import { TabId, Lead } from './types';

// Build ISO date string offset by `days` from today (negative = past)
const isoDateOffset = (days: number) => {
  const d = new Date();
  d.setDate(d.getDate() + days);
  return d.toISOString().split('T')[0];
};

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

  const { leads, loading, isPolling: leadsPolling, error, totalCount, refetch, lastSync } = useLeadsData();
  const { stats, loading: statsLoading, isPolling: statsPolling, refetch: refetchStats, apiLatencyMs } = useDashboardStats(
    fromDate,
    toDate
  );

  const isPolling = leadsPolling || statsPolling;
  const toggleDark = () => setDarkMode(d => !d);

  const pinnedCustomers = leads.slice(0, 4);

  const handleRefreshAll = useCallback(() => {
    refetch();
    refetchStats();
  }, [refetch, refetchStats]);

  const renderTab = () => {
    switch (activeTab) {
      case 'overview':
        return <OverviewTab leads={leads} stats={stats} darkMode={darkMode} loading={loading || statsLoading} totalCount={totalCount} onSelectCustomer={setSelectedCustomer} />;
      case 'users':
        return <UsersTab leads={leads} stats={stats} darkMode={darkMode} loading={loading || statsLoading} />;
      case 'activity':
        return <ActivityTab leads={leads} stats={stats} darkMode={darkMode} loading={loading || statsLoading} />;
      case 'insights':
        return <CustomerInsightsTab leads={leads} stats={stats} darkMode={darkMode} loading={loading} onSelectCustomer={setSelectedCustomer} />;
      case 'performance':
        return <PerformanceTab darkMode={darkMode} apiLatencyMs={apiLatencyMs} />;
      case 'analytics':
        return <AnalyticsTab leads={leads} stats={stats} darkMode={darkMode} loading={loading || statsLoading} />;
      case 'reports':
        return <ReportsTab darkMode={darkMode} />;

      case 'settings':
        return <SettingsTab darkMode={darkMode} toggleDark={toggleDark} />;
      default:
        return <OverviewTab leads={leads} stats={stats} darkMode={darkMode} loading={loading || statsLoading} totalCount={totalCount} onSelectCustomer={setSelectedCustomer} />;
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
        lastSync={lastSync}
      />

      {/* Nav Tabs */}
      <NavTabs activeTab={activeTab} setActiveTab={setActiveTab} darkMode={darkMode} />

      {/* Body */}
      <div className="flex flex-1 overflow-hidden">
        {/* Main Content */}
        <main className="flex-1 overflow-y-auto">
          {/* API Error Banner */}
          {error && (
            <div className={`mx-6 mt-4 px-4 py-3 rounded-xl border text-xs flex items-center gap-2 ${
              darkMode ? 'bg-rose-900/20 border-rose-500/30 text-rose-300' : 'bg-rose-50 border-rose-200 text-rose-700'
            }`}>
              <span>⚠️</span>
              <span><strong>API Error:</strong> Unable to load live database responses ({error}). Please check Django server status and API key in Settings.</span>
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
                    {activeTab === 'users' && 'User Analytics'}
                    {activeTab === 'activity' && 'Platform Activity'}
                    {activeTab === 'insights' && 'Customer Insights'}

                    {activeTab === 'performance' && 'Platform Performance'}
                    {activeTab === 'analytics' && 'Analytics Center'}
                    {activeTab === 'reports' && 'Report Library'}
                    {activeTab === 'settings' && 'Dashboard Settings'}
                  </h1>
                  <p className={`text-xs mt-0.5 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                    Manipal Fintech AI Platform · {new Date().toLocaleDateString('en-IN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
                    {(loading || statsLoading) && <span className="ml-2 text-brand-blue animate-pulse">· Syncing data...</span>}
                  </p>
                </div>
                <div className="flex items-center gap-2 flex-wrap">
                  <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium border ${
                    darkMode ? 'bg-gray-800 border-gray-700 text-gray-300' : 'bg-white border-gray-250 text-gray-600'
                  }`}>
                    <div className={`w-1.5 h-1.5 rounded-full ${error ? 'bg-rose-500' : 'bg-emerald-500'} animate-pulse`} />
                    {error ? 'API Offline' : `Live · ${totalCount} records`}
                  </div>
                </div>
              </div>
            </div>

            {/* Tab Content */}
            {renderTab()}
          </div>
        </main>

        {/* Right Sidebar */}
        <div className="hidden xl:block">
          <RightSidebar
            darkMode={darkMode}
            lastSync={lastSync}
            pinnedCustomers={pinnedCustomers}
            onSelectCustomer={setSelectedCustomer}
            onRefresh={handleRefreshAll}
          />
        </div>
      </div>

      {/* Footer */}
      <Footer darkMode={darkMode} lastSync={lastSync} />

      {/* Customer Panel Drawer */}
      {selectedCustomer && (
        <CustomerPanel
          customer={selectedCustomer}
          onClose={() => setSelectedCustomer(null)}
          darkMode={darkMode}
        />
      )}


    </div>
  );
};

export default App;
