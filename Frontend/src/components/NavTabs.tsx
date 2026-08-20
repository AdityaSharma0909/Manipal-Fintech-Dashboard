import React from 'react';
import { LayoutDashboard, Users, Activity, Lightbulb, Bot, Zap, BarChart3, FileText, Settings } from 'lucide-react';
import { TabId } from '../types';

interface NavTabsProps {
  activeTab: TabId;
  setActiveTab: (tab: TabId) => void;
  darkMode: boolean;
}

const tabs: { id: TabId; label: string; icon: React.ReactNode }[] = [
  { id: 'overview', label: 'Executive Overview', icon: <LayoutDashboard size={14} /> },
  /* Temporarily disabled non-overview tabs
  { id: 'leads', label: 'Leads Module', icon: <Users size={14} /> },
  { id: 'applications', label: 'Applications Module', icon: <FileText size={14} /> },
  { id: 'employees', label: 'Employees Module', icon: <Users size={14} /> },
  { id: 'analytics', label: 'Analytics Center', icon: <BarChart3 size={14} /> },
  { id: 'settings', label: 'Settings', icon: <Settings size={14} /> },
  */
];

const NavTabs: React.FC<NavTabsProps> = ({ activeTab, setActiveTab, darkMode }) => {
  return (
    <div className={`sticky top-[57px] z-40 ${darkMode ? 'bg-gray-900/95 border-gray-700' : 'bg-white/95 border-gray-200'} border-b backdrop-blur-xl`}>
      <div className="px-6 overflow-x-auto scrollbar-hide">
        <div className="flex items-center gap-1 py-2 min-w-max">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all whitespace-nowrap cursor-pointer ${
                activeTab === tab.id
                  ? 'bg-brand-blue text-white shadow-sm'
                  : darkMode
                  ? 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/80'
                  : 'text-gray-500 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default NavTabs;
