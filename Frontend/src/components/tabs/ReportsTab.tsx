import React, { useState } from 'react';
import { FileText, Download, Calendar, Clock, CheckCircle, RefreshCw, Plus } from 'lucide-react';

interface ReportsTabProps {
  darkMode: boolean;
}

const reports = [
  { name: 'Q4 2025 Executive Summary', type: 'Executive', size: '2.4 MB', created: 'Dec 31, 2025', status: 'Ready', format: 'PDF' },
  { name: 'Monthly MAU Report — December', type: 'Analytics', size: '1.8 MB', created: 'Dec 30, 2025', status: 'Ready', format: 'Excel' },
  { name: 'AI Usage Deep Dive Report', type: 'AI', size: '3.1 MB', created: 'Dec 28, 2025', status: 'Ready', format: 'PDF' },
  { name: 'Customer Health Analysis', type: 'Customer', size: '1.2 MB', created: 'Dec 25, 2025', status: 'Ready', format: 'PDF' },
  { name: 'Revenue Impact Report — Q4', type: 'Finance', size: '0.9 MB', created: 'Dec 20, 2025', status: 'Ready', format: 'Excel' },
  { name: 'Regional Performance Breakdown', type: 'Analytics', size: '1.5 MB', created: 'Dec 18, 2025', status: 'Processing', format: 'PDF' },
  { name: 'Platform Performance Report', type: 'Technical', size: '0.7 MB', created: 'Dec 15, 2025', status: 'Ready', format: 'PDF' },
];

const scheduled = [
  { name: 'Weekly MAU Digest', frequency: 'Every Monday', next: 'Jan 6, 2026', recipients: 5 },
  { name: 'Monthly Executive Report', frequency: 'Every 1st', next: 'Feb 1, 2026', recipients: 8 },
  { name: 'AI Usage Summary', frequency: 'Bi-weekly', next: 'Jan 12, 2026', recipients: 3 },
];

const typeColors: Record<string, string> = {
  Executive: 'bg-blue-100 text-brand-blue dark:bg-brand-blue/15 dark:text-blue-300',
  Analytics: 'bg-purple-100 text-purple-700',
  AI: 'bg-blue-100 text-blue-700',
  Customer: 'bg-emerald-100 text-emerald-700',
  Finance: 'bg-amber-100 text-amber-700',
  Technical: 'bg-gray-100 text-gray-600',
};

