import React, { useState } from 'react';
import { Application, ComprehensiveDashboardStats } from '../../types';
import { FileText, CheckCircle2, Clock, DollarSign, Building2, MapPin, Layers, Users, Info } from 'lucide-react';
import KPICard from '../KPICard';
import {
  ChartCard,
  TimeBasedTrendChart,
  LendingPartnerPerformanceChart,
} from '../Charts';

interface ApplicationsTabProps {
  applications: Application[];
  stats: ComprehensiveDashboardStats | null;
  darkMode: boolean;
  loading: boolean;
}

const ApplicationsTab: React.FC<ApplicationsTabProps> = ({ applications, stats, darkMode, loading }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [lenderFilter, setLenderFilter] = useState('ALL');

  const appsData = stats?.applicationsStats;

  const filteredApps = applications.filter((app) => {
    const matchesSearch =
      (app.name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (app.application_id || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (app.lead_code || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (app.mobile_number || '').includes(searchTerm);

    const matchesStatus = statusFilter === 'ALL' || app.status === statusFilter;
    const matchesLender = lenderFilter === 'ALL' || app.lending_partner === lenderFilter;

    return matchesSearch && matchesStatus && matchesLender;
  });

  const totalApps = appsData?.total || applications.length;
  const approvedCount = appsData?.approvedCount || 0;
  const rejectedCount = appsData?.rejectedCount || 0;
  const inProgressCount = appsData?.inProgressCount || 0;
  const totalAmount = appsData?.totalAmount || 0;
  const totalDisbursedAmount = appsData?.totalDisbursedAmount || 0;

  return (
    <div className="space-y-6">
      {/* ── Top Application KPIs with Data Source Attribution ───────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Total Applications"
          value={totalApps}
          description="Total onboarding applications submitted"
          icon="FileText"
          color="blue"
          apiEndpoint="/api/v2/onboarding/applications/list/"
          darkMode={darkMode}
        />
        <KPICard
          title="Approved Applications"
          value={approvedCount}
          description={`${inProgressCount} in progress · ${rejectedCount} rejected`}
          icon="CheckCircle"
          color="emerald"
          apiEndpoint="/api/v2/onboarding/applications/list/"
          darkMode={darkMode}
        />
        <KPICard
          title="Application Loan Amount"
          value={`₹${(totalAmount / 100000).toFixed(1)} L`}
          description="Total requested application value"
          icon="DollarSign"
          color="indigo"
          apiEndpoint="/api/v2/onboarding/applications/list/"
          darkMode={darkMode}
        />
        <KPICard
          title="Total Disbursed Amount"
          value={`₹${(totalDisbursedAmount / 100000).toFixed(1)} L`}
          description="Total loans disbursed to borrowers"
          icon="DollarSign"
          color="emerald"
          apiEndpoint="/api/v2/onboarding/applications/list/"
          darkMode={darkMode}
        />
      </div>

      {/* ── Visual Analytics Row 1: Line Trend & Partner Chart ───────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ChartCard
            title="Application Monthly Volume Trend"
            subtitle="Time-based application submission trend"
            apiEndpoint="/api/v2/onboarding/applications/list/"
            darkMode={darkMode}
          >
            <TimeBasedTrendChart
              data={appsData?.monthlyTrend || []}
              darkMode={darkMode}
              metricName="Applications"
              color="#8b5cf6"
            />
          </ChartCard>
        </div>

        {/* Requested vs Disbursed Widget */}
        <div className={`p-5 rounded-2xl border flex flex-col justify-between ${darkMode ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-200'} shadow-sm`}>
          <div>
            <div className="flex items-center justify-between mb-1">
              <h3 className={`text-sm font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>Requested vs Disbursed</h3>
              <div className="relative group/tooltip">
                <Info size={14} className={`${darkMode ? 'text-gray-500 group-hover/tooltip:text-gray-300' : 'text-gray-400 group-hover/tooltip:text-gray-600'} transition-colors cursor-pointer`} />
                <div className={`absolute right-0 top-full mt-1.5 hidden group-hover/tooltip:flex flex-col whitespace-nowrap z-50 px-2.5 py-1 rounded-lg text-[10px] font-mono shadow-xl border pointer-events-none ${
                  darkMode ? 'bg-gray-800 border-gray-700 text-gray-200' : 'bg-gray-900 border-gray-800 text-white'
                }`}>
                  <span className="text-[9px] text-gray-400 font-sans uppercase font-bold tracking-wider">Data Source</span>
                  <span>/api/v2/onboarding/applications/list/</span>
                </div>
              </div>
            </div>
            <p className={`text-xs mb-4 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Capital allocation efficiency</p>

            <div className="space-y-4">
              <div className={`p-4 rounded-xl border ${darkMode ? 'bg-indigo-900/10 border-indigo-500/30' : 'bg-indigo-50 border-indigo-200'}`}>
                <div className="text-xs font-semibold text-gray-500">Requested Capital</div>
                <div className="text-xl font-extrabold text-indigo-600 mt-1">₹{(totalAmount / 10000000).toFixed(2)} Cr</div>
                <div className="text-[11px] text-gray-400 mt-0.5">{totalApps} Applications</div>
              </div>

              <div className={`p-4 rounded-xl border ${darkMode ? 'bg-emerald-900/10 border-emerald-500/30' : 'bg-emerald-50 border-emerald-200'}`}>
                <div className="text-xs font-semibold text-gray-500">Disbursed Capital</div>
                <div className="text-xl font-extrabold text-emerald-600 mt-1">₹{(totalDisbursedAmount / 10000000).toFixed(2)} Cr</div>
                <div className="text-[11px] text-gray-400 mt-0.5">{approvedCount} Disbursed Apps</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ── Applications Register Table ─────────────────────────────── */}
      <div className={`p-5 rounded-2xl border ${darkMode ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-200'} shadow-sm`}>
        <div className="flex items-center justify-between flex-wrap gap-4 mb-4">
          <div>
            <div className="flex items-center gap-2">
              <h3 className={`text-base font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>Applications Register</h3>
              <div className="relative group/tooltip">
                <Info size={14} className={`${darkMode ? 'text-gray-500 group-hover/tooltip:text-gray-300' : 'text-gray-400 group-hover/tooltip:text-gray-600'} transition-colors cursor-pointer`} />
                <div className={`absolute left-0 top-full mt-1.5 hidden group-hover/tooltip:flex flex-col whitespace-nowrap z-50 px-2.5 py-1 rounded-lg text-[10px] font-mono shadow-xl border pointer-events-none ${
                  darkMode ? 'bg-gray-800 border-gray-700 text-gray-200' : 'bg-gray-900 border-gray-800 text-white'
                }`}>
                  <span className="text-[9px] text-gray-400 font-sans uppercase font-bold tracking-wider">Data Source</span>
                  <span>/api/v2/onboarding/applications/list/</span>
                </div>
              </div>
            </div>
            <p className={`text-xs mt-0.5 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
              Showing {filteredApps.length} of {totalApps} application records
            </p>
          </div>

          <div className="flex items-center gap-3 flex-wrap">
            <input
              type="text"
              placeholder="Search app ID, lead code, name..."
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
              <option value="DRAFT">DRAFT</option>
              <option value="IN_PROGRESS">IN_PROGRESS</option>
              <option value="APPROVED">APPROVED</option>
              <option value="DISBURSED">DISBURSED</option>
              <option value="REJECTED">REJECTED</option>
            </select>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className={`border-b text-[11px] font-semibold uppercase tracking-wider ${darkMode ? 'border-gray-800 text-gray-400' : 'border-gray-200 text-gray-500'}`}>
                <th className="py-3 px-3">Application / Lead Code</th>
                <th className="py-3 px-3">Customer Name</th>
                <th className="py-3 px-3">Loan Type / Product</th>
                <th className="py-3 px-3">Lending Partner</th>
                <th className="py-3 px-3">Req. Amount</th>
                <th className="py-3 px-3">Disbursed Amount</th>
                <th className="py-3 px-3">Branch / State</th>
                <th className="py-3 px-3">Status</th>
                <th className="py-3 px-3">Punched By</th>
              </tr>
            </thead>
            <tbody className="divide-y text-xs font-medium">
              {filteredApps.length === 0 ? (
                <tr>
                  <td colSpan={9} className="py-8 text-center text-gray-500">
                    No applications matching filters found.
                  </td>
                </tr>
              ) : (
                filteredApps.map((app) => (
                  <tr key={app.application_id} className={`hover:bg-brand-blue/5 transition-colors ${darkMode ? 'border-gray-800 text-gray-300' : 'border-gray-100 text-gray-800'}`}>
                    <td className="py-3 px-3">
                      <div className="font-bold text-brand-blue">{app.application_id}</div>
                      <div className="text-[10px] text-gray-500">{app.lead_code || 'N/A'}</div>
                    </td>
                    <td className="py-3 px-3 font-semibold">{app.name}</td>
                    <td className="py-3 px-3">
                      <span>{app.loan_type || 'BALANCE_TRANSFER'}</span>
                      <span className="block text-[10px] text-gray-500">{app.product_subcategory}</span>
                    </td>
                    <td className="py-3 px-3">{app.lending_partner}</td>
                    <td className="py-3 px-3 font-bold">₹{app.amount ? app.amount.toLocaleString('en-IN') : '0'}</td>
                    <td className="py-3 px-3 font-bold text-emerald-600">₹{app.disbursed_amount ? app.disbursed_amount.toLocaleString('en-IN') : '0'}</td>
                    <td className="py-3 px-3">
                      <span>{app.bank_branch}</span>
                      <span className="block text-[10px] text-gray-500">{app.state}</span>
                    </td>
                    <td className="py-3 px-3">
                      <span className={`px-2 py-0.5 rounded-md text-[10px] font-bold ${
                        ['APPROVED', 'DISBURSED', 'ESIGN_COMPLETED'].includes(app.status) ? 'bg-emerald-500/10 text-emerald-600' :
                        ['REJECTED', 'REJECTED_BY_RH', 'DROPPED'].includes(app.status) ? 'bg-rose-500/10 text-rose-600' :
                        'bg-amber-500/10 text-amber-600'
                      }`}>
                        {app.status}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-[11px] text-gray-500">
                      {app.punched_by_name || app.punched_by || 'N/A'}
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

export default ApplicationsTab;
