import React from 'react';
import { Trophy, Building2, UserCheck, TrendingUp, Medal, Star } from 'lucide-react';

interface TeamPerformanceSectionProps {
  teamStats: any;
  darkMode: boolean;
}

const rankColors = [
  'from-yellow-400 to-amber-500',    // Gold
  'from-slate-400 to-slate-500',     // Silver
  'from-amber-600 to-amber-700',     // Bronze
  'from-indigo-500 to-purple-500',
  'from-blue-500 to-cyan-500',
];

const rankIcons = [
  <Trophy size={12} className="text-yellow-400" />,
  <Medal size={12} className="text-slate-400" />,
  <Medal size={12} className="text-amber-600" />,
  <Star size={12} className="text-indigo-400" />,
  <Star size={12} className="text-blue-400" />,
];

const TeamPerformanceSection: React.FC<TeamPerformanceSectionProps> = ({ teamStats, darkMode }) => {
  const topPerformers: any[] = teamStats?.top_performers || [];
  const conversionsPerBranch: any[] = teamStats?.conversions_per_branch?.slice(0, 6) || [];
  const approvalsPerBm: any[] = teamStats?.approvals_per_bm?.slice(0, 5) || [];

  const maxLeads = topPerformers.reduce((m: number, p: any) => Math.max(m, p.lead_count || 0), 1);
  const maxApprovals = approvalsPerBm.reduce((m: number, p: any) => Math.max(m, p.approved_count || 0), 1);

  const card = `rounded-2xl border ${darkMode ? 'bg-gray-800/60 border-gray-700' : 'bg-white border-gray-100'}`;
  const subText = `text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`;
  const heading = `text-sm font-semibold ${darkMode ? 'text-white' : 'text-gray-900'}`;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className={heading}>Team Performance</h3>
        <div className="flex items-center gap-1.5">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span className={subText}>Live team data</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Top Performers */}
        <div className={`${card} p-5`}>
          <div className="flex items-center gap-2 mb-4">
            <div className="p-1.5 rounded-lg bg-yellow-50">
              <Trophy size={14} className="text-yellow-500" />
            </div>
            <div>
              <h4 className={heading}>Top Loan Officers</h4>
              <p className={subText}>By lead count</p>
            </div>
          </div>

          {topPerformers.length === 0 ? (
            <div className="py-8 text-center">
              <UserCheck size={28} className={`mx-auto mb-2 ${darkMode ? 'text-gray-600' : 'text-gray-300'}`} />
              <p className={subText}>No performer data available</p>
            </div>
          ) : (
            <div className="space-y-3">
              {topPerformers.map((p: any, i: number) => (
                <div key={p.officer_id || i} className="flex items-center gap-3">
                  <div className={`w-7 h-7 rounded-lg bg-gradient-to-br ${rankColors[i] || rankColors[4]} flex items-center justify-center flex-shrink-0`}>
                    <span className="text-white text-xs font-bold">{i + 1}</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className={`text-xs font-medium truncate ${darkMode ? 'text-gray-200' : 'text-gray-700'}`}>
                      {p.first_name || ''} {p.last_name || ''}
                    </p>
                    <div className={`h-1.5 mt-1 rounded-full ${darkMode ? 'bg-gray-700' : 'bg-gray-100'} overflow-hidden`}>
                      <div
                        className={`h-full rounded-full bg-gradient-to-r ${rankColors[i] || rankColors[4]}`}
                        style={{ width: `${((p.lead_count || 0) / maxLeads) * 100}%` }}
                      />
                    </div>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <p className={`text-xs font-bold ${darkMode ? 'text-gray-200' : 'text-gray-800'}`}>{p.lead_count}</p>
                    <p className={subText}>leads</p>
                  </div>
                  <div className="flex-shrink-0">{rankIcons[i] || rankIcons[4]}</div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Branch Conversions */}
        <div className={`${card} p-5`}>
          <div className="flex items-center gap-2 mb-4">
            <div className="p-1.5 rounded-lg bg-indigo-50">
              <Building2 size={14} className="text-indigo-500" />
            </div>
            <div>
              <h4 className={heading}>Branch Conversions</h4>
              <p className={subText}>Applications disbursed</p>
            </div>
          </div>

          {conversionsPerBranch.length === 0 ? (
            <div className="py-8 text-center">
              <Building2 size={28} className={`mx-auto mb-2 ${darkMode ? 'text-gray-600' : 'text-gray-300'}`} />
              <p className={subText}>No branch data available</p>
            </div>
          ) : (
            <div className="space-y-2.5">
              {conversionsPerBranch.map((b: any, i: number) => (
                <div key={b.branch_id || i} className={`flex items-center gap-2 p-2 rounded-xl ${darkMode ? 'bg-gray-700/40' : 'bg-gray-50'}`}>
                  <div className={`w-6 h-6 rounded-lg flex items-center justify-center flex-shrink-0 text-xs font-bold text-white bg-gradient-to-br ${rankColors[Math.min(i, 4)]}`}>
                    {i + 1}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className={`text-xs font-medium truncate ${darkMode ? 'text-gray-200' : 'text-gray-700'}`}>
                      {b.branch_name}
                    </p>
                    <p className={subText}>{b.branch_code}</p>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <p className="text-xs font-bold text-indigo-500">{b.conversion_rate_pct?.toFixed(1) ?? '0.0'}%</p>
                    <p className={subText}>{b.disbursed}/{b.total_applications}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* BM Approvals */}
        <div className={`${card} p-5`}>
          <div className="flex items-center gap-2 mb-4">
            <div className="p-1.5 rounded-lg bg-emerald-50">
              <UserCheck size={14} className="text-emerald-500" />
            </div>
            <div>
              <h4 className={heading}>Branch Manager Approvals</h4>
              <p className={subText}>Applications approved</p>
            </div>
          </div>

          {approvalsPerBm.length === 0 ? (
            <div className="py-8 text-center">
              <UserCheck size={28} className={`mx-auto mb-2 ${darkMode ? 'text-gray-600' : 'text-gray-300'}`} />
              <p className={subText}>No BM approval data available</p>
            </div>
          ) : (
            <div className="space-y-3">
              {approvalsPerBm.map((bm: any, i: number) => (
                <div key={bm.bm_id || i} className="flex items-center gap-3">
                  <div
                    className="w-8 h-8 rounded-xl text-white text-xs font-bold flex items-center justify-center flex-shrink-0 shadow-sm"
                    style={{ background: `hsl(${(i * 60 + 200) % 360}, 65%, 55%)` }}
                  >
                    {(bm.first_name || '?')[0]}{(bm.last_name || '')[0]}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className={`text-xs font-medium truncate ${darkMode ? 'text-gray-200' : 'text-gray-700'}`}>
                      {bm.first_name} {bm.last_name}
                    </p>
                    <div className={`h-1.5 mt-1 rounded-full ${darkMode ? 'bg-gray-700' : 'bg-gray-100'} overflow-hidden`}>
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-emerald-400 to-teal-500"
                        style={{ width: `${((bm.approved_count || 0) / maxApprovals) * 100}%` }}
                      />
                    </div>
                  </div>
                  <div className="flex-shrink-0 text-right">
                    <div className="flex items-center gap-1">
                      <TrendingUp size={10} className="text-emerald-500" />
                      <span className={`text-xs font-bold ${darkMode ? 'text-gray-200' : 'text-gray-800'}`}>{bm.approved_count}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TeamPerformanceSection;