const ReportsTab: React.FC<ReportsTabProps> = ({ darkMode }) => {
  const [search, setSearch] = useState('');

  const handleNewReport = () => {
    const title = prompt('Enter new report name:');
    if (title) alert(`Report "${title}" generation queued successfully!`);
  };

  const handleDownload = (name: string, format: string) => {
    alert(`Downloading ${name}.${format.toLowerCase()}...`);
  };

  const handleEditSchedule = (name: string) => {
    alert(`Editing schedule for "${name}"`);
  };

  const filtered = reports.filter(r =>
    r.name.toLowerCase().includes(search.toLowerCase()) ||
    r.type.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Reports', value: '127', icon: <FileText size={16} className="text-brand-blue" /> },
          { label: 'Generated This Month', value: '24', icon: <CheckCircle size={16} className="text-emerald-500" /> },
          { label: 'Scheduled', value: '8', icon: <Calendar size={16} className="text-purple-500" /> },
          { label: 'Avg Generation Time', value: '45s', icon: <Clock size={16} className="text-amber-500" /> },
        ].map(s => (
          <div key={s.label} className={`rounded-2xl border p-4 ${darkMode ? 'bg-gray-800/60 border-gray-700' : 'bg-white border-gray-100'}`}>
            <div className="flex items-center gap-2 mb-2">{s.icon}<span className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>{s.label}</span></div>
            <p className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>{s.value}</p>
          </div>
        ))}
      </div>

      {/* Reports Table */}
      <div className={`rounded-2xl border overflow-hidden ${darkMode ? 'bg-gray-800/60 border-gray-700' : 'bg-white border-gray-100'}`}>
        <div className={`flex items-center justify-between px-5 py-4 border-b ${darkMode ? 'border-gray-700' : 'border-gray-100'}`}>
          <h3 className={`text-sm font-semibold ${darkMode ? 'text-white' : 'text-gray-900'}`}>Report Library</h3>
          <div className="flex items-center gap-2">
            <input
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search reports..."
              className={`px-3 py-1.5 rounded-xl border text-xs outline-none ${darkMode ? 'bg-gray-700 border-gray-600 text-gray-200 placeholder:text-gray-500' : 'bg-gray-50 border-gray-200 text-gray-700 placeholder:text-gray-400'}`}
            />
            <button
              onClick={handleNewReport}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-brand-blue hover:bg-brand-blue-hover text-white rounded-xl text-xs font-semibold shadow-md shadow-brand-blue/10 cursor-pointer"
            >
              <Plus size={12} /> New Report
            </button>
          </div>
        </div>
        <table className="w-full text-xs">
          <thead>
            <tr className={darkMode ? 'bg-gray-700/40' : 'bg-gray-50'}>
              {['Report Name', 'Type', 'Format', 'Size', 'Created', 'Status', ''].map(h => (
                <th key={h} className={`px-4 py-3 text-left font-semibold ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.map((r, i) => (
              <tr key={i} className={`border-t transition-colors group ${darkMode ? 'border-gray-700/50 hover:bg-gray-700/30' : 'border-gray-50 hover:bg-gray-50'}`}>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <FileText size={13} className="text-brand-blue flex-shrink-0" />
                    <span className={`font-medium ${darkMode ? 'text-gray-200' : 'text-gray-700'}`}>{r.name}</span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-0.5 rounded-md text-xs font-medium ${typeColors[r.type] ?? 'bg-gray-100 text-gray-600'}`}>{r.type}</span>
                </td>
                <td className={`px-4 py-3 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>{r.format}</td>
                <td className={`px-4 py-3 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>{r.size}</td>
                <td className={`px-4 py-3 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>{r.created}</td>
                <td className="px-4 py-3">
                  {r.status === 'Ready' ? (
                    <div className="flex items-center gap-1 text-emerald-500">
                      <CheckCircle size={11} />
                      <span className="text-xs font-medium">Ready</span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-1 text-amber-500">
                      <RefreshCw size={11} className="animate-spin" />
                      <span className="text-xs font-medium">Processing</span>
                    </div>
                  )}
                </td>
                <td className="px-4 py-3">
                  <button
                    onClick={() => handleDownload(r.name, r.format)}
                    className={`opacity-0 group-hover:opacity-100 flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium transition-all cursor-pointer ${darkMode ? 'bg-gray-700 text-gray-300' : 'bg-blue-50 text-brand-blue'}`}
                  >
                    <Download size={11} /> Download
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Scheduled Reports */}
      <div className={`rounded-2xl border p-5 ${darkMode ? 'bg-gray-800/60 border-gray-700' : 'bg-white border-gray-100'}`}>
        <div className="flex items-center gap-2 mb-4">
          <Calendar size={15} className="text-purple-500" />
          <h3 className={`text-sm font-semibold ${darkMode ? 'text-white' : 'text-gray-900'}`}>Scheduled Reports</h3>
        </div>
        <div className="space-y-3">
          {scheduled.map((s, i) => (
            <div key={i} className={`flex items-center gap-4 p-3 rounded-xl ${darkMode ? 'bg-gray-700/50' : 'bg-gray-50'}`}>
              <div className="w-9 h-9 rounded-xl bg-purple-100 flex items-center justify-center flex-shrink-0">
                <Calendar size={14} className="text-purple-600" />
              </div>
              <div className="flex-1">
                <p className={`text-sm font-medium ${darkMode ? 'text-gray-200' : 'text-gray-700'}`}>{s.name}</p>
                <p className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>{s.frequency} · {s.recipients} recipients</p>
              </div>
              <div className="text-right">
                <p className={`text-xs font-medium ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>Next: {s.next}</p>
                <button
                  onClick={() => handleEditSchedule(s.name)}
                  className={`text-xs text-brand-blue hover:text-brand-blue-hover transition-colors cursor-pointer`}
                >Edit</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ReportsTab;
