import React, { useState } from 'react';
import { Bell, Search, ChevronDown, Plus, Calendar, Globe, X, Moon, Sun } from 'lucide-react';

interface HeaderProps {
  darkMode: boolean;
  toggleDark: () => void;
  notifications: number;
  selectedRange: 'Today' | 'This Week' | 'This Month' | 'All Time' | 'Custom';
  setSelectedRange: (range: 'Today' | 'This Week' | 'This Month' | 'All Time' | 'Custom') => void;
  customFromDate: string;
  setCustomFromDate: (date: string) => void;
  customToDate: string;
  setCustomToDate: (date: string) => void;
  isPolling?: boolean;
  lastSync?: Date | null;
}

const Header: React.FC<HeaderProps> = ({
  darkMode, toggleDark, notifications,
  selectedRange, setSelectedRange,
  customFromDate, setCustomFromDate,
  customToDate, setCustomToDate,
  isPolling, lastSync
}) => {
  const [notifOpen, setNotifOpen] = useState(false);
  const [rangeDropdownOpen, setRangeDropdownOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [orgDropdownOpen, setOrgDropdownOpen] = useState(false);
  const [selectedOrg, setSelectedOrg] = useState('All Organizations');
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <header className={`sticky top-0 z-50 ${darkMode ? 'bg-gray-900/95 border-gray-700' : 'bg-white/95 border-gray-200'} border-b backdrop-blur-xl`}>
      <div className="flex items-center justify-between px-6 py-3 gap-4">
        {/* Logo + Title */}
        <div className="flex items-center gap-4 min-w-0">
          <div className="flex items-center gap-3">
            <img src="/Manipal-Fintech_New-Logo.png" alt="Manipal Fintech Logo" className="h-9 w-auto object-contain flex-shrink-0" />
            <div className="hidden md:block">
              <div className="flex items-center gap-2">
                <span className={`font-bold text-base tracking-tight ${darkMode ? 'text-white' : 'text-gray-900'}`}>Manipal Fintech</span>
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${darkMode ? 'bg-brand-blue/20 text-blue-300' : 'bg-blue-50 text-brand-blue'}`}>Executive</span>
              </div>
              <p className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Analytics Command Center</p>
            </div>
          </div>

          <div className="relative">
            <button
              onClick={() => setOrgDropdownOpen(!orgDropdownOpen)}
              className={`hidden lg:flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium cursor-pointer transition-all ${
                darkMode ? 'bg-gray-800 text-gray-300 hover:bg-gray-700' : 'bg-gray-50 text-gray-600 hover:bg-gray-100'
              }`}
            >
              <span>{selectedOrg}</span>
              <ChevronDown size={12} />
            </button>
            {orgDropdownOpen && (
              <div className={`absolute left-0 top-9 w-48 rounded-xl shadow-xl border z-50 py-1 ${
                darkMode ? 'bg-gray-900 border-gray-700 text-gray-200' : 'bg-white border-gray-100 text-gray-700'
              }`}>
                {['All Organizations', 'Manipal Fintech', 'Radian Finserv', 'Fincome'].map((org) => (
                  <button
                    key={org}
                    onClick={() => { setSelectedOrg(org); setOrgDropdownOpen(false); }}
                    className={`w-full text-left px-3 py-1.5 text-xs font-medium hover:bg-brand-blue hover:text-white transition-colors ${
                      selectedOrg === org ? 'text-brand-blue font-bold' : ''
                    }`}
                  >
                    {org}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Center — Search */}
        <div className="flex-1 max-w-md hidden md:block">
          <div className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-sm transition-all ${darkMode ? 'bg-gray-800/80 border border-gray-700 text-gray-400' : 'bg-gray-50 border border-gray-200 text-gray-400'} hover:border-brand-blue focus-within:border-brand-blue focus-within:ring-2 focus-within:ring-brand-blue/20`}>
            <Search size={14} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search customers, reports, metrics..."
              className={`flex-1 bg-transparent outline-none text-sm ${darkMode ? 'text-gray-200 placeholder:text-gray-500' : 'text-gray-700 placeholder:text-gray-400'}`}
            />
            <kbd className={`hidden lg:inline text-xs px-1.5 py-0.5 rounded font-mono ${darkMode ? 'bg-gray-700 text-gray-400' : 'bg-white text-gray-400 border border-gray-200'}`}>⌘K</kbd>
          </div>
        </div>

        {/* Right Controls */}
        <div className="flex items-center gap-1.5">
          {/* Sync Indicator */}
          <div className={`hidden sm:flex items-center gap-1.5 px-2 mr-2 text-[10px] font-medium tracking-wide ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
            {isPolling ? (
              <>
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                <span>Syncing live...</span>
              </>
            ) : (
              <>
                <div className="w-1.5 h-1.5 rounded-full bg-gray-300 dark:bg-gray-600" />
                <span>Live</span>
              </>
            )}
          </div>

          <div className="relative">
            <button
              onClick={() => setRangeDropdownOpen(!rangeDropdownOpen)}
              className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold border transition-all cursor-pointer ${
                darkMode
                  ? 'bg-gray-800 border-gray-700 text-gray-300 hover:bg-gray-700'
                  : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'
              }`}
            >
              <Calendar size={13} />
              <span>
                {selectedRange === 'Custom'
                  ? `${customFromDate} to ${customToDate}`
                  : selectedRange}
              </span>
              <ChevronDown size={11} className={darkMode ? 'text-gray-500' : 'text-gray-400'} />
            </button>
            {rangeDropdownOpen && (
              <div className={`absolute right-0 top-11 w-64 rounded-2xl shadow-2xl border z-50 p-4 ${
                darkMode ? 'bg-gray-900 border-gray-700' : 'bg-white border-gray-100'
              }`}>
                <p className={`text-[10px] font-bold uppercase tracking-wider mb-2 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Select Range</p>
                <div className="space-y-1">
                  {(['Today', 'This Week', 'This Month', 'All Time', 'Custom'] as const).map((opt) => (
                    <button
                      key={opt}
                      onClick={() => {
                        setSelectedRange(opt);
                        if (opt !== 'Custom') {
                          setRangeDropdownOpen(false);
                        }
                      }}
                      className={`w-full px-3 py-2 text-xs font-semibold text-left rounded-lg transition-colors cursor-pointer ${
                        selectedRange === opt
                          ? 'bg-brand-blue text-white shadow-sm'
                          : darkMode
                          ? 'text-gray-300 hover:bg-gray-800'
                          : 'text-gray-600 hover:bg-gray-50'
                      }`}
                    >
                      {opt === 'Custom' ? 'Custom Date' : opt}
                    </button>
                  ))}
                </div>
                {selectedRange === 'Custom' && (
                  <div className="space-y-3 pt-3 mt-3 border-t border-dashed" style={{ borderColor: darkMode ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)' }}>
                    <div>
                      <label className={`text-[10px] uppercase font-bold block mb-1 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Start Date</label>
                      <input
                        type="date"
                        value={customFromDate}
                        onChange={(e) => setCustomFromDate(e.target.value)}
                        className={`w-full px-2.5 py-1.5 rounded-lg border text-xs outline-none ${
                          darkMode ? 'bg-gray-800 border-gray-700 text-white' : 'bg-gray-50 border-gray-200 text-gray-750'
                        }`}
                      />
                    </div>
                    <div>
                      <label className={`text-[10px] uppercase font-bold block mb-1 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>End Date</label>
                      <input
                        type="date"
                        value={customToDate}
                        onChange={(e) => setCustomToDate(e.target.value)}
                        className={`w-full px-2.5 py-1.5 rounded-lg border text-xs outline-none ${
                          darkMode ? 'bg-gray-800 border-gray-700 text-white' : 'bg-gray-50 border-gray-200 text-gray-750'
                        }`}
                      />
                    </div>
                    <button
                      onClick={() => setRangeDropdownOpen(false)}
                      className="w-full py-1.5 bg-brand-blue hover:bg-brand-blue-hover text-white text-xs font-semibold rounded-lg shadow-sm cursor-pointer text-center"
                    >
                      Apply Range
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>

          <button
            onClick={toggleDark}
            className={`p-2 rounded-xl transition-all ${darkMode ? 'bg-gray-800 text-yellow-400 hover:bg-gray-700 border border-gray-700' : 'bg-gray-50 text-gray-600 hover:bg-gray-100 border border-gray-200'}`}
          >
            {darkMode ? <Sun size={15} /> : <Moon size={15} />}
          </button>

          <div className="relative">
            <button
              onClick={() => setNotifOpen(!notifOpen)}
              className={`relative p-2 rounded-xl transition-all ${darkMode ? 'bg-gray-800 text-gray-300 hover:bg-gray-700 border border-gray-700' : 'bg-gray-50 text-gray-600 hover:bg-gray-100 border border-gray-200'}`}
            >
              <Bell size={15} />
              {notifications > 0 && (
                <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-rose-500 text-white text-xs rounded-full flex items-center justify-center font-bold">
                  {notifications}
                </span>
              )}
            </button>
            {notifOpen && (
              <div className={`absolute right-0 top-11 w-80 rounded-2xl shadow-2xl border z-50 ${darkMode ? 'bg-gray-900 border-gray-700' : 'bg-white border-gray-100'}`}>
                <div className={`flex items-center justify-between px-4 py-3 border-b ${darkMode ? 'border-gray-700' : 'border-gray-100'}`}>
                  <span className={`font-semibold text-sm ${darkMode ? 'text-white' : 'text-gray-900'}`}>Notifications</span>
                  <button onClick={() => setNotifOpen(false)}><X size={14} className="text-gray-400" /></button>
                </div>
                {[
                  { text: 'Enterprise customer health score dropped below 70', time: '5m ago', dot: 'bg-rose-500' },
                  { text: 'Monthly report for December is ready to download', time: '1h ago', dot: 'bg-indigo-500' },
                  { text: 'AI usage milestone reached: 2M tokens generated', time: '3h ago', dot: 'bg-emerald-500' },
                ].map((n, i) => (
                  <div key={i} className={`flex gap-3 px-4 py-3 cursor-pointer transition-colors hover:${darkMode ? 'bg-gray-800' : 'bg-gray-50'}`}>
                    <div className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${n.dot}`} />
                    <div>
                      <p className={`text-xs ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>{n.text}</p>
                      <p className={`text-xs mt-0.5 ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>{n.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Logged-In User Profile Badge */}
          <div className="relative">
            <button
              onClick={() => setUserMenuOpen(!userMenuOpen)}
              className={`flex items-center gap-2 pl-1.5 pr-3 py-1 rounded-xl transition-all cursor-pointer border ${
                darkMode
                  ? 'bg-gray-800/90 border-gray-700 hover:bg-gray-700 text-white'
                  : 'bg-gray-50 border-gray-200 hover:bg-gray-100 text-gray-800'
              }`}
            >
              <div className="relative w-7 h-7 rounded-lg bg-emerald-500 flex items-center justify-center text-white font-bold text-xs shadow-sm flex-shrink-0">
                AD
                <span className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 bg-emerald-400 border-2 border-white dark:border-gray-900 rounded-full" />
              </div>
              <div className="text-left hidden sm:block leading-tight">
                <p className="text-xs font-semibold">Aditya (Admin)</p>
                <p className={`text-[10px] ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Superuser</p>
              </div>
              <ChevronDown size={12} className={darkMode ? 'text-gray-400' : 'text-gray-500'} />
            </button>

            {userMenuOpen && (
              <div className={`absolute right-0 top-11 w-64 rounded-2xl shadow-2xl border z-50 p-4 ${
                darkMode ? 'bg-gray-900 border-gray-700 text-white' : 'bg-white border-gray-100 text-gray-900'
              }`}>
                <div className="flex items-center gap-3 pb-3 border-b border-dashed mb-3" style={{ borderColor: darkMode ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)' }}>
                  <div className="w-10 h-10 rounded-xl bg-emerald-500 flex items-center justify-center text-white font-bold text-sm shadow-md">
                    AD
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-bold truncate">Aditya (Admin)</p>
                    <p className={`text-[11px] truncate ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>admin@manipalfintech.com</p>
                    <span className="inline-block mt-1 text-[9px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-500">
                      Active Superuser
                    </span>
                  </div>
                </div>

                <div className="space-y-1 text-xs">
                  <div className={`px-2.5 py-1.5 rounded-lg flex items-center justify-between ${darkMode ? 'bg-gray-800/60' : 'bg-gray-50'}`}>
                    <span className={darkMode ? 'text-gray-400' : 'text-gray-500'}>Role</span>
                    <span className="font-semibold text-brand-blue">System Administrator</span>
                  </div>
                  <div className={`px-2.5 py-1.5 rounded-lg flex items-center justify-between ${darkMode ? 'bg-gray-800/60' : 'bg-gray-50'}`}>
                    <span className={darkMode ? 'text-gray-400' : 'text-gray-500'}>Session Status</span>
                    <span className="font-semibold text-emerald-500 flex items-center gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                      Authenticated
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
