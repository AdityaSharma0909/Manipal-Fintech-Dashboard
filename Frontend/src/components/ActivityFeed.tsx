import React from 'react';
import { LogIn, FolderPlus, ArrowUpCircle, Bot, UserPlus, Download } from 'lucide-react';
import { ActivityEvent } from '../types';

interface ActivityFeedProps {
  events: ActivityEvent[];
  darkMode: boolean;
}

const categoryConfig: Record<string, { icon: React.ReactNode; bg: string; light: string; label: string }> = {
  auth: { icon: <LogIn size={12} />, bg: 'bg-blue-500', light: 'bg-blue-50', label: 'Auth' },
  workspace: { icon: <FolderPlus size={12} />, bg: 'bg-purple-500', light: 'bg-purple-50', label: 'Workspace' },
  upgrade: { icon: <ArrowUpCircle size={12} />, bg: 'bg-emerald-500', light: 'bg-emerald-50', label: 'Upgrade' },
  ai: { icon: <Bot size={12} />, bg: 'bg-indigo-500', light: 'bg-indigo-50', label: 'AI' },
  admin: { icon: <UserPlus size={12} />, bg: 'bg-amber-500', light: 'bg-amber-50', label: 'Admin' },
  report: { icon: <Download size={12} />, bg: 'bg-rose-500', light: 'bg-rose-50', label: 'Report' },

  // Gold Loan categories
  leads: { icon: <LogIn size={12} />, bg: 'bg-blue-500', light: 'bg-blue-50/70 dark:bg-blue-900/10', label: 'Leads' },
  underwriting: { icon: <FolderPlus size={12} />, bg: 'bg-purple-500', light: 'bg-purple-50/70 dark:bg-purple-900/10', label: 'Underwriting' },
  disbursement: { icon: <ArrowUpCircle size={12} />, bg: 'bg-emerald-500', light: 'bg-emerald-50/70 dark:bg-emerald-900/10', label: 'Disbursement' },
  repayments: { icon: <Bot size={12} />, bg: 'bg-indigo-500', light: 'bg-indigo-50/70 dark:bg-indigo-900/10', label: 'Repayments' },
  'npa / risk': { icon: <UserPlus size={12} />, bg: 'bg-rose-500', light: 'bg-rose-50/70 dark:bg-rose-900/10', label: 'Risk' },
};

const ActivityFeed: React.FC<ActivityFeedProps> = ({ events, darkMode }) => {
  return (
    <div className="space-y-1">
      {events.map((event, idx) => {
        const config = categoryConfig[event.category.toLowerCase()] || categoryConfig['leads'];
        return (
          <div
            key={event.id}
            className={`flex items-start gap-3 p-3 rounded-xl transition-all hover:scale-[1.01] cursor-pointer ${
              darkMode ? 'hover:bg-gray-700/50' : 'hover:bg-gray-50'
            }`}
            style={{ animationDelay: `${idx * 50}ms` }}
          >
            <div className="flex-shrink-0 relative">
              <div className={`w-8 h-8 rounded-xl ${config.bg} flex items-center justify-center`}>
                <span className="text-white text-xs font-bold">{event.avatar.slice(0, 2)}</span>
              </div>
              <div className={`absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 ${config.bg} rounded-full border-2 ${darkMode ? 'border-gray-800' : 'border-white'} flex items-center justify-center`}>
                <span className="text-white" style={{ fontSize: '7px' }}>{config.icon}</span>
              </div>
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-1.5 flex-wrap">
                <span className={`text-xs font-semibold ${darkMode ? 'text-gray-200' : 'text-gray-800'}`}>{event.user}</span>
                <span className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>{event.action}</span>
              </div>
              <div className="flex items-center gap-2 mt-0.5">
                <span className={`text-xs ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>{event.time}</span>
                <span className={`text-xs px-1.5 py-0.5 rounded-md font-medium ${
                  darkMode ? 'bg-gray-700 text-gray-300' : `${config.light} text-gray-600`
                }`}>{config.label}</span>
              </div>
            </div>

            <div className={`w-1.5 h-1.5 rounded-full mt-2 flex-shrink-0 ${config.bg}`} />
          </div>
        );
      })}
    </div>
  );
};

export default ActivityFeed;
