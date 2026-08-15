import React from 'react';
import { LayoutDashboard, Users, Activity, Lightbulb, Bot, Zap, BarChart3, FileText, Settings } from 'lucide-react';
import { TabId } from '../types';

interface NavTabsProps {
  activeTab: TabId;
  setActiveTab: (tab: TabId) => void;
  darkMode: boolean;
}

const tabs: { id: TabId; label: string; icon: React.ReactNode }[] = [
  { id: 'overview', label: 'Overview', icon: <LayoutDashboard size={14} /> },
  { id: 'users', label: 'Users', icon: <Users size={14} /> },
  { id: 'activity', label: 'Activity', icon: <Activity size={14} /> },
  { id: 'insights', label: 'Customer Insights', icon: <Lightbulb size={14} /> },

  { id: 'performance', label: 'Performance', icon: <Zap size={14} /> },
  { id: 'analytics', label: 'Analytics', icon: <BarChart3 size={14} /> },
  { id: 'reports', label: 'Reports', icon: <FileText size={14} /> },
  { id: 'settings', label: 'Settings', icon: <Settings size={14} /> },
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
