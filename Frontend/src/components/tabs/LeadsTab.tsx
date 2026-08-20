import React, { useState } from 'react';
import { Lead, ComprehensiveDashboardStats } from '../../types';
import { UserCheck, PieChart as PieIcon, TrendingUp, Layers, Building2, MapPin, Users, CheckCircle2, XCircle, Search, Filter, Info } from 'lucide-react';
import KPICard from '../KPICard';
import {
  ChartCard,
  TimeBasedTrendChart,
  SalesOfficerLeaderboardChart,
  ProductDistributionChart,
} from '../Charts';

interface LeadsTabProps {
  leads: Lead[];
  stats: ComprehensiveDashboardStats | null;
  darkMode: boolean;
  loading: boolean;
}

const LeadsTab: React.FC<LeadsTabProps> = ({ leads, stats, darkMode, loading }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [partnerFilter, setPartnerFilter] = useState('ALL');

  const leadsData = stats?.leadsStats;
  const officerPerformance = stats?.employeesStats?.employeePerformance || [];

  const filteredLeads = leads.filter((lead) => {
    const matchesSearch =
      (lead.name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (lead.lead_code || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (lead.phone || '').includes(searchTerm);

    const matchesStatus = statusFilter === 'ALL' || lead.status === statusFilter;
    const matchesPartner = partnerFilter === 'ALL' || lead.lending_partner === partnerFilter;

    return matchesSearch && matchesStatus && matchesPartner;
  });

  const totalLeads = leadsData?.total || leads.length;
  const eligibleCount = stats?.overview.eligibleLeads || totalLeads;
  const notEligibleCount = stats?.overview.notEligibleLeads || 0;
  const conversionCount = leadsData?.conversionCount || 0;
  const assignedCount = leadsData?.assignedVsUnassigned.assigned || 0;
  const unassignedCount = leadsData?.assignedVsUnassigned.unassigned || 0;
  const conversionRatePct = totalLeads > 0 ? Math.round((conversionCount / totalLeads) * 100) : 0;

  return (
    <div className="space-y-6">
      {/* ── Top Lead KPI Row with Data Source Attribution ────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Total Leads"
          value={totalLeads}
          description="Total onboarding leads logged"
          icon="Users"
          color="blue"
          apiEndpoint="/api/v2/onboarding/leads/list/"
          darkMode={darkMode}
        />
        <KPICard
          title="Eligible / Active Leads"
          value={eligibleCount}
          description={`${notEligibleCount} marked Not Eligible`}
          icon="CheckCircle"
          color="emerald"
          apiEndpoint="/api/v2/onboarding/leads/list/"
          darkMode={darkMode}
        />
        <KPICard
          title="Lead → App Conversion"
          value={`${conversionRatePct}%`}
          description={`${conversionCount} converted to applications`}
          icon="TrendingUp"
          color="indigo"
          apiEndpoint="/api/v2/onboarding/leads/list/"
          darkMode={darkMode}
        />
        <KPICard
          title="Assigned vs Unassigned"
          value={`${assignedCount} / ${unassignedCount}`}
          description={`${assignedCount} assigned · ${unassignedCount} unassigned`}
          icon="UserCheck"
          color="amber"
          apiEndpoint="/api/v2/onboarding/leads/list/"
          darkMode={darkMode}
        />
      </div>

      {/* ── Visual Analytics Row 1: Line Trend & Leaderboard ─────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Time-Based Lead Trend Line Chart */}
        <div className="lg:col-span-2">
          <ChartCard
            title="Lead Onboarding Monthly Trend"
            subtitle="Time-based volume of incoming leads"
            apiEndpoint="/api/v2/onboarding/leads/list/"
            darkMode={darkMode}
          >
            <TimeBasedTrendChart
              data={leadsData?.monthlyTrend || []}
              darkMode={darkMode}
              metricName="Leads Sourced"
              color="#0076eb"
            />
          </ChartCard>
        </div>

        {/* Officer Leaderboard */}
        <ChartCard
          title="Sales Officer Lead Originators"
          subtitle="Top staff members handling leads"
          apiEndpoint="/user/employee & /onboarding/leads/list/"
          darkMode={darkMode}
        >
          <SalesOfficerLeaderboardChart data={officerPerformance} darkMode={darkMode} />
        </ChartCard>
      </div>

      {/* ── Visual Analytics Row 2: Status Pipeline & Category Breakups ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Lead Status Pipeline */}
        <div className={`p-5 rounded-2xl border flex flex-col justify-between ${darkMode ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-200'} shadow-sm`}>
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className={`text-sm font-bold flex items-center gap-2 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                <PieIcon size={16} className="text-brand-blue" />
                Lead Status Pipeline
              </h3>
              <div className="relative group/tooltip">
                <Info size={14} className={`${darkMode ? 'text-gray-500 group-hover/tooltip:text-gray-300' : 'text-gray-400 group-hover/tooltip:text-gray-600'} transition-colors cursor-pointer`} />
                <div className={`absolute right-0 top-full mt-1.5 hidden group-hover/tooltip:flex flex-col whitespace-nowrap z-50 px-2.5 py-1 rounded-lg text-[10px] font-mono shadow-xl border pointer-events-none ${
                  darkMode ? 'bg-gray-800 border-gray-700 text-gray-200' : 'bg-gray-900 border-gray-800 text-white'
                }`}>
                  <span className="text-[9px] text-gray-400 font-sans uppercase font-bold tracking-wider">Data Source</span>
                  <span>/api/v2/onboarding/leads/list/</span>
                </div>
              </div>
            </div>
            <div className="space-y-3">
              {(leadsData?.byStatus || []).map((item) => {
                const pct = totalLeads > 0 ? Math.round((item.count / totalLeads) * 100) : 0;
                let barColor = 'bg-brand-blue';
                if (item.status === 'NOT_ELIGIBLE') barColor = 'bg-rose-500';
                else if (item.status === 'APPLICATION_CREATED') barColor = 'bg-emerald-500';
                else if (item.status === 'AUTO_CLOSED') barColor = 'bg-gray-400';

                return (
                  <div key={item.status} className="space-y-1">
                    <div className="flex justify-between text-xs font-semibold">
                      <span className={darkMode ? 'text-gray-300' : 'text-gray-700'}>{item.status}</span>
                      <span className={darkMode ? 'text-gray-400' : 'text-gray-500'}>
                        {item.count} ({pct}%)
                      </span>
                    </div>
                    <div className={`h-2 rounded-full overflow-hidden ${darkMode ? 'bg-gray-800' : 'bg-gray-100'}`}>
                      <div className={`h-full ${barColor}`} style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Product Category Distribution */}
        <ChartCard
          title="Product Category Spread"
          subtitle="Gold loan, personal loan, home loan share"
          apiEndpoint="/api/v2/onboarding/leads/list/"
          darkMode={darkMode}
        >
          <ProductDistributionChart data={leadsData?.byProductCategory || []} darkMode={darkMode} />
        </ChartCard>

        {/* Assigned vs Unassigned Visual Widget */}
        <div className={`p-5 rounded-2xl border flex flex-col justify-between ${darkMode ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-200'} shadow-sm`}>
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className={`text-sm font-bold flex items-center gap-2 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                <UserCheck size={16} className="text-amber-500" />
                Assigned vs Unassigned Leads
              </h3>
              <div className="relative group/tooltip">
                <Info size={14} className={`${darkMode ? 'text-gray-500 group-hover/tooltip:text-gray-300' : 'text-gray-400 group-hover/tooltip:text-gray-600'} transition-colors cursor-pointer`} />
                <div className={`absolute right-0 top-full mt-1.5 hidden group-hover/tooltip:flex flex-col whitespace-nowrap z-50 px-2.5 py-1 rounded-lg text-[10px] font-mono shadow-xl border pointer-events-none ${
                  darkMode ? 'bg-gray-800 border-gray-700 text-gray-200' : 'bg-gray-900 border-gray-800 text-white'
                }`}>
                  <span className="text-[9px] text-gray-400 font-sans uppercase font-bold tracking-wider">Data Source</span>
                  <span>/api/v2/onboarding/leads/list/</span>
                </div>
              </div>
            </div>
            <div className="space-y-4">
              <div className={`p-4 rounded-xl border ${darkMode ? 'bg-emerald-900/10 border-emerald-500/30' : 'bg-emerald-50 border-emerald-200'}`}>
                <div className="flex justify-between items-center text-xs font-bold text-emerald-600 mb-1">
                  <span>Assigned to Sales Officers</span>
                  <span>{assignedCount} Leads</span>
                </div>
                <div className={`h-2.5 rounded-full overflow-hidden ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
                  <div
                    className="h-full bg-emerald-500 rounded-full"
                    style={{ width: `${totalLeads > 0 ? Math.round((assignedCount / totalLeads) * 100) : 0}%` }}
                  />
                </div>
              </div>

              <div className={`p-4 rounded-xl border ${darkMode ? 'bg-amber-900/10 border-amber-500/30' : 'bg-amber-50 border-amber-200'}`}>
                <div className="flex justify-between items-center text-xs font-bold text-amber-600 mb-1">
                  <span>Unassigned Pool</span>
                  <span>{unassignedCount} Leads</span>
                </div>
                <div className={`h-2.5 rounded-full overflow-hidden ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
                  <div
                    className="h-full bg-amber-500 rounded-full"
                    style={{ width: `${totalLeads > 0 ? Math.round((unassignedCount / totalLeads) * 100) : 0}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ── Detailed Leads Data Register Table ────────────────────────── */}
      <div className={`p-5 rounded-2xl border ${darkMode ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-200'} shadow-sm`}>
        <div className="flex items-center justify-between flex-wrap gap-4 mb-4">
          <div>
            <div className="flex items-center gap-2">
              <h3 className={`text-base font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>All Onboarding Leads Register</h3>
              <div className="relative group/tooltip">
                <Info size={14} className={`${darkMode ? 'text-gray-500 group-hover/tooltip:text-gray-300' : 'text-gray-400 group-hover/tooltip:text-gray-600'} transition-colors cursor-pointer`} />
                <div className={`absolute left-0 top-full mt-1.5 hidden group-hover/tooltip:flex flex-col whitespace-nowrap z-50 px-2.5 py-1 rounded-lg text-[10px] font-mono shadow-xl border pointer-events-none ${
                  darkMode ? 'bg-gray-800 border-gray-700 text-gray-200' : 'bg-gray-900 border-gray-800 text-white'
                }`}>
                  <span className="text-[9px] text-gray-400 font-sans uppercase font-bold tracking-wider">Data Source</span>
                  <span>/api/v2/onboarding/leads/list/</span>
                </div>
              </div>
            </div>
            <p className={`text-xs mt-0.5 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
              Showing {filteredLeads.length} of {totalLeads} lead records
            </p>
          </div>

          <div className="flex items-center gap-3 flex-wrap">
            <input
              type="text"
              placeholder="Search name, phone, lead code..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className={`px-3 py-1.5 rounded-xl border text-xs font-medium focus:outline-none ${
                darkMode ? 'bg-gray-800 border-gray-700 text-white placeholder-gray-500' : 'bg-white border-gray-300 text-gray-900'
              }`}
            />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className={`px-3 py-1.5 rounded-xl border text-xs font-medium focus:outline-none ${
                darkMode ? 'bg-gray-800 border-gray-700 text-white' : 'bg-white border-gray-300 text-gray-900'
              }`}
            >
              <option value="ALL">All Statuses</option>
              <option value="ACTIVE">ACTIVE</option>
              <option value="APPLICATION_CREATED">APPLICATION_CREATED</option>
              <option value="NOT_ELIGIBLE">NOT_ELIGIBLE</option>
              <option value="AUTO_CLOSED">AUTO_CLOSED</option>
              <option value="UNVERIFIED">UNVERIFIED</option>
            </select>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className={`border-b text-[11px] font-semibold uppercase tracking-wider ${darkMode ? 'border-gray-800 text-gray-400' : 'border-gray-200 text-gray-500'}`}>
                <th className="py-3 px-3">Lead Code / Customer</th>
                <th className="py-3 px-3">Contact</th>
                <th className="py-3 px-3">Product / Type</th>
                <th className="py-3 px-3">Lending Partner</th>
                <th className="py-3 px-3">Amount</th>
                <th className="py-3 px-3">State</th>
                <th className="py-3 px-3">Status</th>
                <th className="py-3 px-3">Prescreen</th>
                <th className="py-3 px-3">Assigned Employee</th>
              </tr>
            </thead>
            <tbody className="divide-y text-xs font-medium">
              {filteredLeads.length === 0 ? (
                <tr>
                  <td colSpan={9} className="py-8 text-center text-gray-500">
                    No leads matching filters found.
                  </td>
                </tr>
              ) : (
                filteredLeads.map((lead) => (
                  <tr key={lead.id} className={`hover:bg-brand-blue/5 transition-colors ${darkMode ? 'border-gray-800 text-gray-300' : 'border-gray-100 text-gray-800'}`}>
                    <td className="py-3 px-3">
                      <div className="font-bold text-brand-blue">{lead.lead_code || lead.id}</div>
                      <div className="text-[11px] font-medium opacity-80">{lead.name}</div>
                    </td>
                    <td className="py-3 px-3 font-mono">{lead.phone || 'N/A'}</td>
                    <td className="py-3 px-3">
                      <span className="font-semibold">{lead.product_subcategory || lead.product_category}</span>
                      <span className="block text-[10px] text-gray-500">{lead.lead_type}</span>
                    </td>
                    <td className="py-3 px-3">{lead.lending_partner}</td>
                    <td className="py-3 px-3 font-bold">₹{lead.amount ? lead.amount.toLocaleString('en-IN') : '0'}</td>
                    <td className="py-3 px-3">{lead.state}</td>
                    <td className="py-3 px-3">
                      <span className={`px-2 py-0.5 rounded-md text-[10px] font-bold ${
                        lead.status === 'APPLICATION_CREATED' ? 'bg-emerald-500/10 text-emerald-600' :
                        lead.status === 'NOT_ELIGIBLE' ? 'bg-rose-500/10 text-rose-600' :
                        lead.status === 'ACTIVE' ? 'bg-blue-500/10 text-blue-600' :
                        'bg-gray-500/10 text-gray-600'
                      }`}>
                        {lead.status}
                      </span>
                    </td>
                    <td className="py-3 px-3">
                      {lead.prescreen_status ? (
                        <span className="inline-flex items-center gap-1 text-emerald-500 text-[11px] font-bold">
                          <CheckCircle2 size={12} /> Passed
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-gray-400 text-[11px]">
                          Pending
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-3 text-[11px] text-gray-500">
                      {lead.assigned_to || lead.punched_by || 'Unassigned'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default LeadsTab;
