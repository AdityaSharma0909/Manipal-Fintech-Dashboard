import React, { useState } from 'react';
import { FileText, Download, Share2, Mail, FileDown, Pin, Eye, RefreshCw } from 'lucide-react';
import { Lead } from '../types';

interface RightSidebarProps {
  darkMode: boolean;
  lastSync: Date | null;
  pinnedCustomers: Lead[];
  onSelectCustomer: (lead: Lead) => void;
  onRefresh: () => void;
}

const savedViews = [
  { name: 'Enterprise Accounts', count: 24 },
  { name: 'At-Risk Customers', count: 8 },
  { name: 'Top AI Users', count: 15 },
  { name: 'Trial Conversions', count: 31 },
];

const RightSidebar: React.FC<RightSidebarProps> = ({ darkMode, lastSync, pinnedCustomers, onSelectCustomer, onRefresh }) => {
  const [activeSavedView, setActiveSavedView] = useState<string | null>(null);

  const handleActionClick = (label: string) => {
    switch (label) {
      case 'Create Report':
        alert('Report generation started. You will be notified when it is ready.');
        break;
      case 'Export Dashboard':
        alert('Dashboard exported successfully to CSV format.');
        break;
      case 'Share View':
        navigator.clipboard.writeText(window.location.href).then(() => {
          alert('Dashboard link copied to clipboard!');
        }).catch(() => {
          alert('Failed to copy link to clipboard.');
        });
        break;
      case 'Schedule Email':
        const email = prompt('Enter email address to schedule report delivery:');
        if (email) alert(`Report scheduled successfully for ${email}`);
        break;
      case 'Download PDF':
        window.print();
        break;
      default:
        break;
    }
  };

  const actions = [
    { icon: <FileText size={14} />, label: 'Create Report', color: 'text-brand-blue' },
    { icon: <Download size={14} />, label: 'Export Dashboard', color: 'text-emerald-500' },
    { icon: <Share2 size={14} />, label: 'Share View', color: 'text-blue-500' },
    { icon: <Mail size={14} />, label: 'Schedule Email', color: 'text-amber-500' },
    { icon: <FileDown size={14} />, label: 'Download PDF', color: 'text-rose-500' },
  ];

  return (
    <aside className={`w-60 flex-shrink-0 border-l ${darkMode ? 'border-gray-700 bg-gray-900/50' : 'border-gray-100 bg-white/50'} backdrop-blur-sm overflow-y-auto`}>
      <div className="p-4 space-y-5">
        {/* Quick Actions - Temporarily disabled */}
        {/*
        <div>
          <h4 className={`text-xs font-semibold uppercase tracking-wider mb-3 ${darkMode ? 'text-gray-400' : 'text-gray-400'}`}>Quick Actions</h4>
          <div className="space-y-1">
            {actions.map((action) => (
              <button
                key={action.label}
                onClick={() => handleActionClick(action.label)}
                className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-medium transition-all text-left ${
                  darkMode ? 'text-gray-300 hover:bg-gray-800' : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                <span className={action.color}>{action.icon}</span>
                {action.label}
              </button>
            ))}
          </div>
        </div>

        <div className={`h-px ${darkMode ? 'bg-gray-700' : 'bg-gray-100'}`} />
        */}

        {/* Pinned Customers - Temporarily disabled */}
        {/*
        <div>
          <h4 className={`text-xs font-semibold uppercase tracking-wider mb-3 ${darkMode ? 'text-gray-400' : 'text-gray-400'}`}>Pinned Customers</h4>
          <div className="space-y-2">
            {pinnedCustomers.slice(0, 4).map((customer) => (
              <button
                key={customer.id}
                onClick={() => onSelectCustomer(customer)}
                className={`w-full flex items-center gap-2 px-2 py-2 rounded-xl text-left transition-all hover:scale-[1.02] ${
                  darkMode ? 'hover:bg-gray-800' : 'hover:bg-gray-50'
                }`}
              >
                <div
                  className="w-7 h-7 rounded-lg text-white text-xs font-bold flex items-center justify-center flex-shrink-0"
                  style={{ background: `hsl(${((typeof customer.id === 'number' ? customer.id : String(customer.id).split('').reduce((acc, c) => acc + c.charCodeAt(0), 0)) * 47) % 360}, 65%, 55%)` }}
                >
                  {customer.name?.slice(0, 1)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className={`text-xs font-medium truncate ${darkMode ? 'text-gray-200' : 'text-gray-700'}`}>{customer.organization}</p>
                  <p className={`text-xs truncate ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>{customer.plan}</p>
                </div>
                <Pin size={10} className={darkMode ? 'text-gray-600' : 'text-gray-300'} />
              </button>
            ))}
          </div>
        </div>

        <div className={`h-px ${darkMode ? 'bg-gray-700' : 'bg-gray-100'}`} />
        */}

        {/* Saved Views - Temporarily disabled */}
        {/*
        <div>
          <h4 className={`text-xs font-semibold uppercase tracking-wider mb-3 ${darkMode ? 'text-gray-400' : 'text-gray-400'}`}>Saved Views</h4>
          <div className="space-y-1">
            {savedViews.map((view) => (
              <button
                key={view.name}
                onClick={() => setActiveSavedView(view.name === activeSavedView ? null : view.name)}
                className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs transition-all cursor-pointer ${
                  activeSavedView === view.name
                    ? 'bg-brand-blue text-white font-semibold shadow-sm'
                    : darkMode ? 'text-gray-300 hover:bg-gray-800' : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                <div className="flex items-center gap-2">
                  <Eye size={11} className={activeSavedView === view.name ? 'text-white' : darkMode ? 'text-gray-500' : 'text-gray-400'} />
                  {view.name}
                </div>
                <span className={`px-1.5 py-0.5 rounded-md text-xs font-medium ${
                  activeSavedView === view.name ? 'bg-white/20 text-white' : darkMode ? 'bg-gray-700 text-gray-400' : 'bg-gray-100 text-gray-500'
                }`}>
                  {view.count}
                </span>
              </button>
            ))}
          </div>
        </div>

        <div className={`h-px ${darkMode ? 'bg-gray-700' : 'bg-gray-100'}`} />
        */}

        {/* Data Freshness */}
        <div>
          <h4 className={`text-xs font-semibold uppercase tracking-wider mb-3 ${darkMode ? 'text-gray-400' : 'text-gray-400'}`}>Data Status</h4>
          <div className={`rounded-xl p-3 ${darkMode ? 'bg-gray-800' : 'bg-gray-50'}`}>
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className={`text-xs font-medium ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>Live Data</span>
            </div>
            <p className={`text-xs ${darkMode ? 'text-gray-500' : 'text-gray-400'} mb-2`}>
              Synced {lastSync ? lastSync.toLocaleTimeString() : 'Loading...'}
            </p>
            <button
              onClick={onRefresh}
              className="flex items-center gap-1.5 text-xs text-indigo-500 font-medium hover:text-indigo-600 transition-colors"
            >
              <RefreshCw size={11} /> Refresh Now
            </button>
          </div>
        </div>
      </div>
    </aside>
  );
};

export default RightSidebar;
